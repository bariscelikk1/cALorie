#!/usr/bin/env python3
"""Evaluation 2 on the locked long-video test v1: the frozen final model (Notebook 46).

Run once, predeclared 2026-10-28 before scoring. Same scorer, decoders, and
metrics as evaluation 1 (`score_long_video_test_v1.py`). The final model is
Notebook 46 (Notebook 45 classifiers + gate-balanced gates, 3 seeds). It is
frozen and labeled as NOT passing the 15-point dev gate bar; this score is
for the final report only. Nothing is tuned, chosen, or relabeled from it.

Primary: smoothed pooled 15-label Macro F1, Notebook 46 seed median minus
V6-F, with a video-level bootstrap (2,000 draws). Also reported against the
v2 seed median. Parity: V6-F and v2 must reproduce evaluation 1 within 0.005.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from score_long_video_test_v1 import BOOTSTRAP, STREAMS, SUPPORTED, SmallTCN, build_models, load, metrics, predict, smooth, truth_at

NB46_ZIP = "ml/artifacts/long_video_gate_balance_v1/calorie_long_video_gate_balance_report.zip"
SEEDS = (42, 137, 2026)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def nb46_models(root: Path, device):
    models = {}
    with zipfile.ZipFile(root / NB46_ZIP) as z:
        for seed in SEEDS:
            ck = load(z.read(f"models/seed_{seed}_classifier_from_nb45.pt"), device)
            assert list(ck["supported_classes"]) == SUPPORTED
            cls = SmallTCN(100, 14).to(device); cls.load_state_dict(ck["exercise_state_dict"]); cls.eval()
            gates = {}
            for s, d in STREAMS.items():
                g = SmallTCN(d, 2).to(device); g.load_state_dict(load(z.read(f"models/seed_{seed}_{s}_gate.pt"), device)["state_dict"]); gates[s] = g.eval()
            models[f"final_nb46_seed{seed}"] = (cls, gates)
    return models


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="repo root")
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    data, evidence = args.root / "ml/data/long_video_test_v1", args.root / "ml/artifacts/long_video_test_v1"
    lock = json.loads((data / "LOCK.json").read_text())
    for name, expected in lock["annotations"].items():
        assert sha256((data / "annotations" / name).read_bytes()) == expected, f"Lock broken: {name}"
    for name, expected in lock["evidence"].items():
        assert sha256((evidence / name).read_bytes()) == expected, f"Lock broken: {name}"
    print("Lock verified:", len(lock["annotations"]), "annotations,", len(lock["evidence"]), "evidence ZIPs")

    models = {**build_models(args.root, device), **nb46_models(args.root, device)}
    per = {name: {"raw": {}, "smoothed": {}} for name in models}
    for name in sorted(lock["annotations"]):
        vid = name[:-4]
        ann = pd.read_csv(data / "annotations" / name).sort_values("start_s").reset_index(drop=True)
        with zipfile.ZipFile(evidence / f"long_video_test_v1_{vid}.zip") as z:
            listed = dict(line.split("  ", 1)[::-1] for line in z.read(f"{vid}/SHA256SUMS.txt").decode().splitlines())
            payload = z.read(f"{vid}/pose.npz")
        assert sha256(payload) == listed["pose.npz"], vid
        pose = np.load(io.BytesIO(payload))["landmarks"].astype(np.float32)
        for mname, model in models.items():
            times, raw, gates = predict(pose, model, device)
            truth, seg, guard = truth_at(times, ann)
            for dec, pred in (("raw", raw), ("smoothed", smooth(raw.copy()))):
                per[mname][dec][vid] = pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg,
                                                     "guard": guard, "pred": pred, "gate": gates})
        print("scored", vid, flush=True)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    videos = sorted(per["v6f"]["raw"])
    rows = []
    for name in per:
        for dec in ("raw", "smoothed"):
            rows.append({"model": name, "decoder": dec, "video_id": "ALL", **metrics([per[name][dec][v] for v in videos])})
            for v in videos:
                rows.append({"model": name, "decoder": dec, "video_id": v, **metrics([per[name][dec][v]])})
    table = pd.DataFrame(rows)
    table.to_csv(args.out_dir / "metrics_by_model_video.csv", index=False)
    pooled = table[table.video_id == "ALL"]
    groups = {"v6f": ["v6f"], "v2_seed_median": [m for m in per if m.startswith("v2_")],
              "final_nb46_seed_median": [m for m in per if m.startswith("final_nb46")]}
    summary = pd.concat([pooled[pooled.model.isin(ms)].groupby("decoder").median(numeric_only=True).assign(model=g)
                         for g, ms in groups.items()]).reset_index()
    summary.to_csv(args.out_dir / "summary.csv", index=False)

    eval1 = pd.read_csv(evidence / "eval1/summary.csv")
    for model in ("v6f", "v2_seed_median"):
        for dec in ("raw", "smoothed"):
            a = summary[(summary.model == model) & (summary.decoder == dec)].iloc[0]
            b = eval1[(eval1.model == model) & (eval1.decoder == dec)].iloc[0]
            for k in ("macro_f1", "supported_called_unknown", "downtime_called_unknown"):
                assert abs(a[k] - b[k]) < 0.005, (model, dec, k, a[k], b[k])
    print("Parity with evaluation 1 passed.")

    def f1(names, sample):
        return np.median([metrics([per[m]["smoothed"][v] for v in sample])["macro_f1"] for m in names])

    rng = np.random.default_rng(20261028)
    d_v6f, d_v2 = [], []
    for _ in range(BOOTSTRAP):
        sample = rng.choice(videos, size=len(videos), replace=True)
        final = f1(groups["final_nb46_seed_median"], sample)
        d_v6f.append(final - f1(["v6f"], sample)); d_v2.append(final - f1(groups["v2_seed_median"], sample))
    sm = summary[summary.decoder == "smoothed"].set_index("model")
    ci = lambda d: [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]
    verdict = {"evaluation_number": 2, "final_model": "Notebook 46 (frozen; did not pass the 15-point dev gate bar)",
               "primary_metric": "smoothed pooled 15-label Macro F1",
               "final_minus_v6f": float(sm.loc["final_nb46_seed_median", "macro_f1"] - sm.loc["v6f", "macro_f1"]),
               "final_minus_v6f_bootstrap_95ci": ci(d_v6f),
               "final_minus_v2": float(sm.loc["final_nb46_seed_median", "macro_f1"] - sm.loc["v2_seed_median", "macro_f1"]),
               "final_minus_v2_bootstrap_95ci": ci(d_v2), "videos": videos, "promotion": False}
    verdict["answer_vs_v6f"] = "final_better" if verdict["final_minus_v6f_bootstrap_95ci"][0] > 0 else "not_shown_better"
    (args.out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    for g, ms in groups.items():
        for m in ms:
            pd.concat(per[m]["smoothed"].values()).to_csv(args.out_dir / f"timeline_{m}_smoothed.csv.gz", index=False)
    print(json.dumps(verdict, indent=2))
    print(summary[["model", "decoder", "macro_f1", "accuracy", "block_f1", "switches_per_min_pred",
                   "downtime_called_unknown", "supported_called_unknown"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
