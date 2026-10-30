#!/usr/bin/env python3
"""Validate independent creator confirmation and materialize resolved regions."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


SUPPORTED = {
    "bench_press", "bicep_curl", "deadlift", "dumbbell_row", "jumping_jack",
    "lat_pulldown", "lateral_raise", "lunge", "pull_up", "push_up",
    "shoulder_press", "sit_up", "squat", "tricep_extension",
}
DECISIONS = {"accept_supported", "accept_unknown", "reject_no_target_motion"}
CONFIDENCE = {"high", "medium", "low"}
SOURCE_FIELDS = (
    "queue_order", "interval_id", "confirmation_reason", "source_decision",
    "source_label", "source_start_s", "source_end_s",
)
INDEPENDENT_FIELDS = (
    "reviewer_id", "independent_decision", "independent_label",
    "independent_start_s", "independent_end_s", "confidence", "notes",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def number(value: str, location: str, errors: list[str]) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        errors.append(f"{location}: expected numeric boundary, got {value!r}")
        return None
    if not math.isfinite(parsed):
        errors.append(f"{location}: boundary must be finite")
        return None
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjudication", required=True, type=Path)
    parser.add_argument("--queue", required=True, type=Path)
    parser.add_argument("--completed", required=True, type=Path)
    parser.add_argument("--resolved", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    adjudication = read_csv(args.adjudication)
    queue = read_csv(args.queue)
    completed = read_csv(args.completed)
    errors: list[str] = []
    warnings: list[str] = []

    queue_by_id = {row["interval_id"]: row for row in queue}
    completed_by_id = {row.get("interval_id", ""): row for row in completed}
    adjudication_by_id = {row["interval_id"]: row for row in adjudication}

    for name, rows in (("queue", queue), ("completed", completed), ("adjudication", adjudication)):
        ids = [row.get("interval_id", "") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{name} contains duplicate interval_id values")
    if set(completed_by_id) != set(queue_by_id):
        errors.append(
            "completed confirmation ID mismatch: "
            f"missing={sorted(set(queue_by_id) - set(completed_by_id))}, "
            f"extra={sorted(set(completed_by_id) - set(queue_by_id))}"
        )
    if not set(queue_by_id) <= set(adjudication_by_id):
        errors.append("queue contains IDs absent from adjudication")

    reviewer_ids: set[str] = set()
    label_agreements = 0
    decision_agreements = 0
    exact_boundary_agreements = 0
    corrected_rows: list[dict[str, object]] = []

    for interval_id, source in queue_by_id.items():
        row = completed_by_id.get(interval_id)
        if row is None:
            continue
        for field in SOURCE_FIELDS:
            if row.get(field, "") != source.get(field, ""):
                errors.append(f"{interval_id}: source field {field} changed")
        missing = [field for field in INDEPENDENT_FIELDS if not row.get(field, "").strip()]
        if missing:
            errors.append(f"{interval_id}: blank independent fields: {missing}")
            continue

        reviewer_ids.add(row["reviewer_id"].strip())
        decision = row["independent_decision"].strip()
        label = row["independent_label"].strip()
        confidence = row["confidence"].strip().lower()
        if decision not in DECISIONS:
            errors.append(f"{interval_id}: invalid independent decision {decision!r}")
        if confidence not in CONFIDENCE:
            errors.append(f"{interval_id}: invalid confidence {confidence!r}")
        if decision == "accept_supported" and label not in SUPPORTED:
            errors.append(f"{interval_id}: invalid supported label {label!r}")
        if decision != "accept_supported" and label != "unknown":
            errors.append(f"{interval_id}: non-supported decision must use label 'unknown'")

        start = number(row["independent_start_s"], f"{interval_id}.start", errors)
        end = number(row["independent_end_s"], f"{interval_id}.end", errors)
        if start is not None and end is not None and start >= end:
            errors.append(f"{interval_id}: expected start < end")

        decision_same = decision == source["source_decision"]
        label_same = label == source["source_label"]
        boundary_same = (
            row["independent_start_s"] == source["source_start_s"]
            and row["independent_end_s"] == source["source_end_s"]
        )
        decision_agreements += decision_same
        label_agreements += label_same
        exact_boundary_agreements += boundary_same
        if not (decision_same and label_same and boundary_same):
            corrected_rows.append({
                "interval_id": interval_id,
                "decision_changed": not decision_same,
                "label_changed": not label_same,
                "boundary_changed": not boundary_same,
                "source": {
                    "decision": source["source_decision"], "label": source["source_label"],
                    "start_s": source["source_start_s"], "end_s": source["source_end_s"],
                },
                "independent": {
                    "decision": decision, "label": label,
                    "start_s": row["independent_start_s"], "end_s": row["independent_end_s"],
                },
            })

    if len(reviewer_ids) != 1:
        errors.append(f"expected one stable reviewer_id, found {sorted(reviewer_ids)}")

    resolved_fields = list(adjudication[0]) + [
        "confirmation_status", "independent_reviewer", "independent_confidence",
        "independent_notes", "source_decision", "source_label", "source_start_s",
        "source_end_s", "benchmark_lock_status",
    ]
    resolved_rows: list[dict[str, str]] = []
    for original in adjudication:
        out = dict(original)
        confirmation = completed_by_id.get(original["interval_id"])
        out["source_decision"] = original["decision"]
        out["source_label"] = original["reviewed_label"]
        out["source_start_s"] = original["start_s"]
        out["source_end_s"] = original["end_s"]
        out["benchmark_lock_status"] = "pending_continuous_timeline_audit"
        if confirmation:
            changed = (
                confirmation["independent_decision"] != original["decision"]
                or confirmation["independent_label"] != original["reviewed_label"]
                or confirmation["independent_start_s"] != original["start_s"]
                or confirmation["independent_end_s"] != original["end_s"]
            )
            out["decision"] = confirmation["independent_decision"]
            out["reviewed_label"] = confirmation["independent_label"]
            out["start_s"] = confirmation["independent_start_s"]
            out["end_s"] = confirmation["independent_end_s"]
            out["confidence"] = confirmation["confidence"]
            out["review_status"] = "adjudicated"
            out["reviewer"] = f"{original['reviewer']} + independent:{confirmation['reviewer_id']}"
            out["needs_second_review"] = "false"
            out["confirmation_status"] = "boundary_corrected" if changed else "confirmed"
            out["independent_reviewer"] = confirmation["reviewer_id"]
            out["independent_confidence"] = confirmation["confidence"]
            out["independent_notes"] = confirmation["notes"]
        else:
            out["confirmation_status"] = "not_selected_high_confidence"
            out["independent_reviewer"] = ""
            out["independent_confidence"] = ""
            out["independent_notes"] = ""
            if original["decision"].startswith("accept") and original["confidence"] == "high":
                out["needs_second_review"] = "false"
        out["benchmark_ready"] = "false"
        resolved_rows.append(out)

    args.resolved.parent.mkdir(parents=True, exist_ok=True)
    with args.resolved.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=resolved_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(resolved_rows)

    unresolved = sum(
        row["decision"].startswith("accept") and row["needs_second_review"] == "true"
        for row in resolved_rows
    )
    n = len(queue)
    report = {
        "status": "confirmation_pass_benchmark_unlocked" if not errors and not unresolved else "failed",
        "errors": errors,
        "warnings": warnings,
        "benchmark_locked": False,
        "lock_blockers": [
            "continuous reviewed timelines and strict timeline audit are not complete",
            "first frozen benchmark evaluation has not run",
        ],
        "confirmation_complete": not errors,
        "independent_reviewer_ids": sorted(reviewer_ids),
        "counts": {
            "adjudication_rows": len(adjudication),
            "confirmation_rows": len(completed),
            "confirmed_without_change": n - len(corrected_rows),
            "corrected_rows": len(corrected_rows),
            "unresolved_retained_second_reviews": unresolved,
        },
        "agreement": {
            "decision": decision_agreements / n if n else None,
            "label": label_agreements / n if n else None,
            "exact_boundary": exact_boundary_agreements / n if n else None,
        },
        "corrections": corrected_rows,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors or unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
