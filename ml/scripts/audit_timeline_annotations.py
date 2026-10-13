#!/usr/bin/env python3
"""Audit cALorie long-video timeline annotations before landmark extraction."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


REQUIRED = {
    "video_id", "video_file", "start_s", "end_s", "segment_type",
    "fine_label", "current_tcn_label", "split", "use_for_training",
    "annotation_source", "boundary_precision_s", "notes",
}
OPTIONAL_QA = {
    "annotation_confidence", "review_status", "reviewer", "needs_second_review"
}
NON_EXERCISE = {"intro", "outro", "transition", "rest", "cooldown"}
CONFIDENCE = {"high", "medium", "low"}
REVIEW_STATUS = {"draft", "reviewed", "adjudicated", "rejected"}
BOOLS = {"true", "false"}


def read_rows(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        return list(reader), set(reader.fieldnames or [])


def load_labels(path: Path) -> set[str]:
    config = json.loads(path.read_text(encoding="utf-8"))
    # Retired labels remain valid in archived annotations so historical
    # experiments can still be audited. Dataset builders decide whether a
    # retired label is an active target or must be remapped to ``unknown``.
    return (
        set(config["exercises"])
        | set(config["non_exercise_classes"])
        | set(config.get("retired_exercises", []))
    )


def as_float(value: str, location: str, errors: list[str]) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        errors.append(f"{location}: expected a number, got {value!r}")
        return None


def audit_file(path: Path, valid_labels: set[str]) -> dict:
    rows, columns = read_rows(path)
    errors: list[str] = []
    warnings: list[str] = []
    missing = sorted(REQUIRED - columns)
    if missing:
        return {"file": str(path), "rows": len(rows), "errors": [
            f"missing required columns: {', '.join(missing)}"
        ], "warnings": [], "labels": {}, "duration_s": 0.0}

    missing_qa = sorted(OPTIONAL_QA - columns)
    if missing_qa:
        warnings.append(
            "legacy schema lacks QA columns: " + ", ".join(missing_qa)
        )

    video_ids = {row["video_id"].strip() for row in rows}
    video_files = {row["video_file"].strip() for row in rows}
    if len(video_ids) != 1:
        errors.append(f"expected one video_id, found {sorted(video_ids)}")
    if len(video_files) != 1:
        errors.append(f"expected one video_file, found {sorted(video_files)}")

    previous_end: float | None = None
    label_counts: Counter[str] = Counter()
    duration = 0.0
    for index, row in enumerate(rows, start=2):
        where = f"{path.name}:{index}"
        start = as_float(row["start_s"], where, errors)
        end = as_float(row["end_s"], where, errors)
        precision = as_float(row["boundary_precision_s"], where, errors)
        if start is None or end is None:
            continue
        if start < 0 or end <= start:
            errors.append(f"{where}: expected 0 <= start_s < end_s")
        if previous_end is not None:
            delta = start - previous_end
            if delta < -1e-6:
                errors.append(f"{where}: overlaps previous row by {-delta:.3f}s")
            elif delta > 0.05:
                errors.append(f"{where}: uncovered timeline gap of {delta:.3f}s")
        previous_end = end
        duration = max(duration, end)

        segment = row["segment_type"].strip()
        label = row["current_tcn_label"].strip()
        label_counts[label] += 1
        if segment not in NON_EXERCISE | {"exercise"}:
            errors.append(f"{where}: invalid segment_type {segment!r}")
        if label not in valid_labels:
            errors.append(f"{where}: invalid canonical label {label!r}")
        if segment in NON_EXERCISE and label != "unknown":
            errors.append(f"{where}: {segment} must map to unknown")
        if not row["fine_label"].strip():
            errors.append(f"{where}: empty fine_label")
        if row["use_for_training"].strip().lower() not in BOOLS:
            errors.append(f"{where}: use_for_training must be true or false")
        if not row["annotation_source"].strip():
            errors.append(f"{where}: annotation_source is required")
        if precision is not None and precision <= 0:
            errors.append(f"{where}: boundary_precision_s must be positive")
        if precision is not None and precision > 2:
            warnings.append(f"{where}: boundary precision is coarse ({precision:g}s)")

        notes = row["notes"].strip().lower()
        training = row["use_for_training"].strip().lower() == "true"
        if training and ("draft" in notes or "review required" in notes):
            warnings.append(f"{where}: training row is described as draft/unreviewed")

        if not missing_qa:
            confidence = row["annotation_confidence"].strip().lower()
            review = row["review_status"].strip().lower()
            second = row["needs_second_review"].strip().lower()
            if confidence not in CONFIDENCE:
                errors.append(f"{where}: invalid annotation_confidence {confidence!r}")
            if review not in REVIEW_STATUS:
                errors.append(f"{where}: invalid review_status {review!r}")
            if second not in BOOLS:
                errors.append(f"{where}: needs_second_review must be true or false")
            if training and review in {"draft", "rejected"}:
                errors.append(f"{where}: draft/rejected row cannot be used for training")
            if confidence == "low" and second != "true" and review != "adjudicated":
                errors.append(f"{where}: low-confidence row needs second review")
            if not row["reviewer"].strip():
                errors.append(f"{where}: reviewer is required in v2 schema")

    return {
        "file": str(path), "rows": len(rows), "duration_s": duration,
        "labels": dict(sorted(label_counts.items())),
        "errors": errors, "warnings": warnings,
    }


def label_at(rows: list[dict[str, str]], time_s: float) -> str | None:
    for row in rows:
        if float(row["start_s"]) <= time_s < float(row["end_s"]):
            return row["current_tcn_label"].strip()
    return None


def compare_roots(first: Path, second: Path, step_s: float = 0.5) -> dict:
    agreements = 0
    compared = 0
    missing_files: list[str] = []
    for first_path in sorted(first.glob("*.csv")):
        second_path = second / first_path.name
        if not second_path.exists():
            missing_files.append(first_path.name)
            continue
        a, _ = read_rows(first_path)
        b, _ = read_rows(second_path)
        if not a or not b:
            continue
        end = min(float(a[-1]["end_s"]), float(b[-1]["end_s"]))
        point = step_s / 2
        while point < end:
            left, right = label_at(a, point), label_at(b, point)
            if left is not None and right is not None:
                compared += 1
                agreements += left == right
            point += step_s
    return {
        "sample_step_s": step_s,
        "compared_points": compared,
        "canonical_label_agreement": agreements / compared if compared else None,
        "missing_second_review_files": missing_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Directory containing timeline CSV files")
    parser.add_argument("--second-root", type=Path, help="Independent second-review CSV directory")
    parser.add_argument("--report", type=Path, help="Optional JSON report path")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    parser.add_argument(
        "--classes", type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "classes.json",
    )
    args = parser.parse_args()
    valid_labels = load_labels(args.classes)
    files = sorted(args.root.glob("*.csv"))
    results = [audit_file(path, valid_labels) for path in files]
    report = {
        "files": len(files),
        "rows": sum(item["rows"] for item in results),
        "errors": sum(len(item["errors"]) for item in results),
        "warnings": sum(len(item["warnings"]) for item in results),
        "results": results,
    }
    if args.second_root:
        report["agreement"] = compare_roots(args.root, args.second_root)
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    if report["errors"] or (args.strict and report["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
