#!/usr/bin/env python3
"""Tier-1 automatic checks for RepCount-A intake v2 (pose features and rules)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


# MediaPipe subset order used by every cALorie pose file (17 joints).
NOSE, L_SH, R_SH, L_EL, R_EL, L_WR, R_WR = 0, 5, 6, 7, 8, 9, 10
L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN = 11, 12, 13, 14, 15, 16
BODY_12 = [L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN]


def angle(a, b, c):
    """Angle at b in degrees for arrays of shape (T, 2)."""
    u, v = a - b, c - b
    cos = (u * v).sum(1) / np.maximum(np.linalg.norm(u, axis=1) * np.linalg.norm(v, axis=1), 1e-6)
    return np.degrees(np.arccos(np.clip(cos, -1, 1)))


def lag_autocorrelation(signal, lag):
    signal = signal - signal.mean()
    if lag < 2 or lag >= len(signal) - 2 or signal.std() < 1e-8:
        return 0.0
    left, right = signal[:-lag], signal[lag:]
    return float(np.dot(left, right) / max(np.linalg.norm(left) * np.linalg.norm(right), 1e-8))


def features(npz_path: Path, published_count: int) -> dict:
    data = np.load(npz_path)
    image = data["image_landmarks"].astype(np.float64)  # x, y in [0, 1]; y points down
    detected = data["detected"]
    fps = float(data["target_fps"])
    xy, vis = image[:, :, :2], image[:, :, 3]
    shoulder, hip = xy[:, [L_SH, R_SH]].mean(1), xy[:, [L_HIP, R_HIP]].mean(1)
    torso_vec = shoulder - hip
    torso_len = np.linalg.norm(torso_vec, axis=1)
    torso_scale = float(np.median(torso_len))
    # 0 = upright, 90 = horizontal, 180 = upside down.
    torso_from_vertical = np.degrees(np.arctan2(np.abs(torso_vec[:, 0]), -torso_vec[:, 1]))
    wrist_y = xy[:, [L_WR, R_WR], 1].mean(1)
    knee = np.minimum(angle(xy[:, L_HIP], xy[:, L_KN], xy[:, L_AN]), angle(xy[:, R_HIP], xy[:, R_KN], xy[:, R_AN]))
    thigh_vec = xy[:, [L_KN, R_KN]].mean(1) - hip
    # Unwrap so a swing across +/-180 degrees is not read as a 360-degree range.
    thigh_angle = np.degrees(np.unwrap(np.arctan2(thigh_vec[:, 1], thigh_vec[:, 0])))
    torso_angle = np.degrees(np.unwrap(np.arctan2(torso_vec[:, 1], torso_vec[:, 0])))
    ankle_spread = np.abs(xy[:, L_AN, 0] - xy[:, R_AN, 0]) / max(torso_scale, 1e-6)
    body_visible = (vis[:, BODY_12] >= 0.5).sum(1) >= 10

    # Edit cuts: the torso jumps or changes size abruptly between consecutive 15-FPS samples.
    hip_jump = np.linalg.norm(np.diff(hip, axis=0), axis=1) / max(torso_scale, 1e-6)
    scale_jump = np.abs(np.diff(np.log(np.maximum(torso_len, 1e-4))))
    cuts = int(((hip_jump > 0.8) | (scale_jump > np.log(1.6))).sum())

    # Periodicity at the period implied by RepCount's published count.
    duration_s = len(xy) / fps
    expected_lag = int(round(len(xy) / max(published_count, 1)))
    normalized = data["landmarks"][:, :, :2].reshape(len(xy), -1)
    centered = normalized - normalized.mean(0)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    pc1 = centered @ vt[0]

    def p(values, q):
        return float(np.percentile(values, q))

    return {
        "frames": int(len(xy)), "duration_s": duration_s, "published_count": int(published_count),
        "pose_detection_rate": float(detected.mean()),
        "body_visible_fraction": float(body_visible.mean()),
        "cut_count": cuts,
        "rep_autocorrelation": lag_autocorrelation(pc1, expected_lag),
        "torso_from_vertical_median": p(torso_from_vertical, 50),
        "torso_from_vertical_range": p(torso_from_vertical, 95) - p(torso_from_vertical, 5),
        "wrists_above_nose_fraction": float((wrist_y < xy[:, NOSE, 1]).mean()),
        "wrists_above_shoulders_fraction": float((wrist_y < shoulder[:, 1]).mean()),
        "wrist_height_range": (p(wrist_y, 95) - p(wrist_y, 5)) / max(torso_scale, 1e-6),
        "knee_angle_range": p(knee, 95) - p(knee, 5),
        "knee_angle_min": p(knee, 5),
        "ankle_spread_range": p(ankle_spread, 95) - p(ankle_spread, 5),
        "torso_swing_range": p(torso_angle, 95) - p(torso_angle, 5),
        "thigh_swing_range": p(thigh_angle, 95) - p(thigh_angle, 5),
        "hip_vertical_range": (p(hip[:, 1], 95) - p(hip[:, 1], 5)) / max(torso_scale, 1e-6),
    }


RULE_SET = "tier1_v1"
# Locked 2026-10-25 from the 64-clip pilot only. Thresholds favour rejecting usable
# clips (they go to visual review) over accepting a wrong or unusable one.
COMMON = {"min_pose_detection": 0.90, "max_cuts": 2, "min_rep_autocorrelation": 0.30}
ALWAYS_REVIEW = {"unknown_front_raise", "unknown_others"}  # frequent supported-motion confusers


def class_rule(bucket: str, f: dict) -> list[str]:
    """Return the failed class-specific checks (empty list = pass)."""
    fails = []
    def need(ok, name):
        if not ok:
            fails.append(name)
    if bucket == "squat":
        need(f["torso_from_vertical_median"] <= 30, "torso_upright")
        need(f["knee_angle_range"] >= 45, "knee_cycles")
    elif bucket == "jumping_jack":
        need(f["torso_from_vertical_median"] <= 20, "torso_upright")
        need(f["wrist_height_range"] >= 1.2, "arms_cycle")
        need(f["ankle_spread_range"] >= 0.3, "legs_cycle")
    elif bucket == "pull_up":
        need(f["torso_from_vertical_median"] <= 20, "torso_vertical")
        need(f["wrists_above_nose_fraction"] >= 0.55, "hands_overhead")
        need(f["hip_vertical_range"] >= 0.5, "body_rises")
    elif bucket == "push_up":
        need(f["torso_from_vertical_median"] >= 60, "torso_horizontal")
        need(f["wrists_above_shoulders_fraction"] <= 0.10, "hands_below_shoulders")
        need(f["torso_from_vertical_range"] <= 45, "no_pike_or_flip")
        need(f["hip_vertical_range"] <= 1.2, "no_plyometric_travel")
    elif bucket == "bench_press":
        need(f["torso_from_vertical_median"] >= 60, "torso_horizontal")
        need(f["wrists_above_shoulders_fraction"] >= 0.80, "hands_above_shoulders")
    elif bucket == "sit_up":
        need(f["torso_from_vertical_range"] >= 50, "torso_cycles")
        need(20 <= f["torso_from_vertical_median"] <= 75, "between_lying_and_up")
        need(f["hip_vertical_range"] <= 1.0, "hips_stay_down")
        need(f["torso_swing_range"] > f["thigh_swing_range"], "torso_not_legs")
    elif bucket == "unknown_battle_rope_or_pommel":
        pass  # unknown by construction; only the common gates apply
    else:
        fails.append("no_rule")
    return fails


def decide(bucket: str, f: dict) -> tuple[str, str]:
    if bucket in ALWAYS_REVIEW:
        return "review", "bucket_always_reviewed"
    fails = []
    if f["pose_detection_rate"] < COMMON["min_pose_detection"]:
        fails.append("pose_detection")
    if f["cut_count"] > COMMON["max_cuts"]:
        fails.append("edit_cuts")
    if not bucket.startswith("unknown") and f["rep_autocorrelation"] < COMMON["min_rep_autocorrelation"]:
        fails.append("rep_periodicity")
    fails += class_rule(bucket, f)
    return ("auto_accept", "") if not fails else ("review", ";".join(fails))


def rule_bucket(published_action: str) -> str:
    mapping = {
        "squat": "squat", "squant": "squat", "situp": "sit_up",
        "pull_up": "pull_up", "pullups": "pull_up",
        "bench_pressing": "bench_press", "benchpressing": "bench_press",
        "push_up": "push_up", "pushups": "push_up",
        "jump_jack": "jumping_jack", "jumpjacks": "jumping_jack",
        "front_raise": "unknown_front_raise", "frontraise": "unknown_front_raise",
        "pommelhorse": "unknown_battle_rope_or_pommel", "battle_rope": "unknown_battle_rope_or_pommel",
        "others": "unknown_others",
    }
    return mapping[published_action]


AUTO_LABEL = {"unknown_battle_rope_or_pommel": "unknown"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_dir", type=Path, help="extracted Notebook 40 report/ directory")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    selection = pd.read_csv(args.report_dir / "pilot_selection.csv")
    rows = []
    for row in selection[selection.role == "pilot"].itertuples(index=False):
        path = args.report_dir / "pose" / f"{row.video_id}.npz"
        f = features(path, int(row.published_count))
        bucket = rule_bucket(row.published_action)
        decision, reasons = decide(bucket, f)
        rows.append({"video_id": row.video_id, "published_action": row.published_action, "rule_bucket": bucket,
                     "tier1_decision": decision,
                     "tier1_label": AUTO_LABEL.get(bucket, bucket) if decision == "auto_accept" else "",
                     "tier1_fail_reasons": reasons, "rule_set": RULE_SET, **f})
    pd.DataFrame(rows).to_csv(args.output, index=False, float_format="%.4f")
    print(f"wrote {args.output}: {len(rows)} clips, {sum(r['tier1_decision'] == 'auto_accept' for r in rows)} auto-accepted")


if __name__ == "__main__":
    main()
