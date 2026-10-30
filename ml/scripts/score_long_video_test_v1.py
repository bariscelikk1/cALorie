#!/usr/bin/env python3
"""Full-session scorer for long-video test v1 (PLAN.md, "Scoring details").

Dense 64-frame windows every 8 frames, raw and fixed smoothed decoders, pooled
metrics over all videos, and a video-level bootstrap of v2 minus V6-F.
"""

from __future__ import annotations

import argparse
import collections
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import f1_score
from torch import nn

WINDOW, STEP, FPS, THRESHOLD = 64, 8, 15.0, 0.65
VOTE, MIN_RUN_S, GUARD_S, BOOTSTRAP = 9, 4.0, 2.0, 2000
SUPPORTED = ["bench_press", "bicep_curl", "deadlift", "dumbbell_row", "jumping_jack", "lat_pulldown", "lateral_raise",
             "lunge", "pull_up", "push_up", "shoulder_press", "sit_up", "squat", "tricep_extension"]
LABELS = SUPPORTED + ["unknown"]
STREAMS = {"joint": 34, "bone": 24, "velocity": 34}
BONE_EDGES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]
ANGLE_TRIPLETS = [(5, 7, 9), (6, 8, 10), (7, 5, 11), (8, 6, 12), (5, 11, 13), (6, 12, 14), (11, 13, 15), (12, 14, 16)]


class TemporalBlock(nn.Module):
    def __init__(self, cin, cout, dilation, dropout=0.2):
        super().__init__()
        self.net = nn.Sequential(nn.Conv1d(cin, cout, 3, padding=dilation, dilation=dilation), nn.BatchNorm1d(cout), nn.ReLU(), nn.Dropout(dropout),
                                 nn.Conv1d(cout, cout, 3, padding=dilation, dilation=dilation), nn.BatchNorm1d(cout), nn.ReLU(), nn.Dropout(dropout))
        self.residual = nn.Conv1d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x):
        return torch.relu(self.net(x) + self.residual(x))


class SmallTCN(nn.Module):
    def __init__(self, features, classes):
        super().__init__()
        blocks, current = [], features
        for level, out in enumerate([64, 96, 128, 128]):
            blocks.append(TemporalBlock(current, out, 2 ** level))
            current = out
        self.features, self.classifier = nn.Sequential(*blocks), nn.Linear(current, classes)

    def forward(self, x):
        return self.classifier(self.features(x).mean(-1))


def features(w):
    xy = w[:, :, :2]
    vel = np.zeros_like(xy); vel[1:] = xy[1:] - xy[:-1]
    bones = np.stack([xy[:, c] - xy[:, p] for p, c in BONE_EDGES], 1)
    angles = []
    for a, b, c in ANGLE_TRIPLETS:
        u, v = xy[:, a] - xy[:, b], xy[:, c] - xy[:, b]
        cos = (u * v).sum(1) / np.maximum(np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1), 1e-6)
        angles.append(np.arccos(np.clip(cos, -1, 1)) / np.pi)
    return np.concatenate([xy.reshape(WINDOW, -1), vel.reshape(WINDOW, -1), bones.reshape(WINDOW, -1), np.stack(angles, 1)], 1)


def stream(w, name):
    xy = w[:, :, :2]
    if name == "joint":
        return xy.reshape(WINDOW, -1)
    if name == "velocity":
        vel = np.zeros_like(xy); vel[1:] = xy[1:] - xy[:-1]
        return vel.reshape(WINDOW, -1)
    return np.stack([xy[:, c] - xy[:, p] for p, c in BONE_EDGES], 1).reshape(WINDOW, -1)


def load(blob, device):
    return torch.load(io.BytesIO(blob) if isinstance(blob, bytes) else blob, map_location=device, weights_only=False)


def build_models(root: Path, device):
    models = {}
    base = root / "ml/artifacts/v6f_multistream_gate/model"
    ck = load(base / "frozen_temporal_classifier_checkpoint.pt", device)
    assert list(ck["supported_classes"]) == SUPPORTED
    cls = SmallTCN(100, 14).to(device); cls.load_state_dict(ck["exercise_state_dict"])
    gates = {}
    for s, d in STREAMS.items():
        g = SmallTCN(d, 2).to(device); g.load_state_dict(load(base / f"{s}_gate.pt", device)["state_dict"]); gates[s] = g
    models["v6f"] = (cls, gates)
    with zipfile.ZipFile(root / "ml/artifacts/repcount_training_v2_stage_a/calorie_repcount_training_v2_stage_a_report.zip") as z:
        for seed in (42, 137, 2026):
            ck = load(z.read(f"models/seed_{seed}_classifier.pt"), device)
            cls = SmallTCN(100, 14).to(device); cls.load_state_dict(ck["exercise_state_dict"])
            gates = {}
            for s, d in STREAMS.items():
                g = SmallTCN(d, 2).to(device); g.load_state_dict(load(z.read(f"models/seed_{seed}_{s}_gate.pt"), device)["state_dict"]); gates[s] = g
            models[f"v2_seed{seed}"] = (cls, gates)
    for cls, gates in models.values():
        cls.eval(); [g.eval() for g in gates.values()]
    return models


def predict(pose, model, device, batch=256):
    cls, gates = model
    centers = np.arange(0, len(pose), STEP)
    labels, gate_scores = [], []
    with torch.no_grad():
        for i in range(0, len(centers), batch):
            idx = [np.clip(np.arange(c - WINDOW // 2, c + WINDOW // 2), 0, len(pose) - 1) for c in centers[i:i + batch]]
            wins = [pose[j] for j in idx]
            x = torch.from_numpy(np.stack([features(w) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)
            ex = cls(x).softmax(1).argmax(1).cpu().numpy()
            g = np.mean([gates[s](torch.from_numpy(np.stack([stream(w, s) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)).softmax(1)[:, 1].cpu().numpy()
                         for s in STREAMS], axis=0)
            labels += [SUPPORTED[e] if gs >= THRESHOLD else "unknown" for e, gs in zip(ex, g)]
            gate_scores += list(g)
    return centers / FPS, np.array(labels, dtype=object), np.array(gate_scores)


def smooth(raw):
    half = VOTE // 2
    voted = []
    for i in range(len(raw)):
        counts = collections.Counter(raw[max(0, i - half):i + half + 1])
        top = max(counts.values())
        voted.append(raw[i] if counts[raw[i]] == top else sorted(k for k, v in counts.items() if v == top)[0])
    seq = np.array(voted, dtype=object)
    min_n = MIN_RUN_S * FPS / STEP
    while True:
        runs = [(s, e) for s, e in run_bounds(seq)]
        short = [(e - s, s, e) for s, e in runs if e - s < min_n and len(runs) > 1]
        if not short:
            return seq
        _, s, e = min(short)
        left = seq[s - 1] if s > 0 else None
        right = seq[e] if e < len(seq) else None
        left_len = next((b - a for a, b in runs if b == s), 0)
        right_len = next((b - a for a, b in runs if a == e), 0)
        seq[s:e] = left if (left is not None and (right is None or left_len >= right_len)) else right


def run_bounds(seq):
    out, start = [], 0
    for i in range(1, len(seq) + 1):
        if i == len(seq) or seq[i] != seq[start]:
            out.append((start, i)); start = i
    return out


def truth_at(times, ann):
    ends = ann.end_s.to_numpy(float)
    idx = np.minimum(np.searchsorted(ends, times, side="right"), len(ann) - 1)
    rows = ann.iloc[idx]
    starts, stops = rows.start_s.to_numpy(float), rows.end_s.to_numpy(float)
    label = rows.current_tcn_label.to_numpy(object)
    # Guard only boundaries where the canonical label changes.
    change = [0.0] + [float(ann.start_s.iloc[k]) for k in range(1, len(ann)) if ann.current_tcn_label.iloc[k] != ann.current_tcn_label.iloc[k - 1]]
    dist = np.min(np.abs(times[:, None] - np.array(change[1:] or [-1e9])[None, :]), axis=1)
    return label, rows.segment_type.to_numpy(object), dist >= GUARD_S


def blocks(seq):
    return [(seq[s], s, e) for s, e in run_bounds(seq) if seq[s] != "unknown"]


def block_f1(truth, pred):
    t, p = blocks(truth), blocks(pred)
    used, hits = set(), 0
    for lab, s, e in t:
        best, bi = 0.0, None
        for k, (pl, ps, pe) in enumerate(p):
            if pl != lab or k in used:
                continue
            inter = max(0, min(e, pe) - max(s, ps)); union = max(e, pe) - min(s, ps)
            if union and inter / union > best:
                best, bi = inter / union, k
        if best >= 0.5:
            used.add(bi); hits += 1
    prec, rec = hits / max(len(p), 1), hits / max(len(t), 1)
    return 0.0 if hits == 0 else 2 * prec * rec / (prec + rec)


def metrics(frames):
    d = pd.concat(frames, ignore_index=True)
    t, p, g = d.truth.to_numpy(object), d.pred.to_numpy(object), d.guard.to_numpy(bool)
    sup = t != "unknown"
    downtime = d.segment_type.to_numpy(object) != "exercise"
    minutes = len(d) * STEP / FPS / 60
    out = {"macro_f1": f1_score(t, p, labels=LABELS, average="macro", zero_division=0),
           "accuracy": float((t == p).mean()),
           "macro_f1_guarded": f1_score(t[g], p[g], labels=LABELS, average="macro", zero_division=0),
           "accuracy_guarded": float((t[g] == p[g]).mean()),
           "block_f1": float(np.mean([block_f1(f.truth.to_numpy(object), f.pred.to_numpy(object)) for f in frames])),
           "switches_per_min_pred": sum(len(run_bounds(f.pred.to_numpy(object))) - 1 for f in frames) / minutes,
           "switches_per_min_truth": sum(len(run_bounds(f.truth.to_numpy(object))) - 1 for f in frames) / minutes,
           "downtime_called_unknown": float((p[downtime] == "unknown").mean()),
           "supported_called_unknown": float((p[sup] == "unknown").mean())}
    for lab in LABELS:
        m = t == lab
        out[f"recall__{lab}"] = float((p[m] == lab).mean()) if m.any() else float("nan")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="repo root")
    ap.add_argument("evidence_dir", type=Path, help="extracted per-video folders (each with pose.npz)")
    ap.add_argument("annotation_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    models = build_models(args.root, device)
    per = collections.defaultdict(dict)  # model -> decoder -> {video: frame}
    window_rows = []
    for ann_path in sorted(args.annotation_dir.glob("*.csv")):
        vid = ann_path.stem
        ann = pd.read_csv(ann_path).sort_values("start_s").reset_index(drop=True)
        pose = np.load(args.evidence_dir / vid / "pose.npz")["landmarks"].astype(np.float32)
        for name, model in models.items():
            times, raw, gates = predict(pose, model, device)
            truth, seg, guard = truth_at(times, ann)
            for dec, pred in (("raw", raw), ("smoothed", smooth(raw.copy()))):
                per[name].setdefault(dec, {})[vid] = pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg,
                                                                   "guard": guard, "pred": pred, "gate": gates})
        print("scored", vid, flush=True)

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
    v2 = pooled[pooled.model.str.startswith("v2")].groupby("decoder").median(numeric_only=True).assign(model="v2_seed_median")
    summary = pd.concat([pooled[pooled.model == "v6f"].set_index("decoder"), v2]).reset_index()
    summary.to_csv(args.out_dir / "summary.csv", index=False)

    rng = np.random.default_rng(20261027)
    seeds = [m for m in per if m.startswith("v2")]
    deltas = []
    for _ in range(BOOTSTRAP):
        sample = rng.choice(videos, size=len(videos), replace=True)
        base = metrics([per["v6f"]["smoothed"][v] for v in sample])["macro_f1"]
        new = np.median([metrics([per[s]["smoothed"][v] for v in sample])["macro_f1"] for s in seeds])
        deltas.append(new - base)
    point = float(v2.loc["smoothed", "macro_f1"] - pooled[(pooled.model == "v6f") & (pooled.decoder == "smoothed")].macro_f1.iloc[0])
    ci = [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))]
    verdict = {"primary_metric": "smoothed pooled 15-label Macro F1", "v2_minus_v6f": point, "bootstrap_95ci": ci,
               "answer": "v2_better" if ci[0] > 0 else "not_shown_better", "videos": videos,
               "promotion": False, "evaluation_number": 1}
    (args.out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    for name in per:
        pd.concat(per[name]["smoothed"].values()).to_csv(args.out_dir / f"timeline_{name}_smoothed.csv.gz", index=False)
    print(json.dumps(verdict, indent=2))
    print(summary[["model", "decoder", "macro_f1", "accuracy", "macro_f1_guarded", "block_f1", "switches_per_min_pred",
                   "switches_per_min_truth", "downtime_called_unknown", "supported_called_unknown"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
