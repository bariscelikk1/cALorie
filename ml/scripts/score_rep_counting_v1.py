#!/usr/bin/env python3
"""Score the generic rep counter on RepCount-A clips with published human counts.

Roles come from ml/data/repcount_intake_v2/training_v1_roles.csv. Tuning uses
role=dev only; train and sealed_test are scored with frozen constants.
Usage: score_rep_counting_v1.py REPO_ROOT OUT_DIR --roles dev[,train,sealed_test] [--grid]
"""

from __future__ import annotations

import argparse
import io
import itertools
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import reps_and_calories as rc  # noqa: E402

CLASSES = ["bench_press", "jumping_jack", "pull_up", "push_up", "sit_up", "squat"]


def pose_index(root: Path) -> dict:
    """video_id -> (zip path, member). Later archives win (make-up last)."""
    base = root / "ml/artifacts/repcount_intake_v2"
    zips = [base / "pilot/calorie_repcount_intake_v2_pilot.zip"] + [base / f"full/calorie_repcount_intake_v2_shard{i}.zip" for i in range(8)]
    zips.append(base / "full/calorie_repcount_intake_v2_makeup.zip")
    index = {}
    for path in zips:
        with zipfile.ZipFile(path) as z:
            for m in z.namelist():
                if m.startswith("report/pose/") and m.endswith(".npz"):
                    index[Path(m).stem] = (path, m)
    v1 = root / "ml/artifacts/repcount_external_development_v1/calorie_repcount_external_development_v1_report.zip"
    with zipfile.ZipFile(v1) as z:
        for m in z.namelist():
            if m.startswith("report/pose/") and m.endswith(".npz"):
                index.setdefault(Path(m).stem, (v1, m))
    return index


def load_clips(root: Path, roles: list[str]) -> pd.DataFrame:
    r = pd.read_csv(root / "ml/data/repcount_intake_v2/training_v1_roles.csv")
    counts = pd.concat([pd.read_csv(root / f"ml/data/repcount_intake_v2/{f}")[["video_id", "published_count"]]
                        for f in ("full_selection.csv", "pilot_selection.csv")]).drop_duplicates("video_id")
    r = r[(r.role.isin(roles)) & (r.label.isin(CLASSES))].merge(counts, on="video_id", how="left")
    return r


def score(clips: pd.DataFrame, index: dict, params: dict) -> pd.DataFrame:
    rows, cache = [], {}
    for c in clips.itertuples():
        if c.video_id not in cache:
            path, member = index[c.video_id]
            with zipfile.ZipFile(path) as z:
                d = np.load(io.BytesIO(z.read(member)))
                cache[c.video_id] = (d["landmarks"].astype(np.float32), d["image_landmarks"].astype(np.float32) if "image_landmarks" in d.files else None)
        norm, img = cache[c.video_id]
        rows.append({"video_id": c.video_id, "role": c.role, "label": c.label, "true": int(c.published_count),
                     "pred": rc.count_reps(norm, img, params)})
    t = pd.DataFrame(rows)
    t["abs_err"] = (t.pred - t.true).abs()
    t["exact"] = t.abs_err == 0
    t["within1"] = t.abs_err <= 1
    return t


def summarize(t: pd.DataFrame) -> pd.DataFrame:
    g = t.groupby("label")
    out = pd.DataFrame({"clips": g.size(), "exact": g.exact.mean(), "within1": g.within1.mean(), "mae": g.abs_err.mean(),
                        "median_rel_err": g.apply(lambda d: float(np.median(d.abs_err / d.true.clip(lower=1))), include_groups=False)})
    out.loc["ALL"] = [len(t), t.exact.mean(), t.within1.mean(), t.abs_err.mean(), float(np.median(t.abs_err / t.true.clip(lower=1)))]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path); ap.add_argument("out", type=Path)
    ap.add_argument("--roles", default="dev"); ap.add_argument("--grid", action="store_true")
    a = ap.parse_args()
    roles = a.roles.split(",")
    clips, index = load_clips(a.root, roles), pose_index(a.root)
    assert clips.published_count.notna().all(), clips[clips.published_count.isna()].video_id.tolist()[:5]
    a.out.mkdir(parents=True, exist_ok=True)
    if a.grid:
        results = []
        for sig, sm, gap, prom in itertools.product(["normalized", "image"], [0.2, 0.4, 0.6], [0.4, 0.6, 0.8, 1.0], [0.2, 0.3, 0.4, 0.5]):
            p = {"signal": sig, "smooth_s": sm, "min_gap_s": gap, "min_prominence": prom}
            s = summarize(score(clips, index, p))
            results.append({**p, "within1": s.loc["ALL", "within1"], "exact": s.loc["ALL", "exact"], "mae": s.loc["ALL", "mae"],
                            "worst_class_within1": s.drop("ALL").within1.min()})
        g = pd.DataFrame(results).sort_values(["within1", "mae"], ascending=[False, True])
        g.to_csv(a.out / "tuning_grid_dev.csv", index=False)
        print(g.head(8).round(3).to_string(index=False))
        return
    t = score(clips, index, rc.PARAMS)
    t.to_csv(a.out / f"per_clip_{'_'.join(roles)}.csv", index=False)
    s = summarize(t); s.to_csv(a.out / f"summary_{'_'.join(roles)}.csv")
    print(f"constants: {rc.PARAMS}"); print(s.round(3).to_string())


if __name__ == "__main__":
    main()
