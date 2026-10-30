#!/usr/bin/env python3
"""Dev diagnosis for long-video training v1 (PLAN.md section 2). No training.

Scores frozen V6-F and v2 (3 seeds) on the 5 dev videos with the evaluation-1
scorer (dense windows every 8 frames, threshold 0.65) and reports:

1. Control metrics on dev, raw and smoothed (the numbers section 3 compares to).
2. Gate scores: quantiles and AUROC for supported exercise time versus
   downtime (non-exercise segments) and versus unknown exercise.
3. Threshold sweep, descriptive: supported time and downtime called unknown at
   gate thresholds 0.10-0.65.
4. Oracle classifier: the classifier's own argmax on supported time, gate
   ignored, as per-class recall and a confusion table.
5. Where rejected supported time falls: by class, by video, and by pose
   quality (missing-pose share, mean visibility, figure height in the image,
   side-view proxy).

Predeclared reading (written before the run):
- "threshold problem": at the lowest threshold whose downtime-called-unknown
  stays within 10 points of the 0.65 value, supported-called-unknown drops by
  at least 15 points (the section 3 bars).
- "data problem" otherwise, or when supported-vs-downtime AUROC is below 0.75.
Locked test data is never read. Nothing is tuned or promoted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import confusion_matrix, roc_auc_score

from score_long_video_test_v1 import (LABELS, STEP, SUPPORTED, THRESHOLD, WINDOW, STREAMS, build_models, features,
                                      metrics, smooth, stream, truth_at)

SWEEP = [0.10, 0.20, 0.30, 0.40, 0.50, 0.55, 0.60, 0.65]


def predict_full(pose, model, device, batch=256):
    """Like the scorer's predict, but also keeps the classifier argmax."""
    cls, gates = model
    centers = np.arange(0, len(pose), STEP)
    ex_all, g_all = [], []
    with torch.no_grad():
        for i in range(0, len(centers), batch):
            idx = [np.clip(np.arange(c - WINDOW // 2, c + WINDOW // 2), 0, len(pose) - 1) for c in centers[i:i + batch]]
            wins = [pose[j] for j in idx]
            x = torch.from_numpy(np.stack([features(w) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)
            ex_all += list(cls(x).softmax(1).argmax(1).cpu().numpy())
            g_all += list(np.mean([gates[s](torch.from_numpy(np.stack([stream(w, s) for w in wins]).transpose(0, 2, 1).astype(np.float32))
                                            .to(device)).softmax(1)[:, 1].cpu().numpy() for s in STREAMS], axis=0))
    return centers, np.array([SUPPORTED[e] for e in ex_all], dtype=object), np.array(g_all)


def pose_quality(z, centers):
    """Per-window pose covariates over the same 64-frame span."""
    det, img = z["detected"].astype(bool), z["image_landmarks"]
    vis = img[:, :, 3]
    height = np.nanmax(img[:, :, 1], 1) - np.nanmin(img[:, :, 1], 1)
    shoulder = np.abs(img[:, 5, 0] - img[:, 6, 0])
    torso = np.abs((img[:, 5, 1] + img[:, 6, 1]) / 2 - (img[:, 11, 1] + img[:, 12, 1]) / 2)
    side = shoulder / np.maximum(torso, 1e-6)
    out = []
    for c in centers:
        sl = slice(max(0, c - WINDOW // 2), min(len(det), c + WINDOW // 2))
        d = det[sl]
        out.append({"missing_share": 1 - d.mean(),
                    "visibility": float(vis[sl][d].mean()) if d.any() else 0.0,
                    "figure_height": float(np.median(height[sl][d])) if d.any() else 0.0,
                    "shoulder_torso_ratio": float(np.median(side[sl][d])) if d.any() else 0.0})
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="repo root")
    ap.add_argument("evidence_dir", type=Path, help="extracted per-video folders (each with pose.npz)")
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    data = args.root / "ml/data/long_video_train_v1"
    roles = pd.read_csv(data / "roles.csv")
    dev = sorted(roles[roles.role == "dev"].video_id)
    assert len(dev) == 5, dev
    models = build_models(args.root, device)

    rows, frames = [], {}
    for vid in dev:
        ann = pd.read_csv(data / "annotations" / f"{vid}.csv").sort_values("start_s").reset_index(drop=True)
        z = np.load(args.evidence_dir / vid / "pose.npz")
        pose = z["landmarks"].astype(np.float32)
        qual = None
        for name, model in models.items():
            centers, ex, gate = predict_full(pose, model, device)
            times = centers / 15.0
            truth, seg, guard = truth_at(times, ann)
            if qual is None:
                qual = pose_quality(z, centers)
            raw = np.where(gate >= THRESHOLD, ex, "unknown").astype(object)
            frames.setdefault(name, {})[vid] = {
                "raw": pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard, "pred": raw, "gate": gate}),
                "smoothed": pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard,
                                          "pred": smooth(raw.copy()), "gate": gate})}
            rows.append(pd.DataFrame({"model": name, "video_id": vid, "time_s": times, "truth": truth, "segment_type": seg,
                                      "classifier": ex, "gate": gate, "pred_raw": raw}).join(qual))
        print("scored", vid, flush=True)
    win = pd.concat(rows, ignore_index=True)
    win.to_csv(args.out_dir / "dev_windows.csv.gz", index=False)

    # 1. Control metrics on dev.
    table = []
    for name in frames:
        for dec in ("raw", "smoothed"):
            table.append({"model": name, "decoder": dec, "video_id": "ALL", **metrics([frames[name][v][dec] for v in dev])})
            for v in dev:
                table.append({"model": name, "decoder": dec, "video_id": v, **metrics([frames[name][v][dec]])})
    pd.DataFrame(table).to_csv(args.out_dir / "dev_metrics_by_model_video.csv", index=False)

    report = {"dev_videos": dev, "threshold": THRESHOLD, "models": {}}
    sweep_rows, oracle_rows, reject_rows = [], [], []
    for name, w in win.groupby("model"):
        sup = (w.truth != "unknown").to_numpy()
        down = (w.segment_type != "exercise").to_numpy()
        unk_ex = ((w.truth == "unknown") & (w.segment_type == "exercise")).to_numpy()
        g = w.gate.to_numpy()
        q = lambda m: [round(float(x), 3) for x in np.quantile(g[m], [0.1, 0.25, 0.5, 0.75, 0.9])]
        # 3. Threshold sweep.
        sweep = []
        for t in SWEEP:
            sweep.append({"model": name, "threshold": t, "supported_called_unknown": float((g[sup] < t).mean()),
                          "downtime_called_unknown": float((g[down] < t).mean()),
                          "unknown_exercise_called_unknown": float((g[unk_ex] < t).mean())})
        sweep_rows += sweep
        base = sweep[-1]
        ok = [s for s in sweep if s["downtime_called_unknown"] >= base["downtime_called_unknown"] - 0.10]
        best = min(ok, key=lambda s: s["threshold"])
        drop = base["supported_called_unknown"] - best["supported_called_unknown"]
        auc_down = float(roc_auc_score(np.r_[np.ones(sup.sum()), np.zeros(down.sum())], np.r_[g[sup], g[down]]))
        auc_unk = float(roc_auc_score(np.r_[np.ones(sup.sum()), np.zeros(unk_ex.sum())], np.r_[g[sup], g[unk_ex]]))
        reading = "threshold_problem" if (drop >= 0.15 and auc_down >= 0.75) else "data_problem"
        # 4. Oracle classifier.
        ws = w[sup]
        for lab in SUPPORTED:
            m = ws.truth == lab
            if m.any():
                oracle_rows.append({"model": name, "class": lab, "seconds": float(m.sum() * STEP / 15.0),
                                    "oracle_recall": float((ws.classifier[m] == lab).mean()),
                                    "gate_pass": float((ws.gate[m] >= THRESHOLD).mean()),
                                    "end_to_end_recall": float((ws.pred_raw[m] == lab).mean()),
                                    "top_confusion": ws.classifier[m & (ws.classifier != lab)].value_counts().head(2).to_dict()})
        cm = confusion_matrix(ws.truth, ws.classifier, labels=SUPPORTED)
        pd.DataFrame(cm, index=SUPPORTED, columns=SUPPORTED).to_csv(args.out_dir / f"oracle_confusion_{name}.csv")
        # 5. Where rejected supported time falls.
        rej = ws.gate < THRESHOLD
        for col in ("missing_share", "visibility", "figure_height", "shoulder_torso_ratio"):
            bins = pd.qcut(ws[col].rank(method="first"), 4, labels=["q1", "q2", "q3", "q4"])
            for b, grp in ws.groupby(bins, observed=True):
                reject_rows.append({"model": name, "by": col, "bin": b, "range": f"{grp[col].min():.3f}-{grp[col].max():.3f}",
                                    "seconds": float(len(grp) * STEP / 15.0), "rejected_share": float((grp.gate < THRESHOLD).mean())})
        for v, grp in ws.groupby("video_id"):
            reject_rows.append({"model": name, "by": "video", "bin": v, "range": "", "seconds": float(len(grp) * STEP / 15.0),
                                "rejected_share": float((grp.gate < THRESHOLD).mean())})
        report["models"][name] = {"gate_quantiles_supported": q(sup), "gate_quantiles_downtime": q(down),
                                  "gate_quantiles_unknown_exercise": q(unk_ex), "auroc_supported_vs_downtime": auc_down,
                                  "auroc_supported_vs_unknown_exercise": auc_unk,
                                  "supported_called_unknown_at_065": base["supported_called_unknown"],
                                  "downtime_called_unknown_at_065": base["downtime_called_unknown"],
                                  "lowest_threshold_within_10pt_downtime": best["threshold"],
                                  "supported_called_unknown_drop_there": drop, "rejected_supported_share": float(rej.mean()),
                                  "oracle_supported_accuracy": float((ws.classifier == ws.truth).mean()),
                                  "reading": reading}
    pd.DataFrame(sweep_rows).to_csv(args.out_dir / "threshold_sweep.csv", index=False)
    pd.DataFrame(oracle_rows).to_csv(args.out_dir / "oracle_by_class.csv", index=False)
    pd.DataFrame(reject_rows).to_csv(args.out_dir / "rejection_breakdown.csv", index=False)
    (args.out_dir / "diagnosis.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
