from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_COLUMNS = {
    "clip_id",
    "video_path",
    "source_dataset",
    "source_video_id",
    "person_id",
    "exercise",
    "camera_view",
    "repetition_count",
    "start_seconds",
    "end_seconds",
    "split",
    "license",
    "review_status",
    "notes",
}
VALID_SPLITS = {"train", "validation", "test"}
VALID_REVIEW_STATUSES = {"pending", "approved", "rejected"}


def load_classes(path: Path) -> tuple[set[str], set[str]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    exercises = set(config["exercises"])
    labels = exercises | set(config["non_exercise_classes"])
    return labels, set(config["static_exercises"])


def validate(manifest_path: Path, classes_path: Path) -> list[str]:
    labels, static_exercises = load_classes(classes_path)
    errors: list[str] = []

    with manifest_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        columns = set(reader.fieldnames or [])
        missing_columns = sorted(REQUIRED_COLUMNS - columns)
        if missing_columns:
            return [f"Missing columns: {', '.join(missing_columns)}"]
        rows = list(reader)

    seen_clip_ids: set[str] = set()
    person_splits: dict[str, set[str]] = defaultdict(set)
    source_video_splits: dict[tuple[str, str], set[str]] = defaultdict(set)
    class_counts: Counter[str] = Counter()

    for line_number, row in enumerate(rows, start=2):
        prefix = f"line {line_number}"
        clip_id = row["clip_id"].strip()
        if not clip_id:
            errors.append(f"{prefix}: empty clip_id")
        elif clip_id in seen_clip_ids:
            errors.append(f"{prefix}: duplicate clip_id {clip_id!r}")
        seen_clip_ids.add(clip_id)

        exercise = row["exercise"].strip()
        if exercise not in labels:
            errors.append(f"{prefix}: invalid exercise {exercise!r}")
        else:
            class_counts[exercise] += 1

        split = row["split"].strip()
        if split not in VALID_SPLITS:
            errors.append(f"{prefix}: invalid split {split!r}")

        review_status = row["review_status"].strip()
        if review_status not in VALID_REVIEW_STATUSES:
            errors.append(f"{prefix}: invalid review_status {review_status!r}")

        person_id = row["person_id"].strip()
        if not person_id:
            errors.append(f"{prefix}: empty person_id")
        elif split in VALID_SPLITS:
            person_splits[person_id].add(split)

        source_dataset = row["source_dataset"].strip()
        source_video_id = row["source_video_id"].strip()
        if not source_dataset or not source_video_id:
            errors.append(f"{prefix}: source_dataset and source_video_id are required")
        elif split in VALID_SPLITS:
            source_video_splits[(source_dataset, source_video_id)].add(split)

        try:
            start = float(row["start_seconds"])
            end = float(row["end_seconds"])
            if start < 0 or end <= start:
                errors.append(f"{prefix}: expected 0 <= start_seconds < end_seconds")
        except ValueError:
            errors.append(f"{prefix}: start_seconds and end_seconds must be numbers")

        repetitions = row["repetition_count"].strip()
        if exercise in static_exercises or exercise == "unknown":
            if repetitions:
                errors.append(f"{prefix}: {exercise} must not have a repetition_count")
        else:
            try:
                if int(repetitions) < 1:
                    raise ValueError
            except ValueError:
                errors.append(f"{prefix}: dynamic exercise requires a positive integer repetition_count")

        if not row["license"].strip():
            errors.append(f"{prefix}: license/access record is required")

    for person_id, splits in sorted(person_splits.items()):
        if len(splits) > 1:
            errors.append(f"person leakage: {person_id!r} appears in {sorted(splits)}")

    for source_key, splits in sorted(source_video_splits.items()):
        if len(splits) > 1:
            errors.append(f"source-video leakage: {source_key!r} appears in {sorted(splits)}")

    if not rows:
        print("Manifest structure is valid but contains no samples yet.")
    else:
        print(f"Validated {len(rows)} rows across {len(class_counts)} labels.")
        for label, count in sorted(class_counts.items()):
            print(f"  {label}: {count}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the cALorie ML dataset manifest.")
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--classes",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "config" / "classes.json",
    )
    args = parser.parse_args()
    errors = validate(args.manifest, args.classes)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Manifest validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
