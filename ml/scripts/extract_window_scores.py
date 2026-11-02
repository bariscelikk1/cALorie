#!/usr/bin/env python3
"""Save raw per-window model outputs so decoders and thresholds can be tested without re-running the models.

For every 8-frame step of a video this stores: the 14 classifier logits (before softmax), and the 2 logits of each of the
three gate streams (joint, bone, velocity). The existing scorer keeps none of these. This script does not change it.

Check mode (--check): rebuilds the labels from the saved scores with the same rule as predict() and compares them with a
saved smoothed timeline, so we know the new outputs match the old ones exactly before anything else is built on them.

Usage: extract_window_scores.py REPO_ROOT OUT_DIR --videos ID [ID ...] --zips nb47_seed42.zip nb47_seed137.zip nb47_seed2026.zip [--device mps] [--check TIMELINE_DIR]
"""

from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from score_long_video_test_v1 import SUPPORTED, STEP, FPS, STREAMS, THRESHOLD, WINDOW, features, smooth, stream
from score_nb47_round2_v1 import nb47_models


def window_scores(pose, model, device, batch=256):
    """Same windows and features as score_long_video_test_v1.predict, but returns logits instead of labels."""
    cls, gates = model
    centers = np.arange(0, len(pose), STEP)
    cls_logits, gate_logits = [], {s: [] for s in STREAMS}
    with torch.no_grad():
        for i in range(0, len(centers), batch):
            idx = [np.clip(np.arange(c - WINDOW // 2, c + WINDOW // 2), 0, len(pose) - 1) for c in centers[i:i + batch]]
            wins = [pose[j] for j in idx]
            x = torch.from_numpy(np.stack([features(w) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)
            cls_logits.append(cls(x).cpu().numpy())
            for s in STREAMS:
                xs = torch.from_numpy(np.stack([stream(w, s) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)
                gate_logits[s].append(gates[s](xs).cpu().numpy())
    return centers / FPS, np.concatenate(cls_logits), {s: np.concatenate(v) for s, v in gate_logits.items()}


def softmax(a):
    e = np.exp(a - a.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)


def labels_from_scores(cls_logits, gate_logits):
    """Rebuild the old decision rule: mean of the three gate streams' P(exercise), then the 0.65 cutoff."""
    gate = np.mean([softmax(gate_logits[s])[:, 1] for s in STREAMS], axis=0)
    ex = softmax(cls_logits).argmax(1)
    return np.array([SUPPORTED[e] if g >= THRESHOLD else "unknown" for e, g in zip(ex, gate)], dtype=object), gate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path); ap.add_argument("out_dir", type=Path)
    ap.add_argument("--videos", nargs="+", required=True)
    ap.add_argument("--zips", type=Path, nargs=3, required=True, help="the three nb47 (final v2) seed ZIPs, seeds 42 137 2026")
    ap.add_argument("--evidence-dir", default="ml/artifacts/long_video_round3_v1")
    ap.add_argument("--zip-prefix", default="long_video_round3_v1_")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--check", type=Path, help="folder with timeline_v2_seed<N>_smoothed.csv.gz to compare against")
    args = ap.parse_args()
    device = torch.device(args.device)
    models, _ = nb47_models(args.zips, device)  # final v2 = Notebook 47
    args.out_dir.mkdir(parents=True, exist_ok=True)
    mismatches = 0
    for vid in args.videos:
        with zipfile.ZipFile(args.root / args.evidence_dir / f"{args.zip_prefix}{vid}.zip") as z:
            pose = np.load(io.BytesIO(z.read(f"{vid}/pose.npz")))["landmarks"].astype(np.float32)
        for name, model in models.items():
            times, cl, gl = window_scores(pose, model, device)
            np.savez_compressed(args.out_dir / f"{name}_{vid}.npz", time_s=times, cls_logits=cl,
                                **{f"gate_{s}": v for s, v in gl.items()})
            if args.check is not None:
                raw, _ = labels_from_scores(cl, gl)
                old = pd.read_csv(args.check / f"timeline_{name.replace('nb47', 'v2')}_smoothed.csv.gz")
                old = old[old.video_id == vid].sort_values("time_s")
                same = (smooth(raw.copy()) == old.pred.to_numpy(dtype=object)) if len(old) == len(raw) else np.array([False])
                bad = int((~same).sum())
                mismatches += bad
                print(f"check {name} {vid}: {len(raw)} windows, {bad} differ", flush=True)
            else:
                print("saved", name, vid, flush=True)
    if args.check is not None:
        print("REPRODUCTION", "EXACT" if mismatches == 0 else f"FAILED ({mismatches} windows differ)")


if __name__ == "__main__":
    main()
