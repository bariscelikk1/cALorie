#!/usr/bin/env python3
"""Score Notebook 47 (three per-seed ZIPs) once on the locked round-2 test videos.

Predeclared in ml/data/long_video_round2_v1/PLAN.md section 3. Control: frozen Notebook 46 (three seeds).
Treatment: the three Notebook 47 seeds. Same scorer, decoder, and threshold as every earlier long-video evaluation.
The four criteria (all must hold for Notebook 47 to replace Notebook 46):
  1. smoothed pooled Macro F1 gain >= 3 pp (seed medians)
  2. mean time recall over the weak classes gain >= 10 pp
  3. supported exercise time called unknown no more than 3 pp worse
  4. rest/transition time called unknown no more than 5 pp worse
The video-level bootstrap interval and the internal clip test are reported, not judged.
Usage: score_nb47_round2_v1.py REPO_ROOT OUT_DIR seed42.zip seed137.zip seed2026.zip [--device mps]
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

from score_long_video_test_v1 import BOOTSTRAP, STREAMS, SUPPORTED, SmallTCN, load, metrics, predict, smooth, truth_at
from score_long_video_test_v1_eval2 import nb46_models

WEAK = ["tricep_extension", "lateral_raise", "bicep_curl", "dumbbell_row", "shoulder_press"]
SEEDS = (42, 137, 2026)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def nb47_models(zips: list[Path], device):
    models, internal = {}, []
    for seed, path in zip(SEEDS, zips):
        with zipfile.ZipFile(path) as z:
            meta = json.loads(z.read("run_metadata.json"))
            assert meta["seed"] == seed and not meta["dry_run"] and not meta["round2_test_videos_read"], path
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
            models[f"nb47_seed{seed}"] = (cls, gates)
            internal.append(pd.read_csv(io.BytesIO(z.read("internal_test_metrics.csv"))))
    return models, pd.concat(internal, ignore_index=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path); ap.add_argument("out_dir", type=Path)
    ap.add_argument("zips", type=Path, nargs=3); ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    device = torch.device(args.device)
    data, evidence = args.root / "ml/data/long_video_round2_v1", args.root / "ml/artifacts/long_video_round2_v1"
    lock = json.loads((data / "LOCK.json").read_text())
    for name, expected in lock["annotations"].items():
        assert sha256((data / "annotations" / name).read_bytes()) == expected, f"Lock broken: {name}"
    for vid, expected in lock["evidence"].items():
        assert sha256((evidence / f"long_video_round2_v1_{vid}.zip").read_bytes()) == expected, f"Lock broken: {vid}"
    test = sorted(lock["evidence"])
    print("Lock verified:", len(test), "test videos")

    nb47, internal47 = nb47_models(args.zips, device)
    control = {k.replace("final_nb46", "nb46"): v for k, v in nb46_models(args.root, device).items()}
    models = {**control, **nb47}
    per = {name: {} for name in models}
    for vid in test:
        ann = pd.read_csv(data / "annotations" / f"{vid}.csv").sort_values("start_s").reset_index(drop=True)
        with zipfile.ZipFile(evidence / f"long_video_round2_v1_{vid}.zip") as z:
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
    rows = []
    for name in per:
        rows.append({"model": name, "video_id": "ALL", **metrics([per[name][v] for v in test])})
        rows += [{"model": name, "video_id": v, **metrics([per[name][v]])} for v in test]
    table = pd.DataFrame(rows)
    table.to_csv(args.out_dir / "metrics_by_model_video.csv", index=False)
    pooled = table[table.video_id == "ALL"].set_index("model")
    arms = {"nb46_seed_median": [m for m in per if m.startswith("nb46")], "nb47_seed_median": [m for m in per if m.startswith("nb47")]}
    summary = pd.DataFrame({a: pooled.loc[ms].median(numeric_only=True) for a, ms in arms.items()}).T
    summary.to_csv(args.out_dir / "summary.csv")
    present = [w for w in WEAK if not pooled[f"recall__{w}"].isna().any()]
    weak = {a: float(np.mean([summary.loc[a, f"recall__{w}"] for w in present])) for a in arms}

    rng = np.random.default_rng(20261028)
    deltas = []
    f1 = lambda ms, sample: np.median([metrics([per[m][v] for v in sample])["macro_f1"] for m in ms])
    for _ in range(BOOTSTRAP):
        sample = rng.choice(test, size=len(test), replace=True)
        deltas.append(f1(arms["nb47_seed_median"], sample) - f1(arms["nb46_seed_median"], sample))
    s46, s47 = summary.loc["nb46_seed_median"], summary.loc["nb47_seed_median"]
    criteria = {
        "smoothed_macro_f1_gain_at_least_3pp": bool(s47.macro_f1 - s46.macro_f1 >= 0.03),
        "weak_class_mean_recall_gain_at_least_10pp": bool(weak["nb47_seed_median"] - weak["nb46_seed_median"] >= 0.10),
        "supported_called_unknown_not_worse_than_3pp": bool(s47.supported_called_unknown - s46.supported_called_unknown <= 0.03),
        "downtime_called_unknown_not_worse_than_5pp": bool(s47.downtime_called_unknown - s46.downtime_called_unknown <= 0.05),
    }
    verdict = {"evaluation": "long_video_round2_test_v1_eval1", "verdict": "replace_nb46" if all(criteria.values()) else "keep_nb46",
               "criteria": criteria, "macro_f1": {"nb46": float(s46.macro_f1), "nb47": float(s47.macro_f1), "gain": float(s47.macro_f1 - s46.macro_f1)},
               "macro_f1_gain_bootstrap_95ci_reported_only": [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))],
               "weak_classes_scored": present, "weak_class_mean_recall": weak,
               "supported_called_unknown": {"nb46": float(s46.supported_called_unknown), "nb47": float(s47.supported_called_unknown)},
               "downtime_called_unknown": {"nb46": float(s46.downtime_called_unknown), "nb47": float(s47.downtime_called_unknown)},
               "internal_test_macro_f1_nb47_seed_mean": float(internal47.end_to_end_macro_f1.mean()), "test_videos": test, "promotion": False}
    (args.out_dir / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    for name in per:
        pd.concat(per[name].values()).to_csv(args.out_dir / f"timeline_{name}_smoothed.csv.gz", index=False)
    print(json.dumps(verdict, indent=2))
    cols = ["macro_f1", "accuracy", "block_f1", "supported_called_unknown", "downtime_called_unknown", *[f"recall__{c}" for c in SUPPORTED]]
    print(summary[cols].round(3).T.to_string())


if __name__ == "__main__":
    main()
