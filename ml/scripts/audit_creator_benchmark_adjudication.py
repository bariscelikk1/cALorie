#!/usr/bin/env python3
"""Audit the six-creator benchmark adjudication and confirmation queue."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_SUPPORTED_CLASSES = {
    "bench_press",
    "bicep_curl",
    "deadlift",
    "dumbbell_row",
    "jumping_jack",
    "lat_pulldown",
    "lateral_raise",
    "lunge",
    "pull_up",
    "push_up",
    "shoulder_press",
    "sit_up",
    "squat",
    "tricep_extension",
}
ALLOWED_DECISIONS = {
    "accept_supported",
    "accept_unknown",
    "reject_no_target_motion",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_float(value: str, field: str, interval_id: str, errors: list[str]) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        errors.append(f"{interval_id}: {field} must be numeric")
        return None
    if not math.isfinite(parsed):
        errors.append(f"{interval_id}: {field} must be finite")
        return None
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--original-candidates", type=Path, required=True)
    parser.add_argument("--supplemental-candidates", type=Path, required=True)
    parser.add_argument("--confirmation-queue", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    adjudication = read_csv(args.adjudication)
    original = read_csv(args.original_candidates)
    supplemental = read_csv(args.supplemental_candidates)
    confirmation = read_csv(args.confirmation_queue)
    errors: list[str] = []
    warnings: list[str] = []

    expected_rows = original + supplemental
    expected_by_id = {row["interval_id"]: row for row in expected_rows}
    adjudicated_by_id = {row["interval_id"]: row for row in adjudication}
    ids = [row["interval_id"] for row in adjudication]
    if len(ids) != len(set(ids)):
        errors.append("adjudication contains duplicate interval_id values")
    if set(ids) != set(expected_by_id):
        errors.append(
            "adjudication ID mismatch: "
            f"missing={sorted(set(expected_by_id) - set(ids))}, "
            f"extra={sorted(set(ids) - set(expected_by_id))}"
        )

    retained_by_video: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    supported_counts: Counter[str] = Counter()
    creator_counts: Counter[str] = Counter()
    decision_counts: Counter[str] = Counter()
    duration_by_label: Counter[str] = Counter()

    for row in adjudication:
        interval_id = row["interval_id"]
        decision = row["decision"]
        label = row["reviewed_label"]
        decision_counts[decision] += 1
        if decision not in ALLOWED_DECISIONS:
            errors.append(f"{interval_id}: unsupported decision {decision!r}")
            continue
        if row["benchmark_ready"] != "false":
            errors.append(f"{interval_id}: benchmark_ready must remain false")
        if row["needs_second_review"] != "true":
            errors.append(f"{interval_id}: needs_second_review must remain true")
        if row["predictions_used_for_decision"] != "false":
            errors.append(f"{interval_id}: predictions_used_for_decision must be false")
        if row["blind_review"] != "false":
            errors.append(f"{interval_id}: blind_review must honestly remain false")

        if decision == "reject_no_target_motion":
            if row["start_s"] or row["end_s"]:
                errors.append(f"{interval_id}: rejected locator must have blank boundaries")
            if label != "unknown" or row["review_status"] != "rejected":
                errors.append(f"{interval_id}: rejected locator must be rejected/unknown")
            continue

        start = parse_float(row["start_s"], "start_s", interval_id, errors)
        end = parse_float(row["end_s"], "end_s", interval_id, errors)
        if start is None or end is None:
            continue
        if start >= end:
            errors.append(f"{interval_id}: start_s must be less than end_s")
        source = expected_by_id.get(interval_id)
        if source:
            locator_start = float(source["start_s"])
            locator_end = float(source["end_s"])
            if start < locator_start - 15 or end > locator_end + 15:
                errors.append(f"{interval_id}: reviewed boundary exceeds 15-second evidence padding")
        retained_by_video[row["video_id"]].append((start, end, interval_id))
        creator_counts[row["creator"]] += 1
        duration_by_label[label] += end - start

        if decision == "accept_supported":
            if label not in EXPECTED_SUPPORTED_CLASSES:
                errors.append(f"{interval_id}: invalid supported label {label!r}")
            supported_counts[label] += 1
        elif label != "unknown":
            errors.append(f"{interval_id}: accept_unknown must use label 'unknown'")

    for video_id, intervals in retained_by_video.items():
        intervals.sort()
        for previous, current in zip(intervals, intervals[1:]):
            if current[0] < previous[1]:
                errors.append(
                    f"{video_id}: retained overlap {previous[2]} [{previous[0]}, {previous[1]}) "
                    f"with {current[2]} [{current[0]}, {current[1]})"
                )

    missing_classes = sorted(EXPECTED_SUPPORTED_CLASSES - set(supported_counts))
    if missing_classes:
        errors.append(f"missing supported-class coverage: {missing_classes}")

    confirmation_ids = [row["interval_id"] for row in confirmation]
    if len(confirmation_ids) != len(set(confirmation_ids)):
        errors.append("confirmation queue contains duplicate interval_id values")
    if not set(confirmation_ids) <= set(adjudicated_by_id):
        errors.append("confirmation queue contains unknown interval IDs")
    required_confirmation = {
        row["interval_id"]
        for row in adjudication
        if (row["decision"].startswith("accept") and row["confidence"] == "medium")
        or row["decision"] == "accept_unknown"
    }
    if not required_confirmation <= set(confirmation_ids):
        errors.append(
            "confirmation queue misses required rows: "
            f"{sorted(required_confirmation - set(confirmation_ids))}"
        )
    minimum_repeat = math.ceil(len(adjudication) * 0.10)
    if len(confirmation_ids) < minimum_repeat:
        errors.append(
            f"confirmation queue has {len(confirmation_ids)} rows; minimum is {minimum_repeat}"
        )
    independent_fields = {
        "reviewer_id",
        "independent_decision",
        "independent_label",
        "independent_start_s",
        "independent_end_s",
        "confidence",
        "notes",
    }
    for row in confirmation:
        prefilled = sorted(field for field in independent_fields if row.get(field, "").strip())
        if prefilled:
            errors.append(f"{row['interval_id']}: independent fields are prefilled: {prefilled}")

    if len(adjudication) != 41:
        errors.append(f"expected 41 adjudication rows, found {len(adjudication)}")
    if len(expected_rows) != 41:
        errors.append(f"candidate sources should contain 41 rows, found {len(expected_rows)}")

    pending_confirmation = len(confirmation_ids)
    report = {
        "status": "structural_pass_benchmark_unlocked" if not errors else "failed",
        "structural_errors": errors,
        "warnings": warnings,
        "benchmark_locked": False,
        "lock_blockers": [
            f"{pending_confirmation} independent confirmation decisions remain blank",
            "continuous reviewed timelines and strict annotation audit are not complete",
        ],
        "counts": {
            "candidate_rows": len(expected_rows),
            "adjudication_rows": len(adjudication),
            "decisions": dict(sorted(decision_counts.items())),
            "retained_regions": sum(decision.startswith("accept") for decision in decision_counts.elements()),
            "supported_classes_present": len(supported_counts),
            "confirmation_queue_rows": len(confirmation_ids),
            "minimum_independent_repeat_rows": minimum_repeat,
        },
        "supported_regions_by_class": dict(sorted(supported_counts.items())),
        "retained_regions_by_creator": dict(sorted(creator_counts.items())),
        "retained_duration_s_by_label": {
            label: round(duration, 3) for label, duration in sorted(duration_by_label.items())
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
