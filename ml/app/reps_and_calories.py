"""Rep counting and MET-based calories for cALorie (plan: REPS_AND_CALORIES_PLAN.md).

Reps: one generic peak counter on the dominant motion of an exercise segment.
Calories: kcal = MET x 3.5 x weight_kg / 200 x minutes, with a +/-35% range.
Both are estimates; see FINAL_REPORT.md for what was and was not validated.
"""

from __future__ import annotations

import numpy as np
from scipy.signal import find_peaks, savgol_filter

FPS = 15
# Constants tuned on RepCount dev clips only, then frozen (see ml/artifacts/rep_counting_v1).
PARAMS = {"smooth_s": 0.6, "min_gap_s": 0.4, "min_prominence": 0.4, "signal": "normalized"}

# MET per exercise: 2024 Adult Compendium of Physical Activities categories, rounded.
# 02052 squat/deadlift 5.0 | 02054 multi-exercise weights 8-15 reps 3.5 |
# 02020 vigorous calisthenics (jumping jacks, push-ups, pull-ups) 7.5 | 02056 body-weight
# resistance 3.0 | 2011 moderate calisthenics 3.8. Push-up, pull-up use a moderate 5.0.
MET = {
    "squat": 5.0, "deadlift": 5.0, "lunge": 3.8, "push_up": 5.0, "pull_up": 5.0, "sit_up": 3.8, "jumping_jack": 7.5,
    "bench_press": 3.5, "bicep_curl": 3.5, "dumbbell_row": 3.5, "lat_pulldown": 3.5, "lateral_raise": 3.5,
    "shoulder_press": 3.5, "tricep_extension": 3.5,
}
CALORIE_RANGE = 0.35


def motion_signal(normalized: np.ndarray, image: np.ndarray | None, kind: str) -> np.ndarray:
    """One dominant-motion signal (first principal component) for a segment."""
    source = image if (kind == "image" and image is not None) else normalized
    x = source[:, :, :2].reshape(len(source), -1)
    x = x - x.mean(0)
    if not np.isfinite(x).all() or len(x) < 3:
        return np.zeros(len(source))
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    return x @ vt[0]


def count_reps(normalized: np.ndarray, image: np.ndarray | None = None, params: dict | None = None) -> int:
    p = {**PARAMS, **(params or {})}
    if len(normalized) < int(2 * FPS):
        return 0
    signal = motion_signal(normalized, image, p["signal"])
    window = max(5, int(p["smooth_s"] * FPS) | 1)
    signal = savgol_filter(signal, window, 2) if len(signal) > window else signal
    low, high = np.percentile(signal, [5, 95])
    spread = high - low
    if spread < 1e-6:
        return 0
    peaks, _ = find_peaks(signal, distance=max(1, int(p["min_gap_s"] * FPS)), prominence=p["min_prominence"] * spread)
    return int(len(peaks))


def estimate_calories(label: str, weight_kg: float, seconds: float) -> tuple[float, float, float]:
    """Return (estimate, low, high) kcal for `seconds` of `label`."""
    if label not in MET:
        return 0.0, 0.0, 0.0
    kcal = MET[label] * 3.5 * weight_kg / 200.0 * (seconds / 60.0)
    return kcal, kcal * (1 - CALORIE_RANGE), kcal * (1 + CALORIE_RANGE)


# Classes whose dev clips were within one rep at least 50% of the time (decided on dev; plan section 1).
REP_VALIDATED = {"jumping_jack", "pull_up", "push_up", "sit_up", "squat"}


def summarize_exercises(table, pose: np.ndarray, weight_kg: float):
    """Per-exercise totals from a timeline table (start_s, end_s, label) and the full pose."""
    import pandas as pd
    rows = {}
    for r in table.itertuples():
        if r.label == "unknown":
            continue
        seg = pose[int(r.start_s * FPS):int(r.end_s * FPS)]
        row = rows.setdefault(r.label, {"exercise": r.label, "seconds": 0.0, "reps": 0})
        row["seconds"] += r.end_s - r.start_s
        row["reps"] += count_reps(seg) if r.label in REP_VALIDATED else 0
    out = []
    for label, row in rows.items():
        kcal, low, high = estimate_calories(label, weight_kg, row["seconds"])
        out.append({"exercise": label, "seconds": round(row["seconds"]),
                    "reps": row["reps"] if label in REP_VALIDATED else None,
                    "kcal": round(kcal), "kcal_low": round(low), "kcal_high": round(high)})
    return pd.DataFrame(out).sort_values("seconds", ascending=False).reset_index(drop=True) if out else pd.DataFrame(
        columns=["exercise", "seconds", "reps", "kcal", "kcal_low", "kcal_high"])
