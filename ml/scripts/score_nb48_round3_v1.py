#!/usr/bin/env python3
"""Score Notebook 48 (three per-seed ZIPs) once on the locked round-3 test video, against final model v2 (Notebook 47).

Predeclared in ml/data/long_video_round3_v1/PLAN.md. Two test videos: the result is informational only.
Criteria (all must hold to call Notebook 48 better than v2):
  1. smoothed Macro F1 gain >= 2 pp (seed medians)
  2. mean time recall over the weak exercises present in the test videos not worse than 5 pp, and dumbbell row recall not worse than v2
  3. supported exercise time called unknown no more than 3 pp worse
  4. rest/transition time called unknown no more than 5 pp worse
Usage: score_nb48_round3_v1.py REPO_ROOT OUT_DIR nb47_seed42.zip nb47_seed137.zip nb47_seed2026.zip nb48_seed42.zip nb48_seed137.zip nb48_seed2026.zip [--device mps]
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

from score_long_video_test_v1 import STREAMS, SUPPORTED, SmallTCN, load, metrics, predict, smooth, truth_at

WEAK = ["tricep_extension", "lateral_raise", "bicep_curl", "dumbbell_row", "shoulder_press", "bench_press"]
SEEDS = (42, 137, 2026)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def models_from(zips, prefix, flag, device):
    models, internal = {}, []
    for seed, path in zip(SEEDS, zips):
        with zipfile.ZipFile(path) as z:
            meta = json.loads(z.read("run_metadata.json"))
            assert meta["seed"] == seed and not meta["dry_run"] and not meta[flag], path
            listed = dict(line.split("  ", 1)[::-1] for line in z.read("SHA256SUMS.txt").decode().splitlines())
            for name, expected in listed.items():
                assert sha256(z.read(name)) == expected, f"Checksum failed inside {path.name}: {name}"
            ck = load(z.read(f"models/seed_{seed}_classifier.pt"), device)
            assert list(ck["supported_classes"]) == SUPPORTED
            cls = SmallTCN(100, 14).to(device); cls.load_state_dict(ck["exercise_state_dict"]); cls.eval()
            gates = {}
            for s, d in STREAMS.items():
                g = SmallTCN(d, 2).to(device)
                g.load_state_dict(load(z.read(f"models/seed_{seed}_{s}_gate.pt"), device)["state_dict"]); gates[s] = g.eval()
            models[f"{prefix}_seed{seed}"] = (cls, gates)
            internal.append(pd.read_csv(io.BytesIO(z.read("internal_test_metrics.csv"))))
    return models, pd.concat(internal, ignore_index=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path); ap.add_argument("out_dir", type=Path)
    ap.add_argument("zips", type=Path, nargs=6); ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    data, evidence = args.root / "ml/data/long_video_round3_v1", args.root / "ml/artifacts/long_video_round3_v1"
    lock = json.loads((data / "LOCK.json").read_text())
    for name, expected in lock["annotations"].items():
        assert sha256((data / "annotations" / name).read_bytes()) == expected, f"Lock broken: {name}"
    for vid, expected in lock["evidence"].items():
        assert sha256((evidence / f"long_video_round3_v1_{vid}.zip").read_bytes()) == expected, f"Lock broken: {vid}"
    test = sorted(lock["evidence"])
    print("Lock verified:", test)

    control, internal_c = models_from(args.zips[:3], "v2", "round2_test_videos_read", device)
    treat, internal_t = models_from(args.zips[3:], "nb48", "round3_test_videos_read", device)
    models = {**control, **treat}
    per = {name: {} for name in models}
    for vid in test:
        ann = pd.read_csv(data / "annotations" / f"{vid}.csv").sort_values("start_s").reset_index(drop=True)
        with zipfile.ZipFile(evidence / f"long_video_round3_v1_{vid}.zip") as z:
            listed = dict(line.split("  ", 1)[::-1] for line in z.read(f"{vid}/SHA256SUMS.txt").decode().splitlines())
            payload = z.read(f"{vid}/pose.npz")
        assert sha256(payload) == listed["pose.npz"], vid
        pose = np.load(io.BytesIO(payload))["landmarks"].astype(np.float32)
        for name, model in models.items():
            times, raw, gates = predict(pose, model, device)
            truth, seg, guard = truth_at(times, ann)
            per[name][vid] = pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard,
                                           "pred": smooth(raw.copy()), "gate": gates})
        print("scored", vid, flush=True)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = [{"model": name, "video_id": "ALL", **metrics([per[name][v] for v in test])} for name in per]
    table = pd.DataFrame(rows); table.to_csv(args.out_dir / "metrics_by_model.csv", index=False)
    pooled = table.set_index("model")
    arms = {"v2_seed_median": [m for m in per if m.startswith("v2")], "nb48_seed_median": [m for m in per if m.startswith("nb48")]}
    summary = pd.DataFrame({a: pooled.loc[ms].median(numeric_only=True) for a, ms in arms.items()}).T
    summary.to_csv(args.out_dir / "summary.csv")
    present = [w for w in WEAK if not pooled[f"recall__{w}"].isna().any()]
    weak = {a: float(np.mean([summary.loc[a, f"recall__{w}"] for w in present])) for a in arms}
    s2, s48 = summary.loc["v2_seed_median"], summary.loc["nb48_seed_median"]
    criteria = {
        "smoothed_macro_f1_gain_at_least_2pp": bool(s48.macro_f1 - s2.macro_f1 >= 0.02),
        "weak_class_mean_recall_not_worse_than_5pp": bool(weak["nb48_seed_median"] - weak["v2_seed_median"] >= -0.05),
        "dumbbell_row_recall_not_worse_than_v2": bool(s48["recall__dumbbell_row"] - s2["recall__dumbbell_row"] >= 0),
        "supported_called_unknown_not_worse_than_3pp": bool(s48.supported_called_unknown - s2.supported_called_unknown <= 0.03),
        "downtime_called_unknown_not_worse_than_5pp": bool(s48.downtime_called_unknown - s2.downtime_called_unknown <= 0.05),
    }
    verdict = {"evaluation": "long_video_round3_test_v1_eval1", "verdict": "nb48_better_informational" if all(criteria.values()) else "keep_v2",
               "criteria": criteria, "macro_f1": {"v2": float(s2.macro_f1), "nb48": float(s48.macro_f1), "gain": float(s48.macro_f1 - s2.macro_f1)},
               "weak_classes_scored": present, "weak_class_mean_recall": weak,
               "supported_called_unknown": {"v2": float(s2.supported_called_unknown), "nb48": float(s48.supported_called_unknown)},
               "downtime_called_unknown": {"v2": float(s2.downtime_called_unknown), "nb48": float(s48.downtime_called_unknown)},
               "internal_test_macro_f1_seed_mean": {"v2": float(internal_c.end_to_end_macro_f1.mean()), "nb48": float(internal_t.end_to_end_macro_f1.mean())},
               "test_videos": test, "caveat": "two test videos: informational only", "promotion": False}
    (args.out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    for name in per:
        pd.concat(per[name].values()).to_csv(args.out_dir / f"timeline_{name}_smoothed.csv.gz", index=False)
    print(json.dumps(verdict, indent=2))
    cols = ["macro_f1", "accuracy", "block_f1", "supported_called_unknown", "downtime_called_unknown", *[f"recall__{c}" for c in SUPPORTED]]
    print(summary[cols].round(3).T.to_string())


if __name__ == "__main__":
    main()
