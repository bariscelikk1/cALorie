#!/usr/bin/env python3
"""Build the locked region-classification benchmark from resolved adjudication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


EXPECTED_LABELS = {
    "bench_press", "bicep_curl", "deadlift", "dumbbell_row", "jumping_jack",
    "lat_pulldown", "lateral_raise", "lunge", "pull_up", "push_up",
    "shoulder_press", "sit_up", "squat", "tricep_extension", "unknown",
}
EXPECTED_ARCHIVES = {
    "calorie_creator_benchmark_v1_evidence.zip":
        "3c9930fc3086b68240082668648722836c8959c373a58268347788d7ab24b3c4",
    "calorie_creator_benchmark_v1_gapfill_evidence.zip":
        "4d0f3efed5216f0f46e96478c9777fc652814a346046f5866309357efc38e050",
    "calorie_creator_benchmark_dense_review_evidence.zip":
        "5f2f28a7a89177d1e6675d742bf60c9a4851f657baee89d710694716022e9301",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolved", required=True, type=Path)
    parser.add_argument("--confirmation", required=True, type=Path)
    parser.add_argument("--manifest", required=True, action="append", type=Path)
    parser.add_argument("--archive", action="append", default=[], type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    resolved = read_csv(args.resolved)
    manifests = [row for path in args.manifest for row in read_csv(path)]
    sources = {row["video_id"]: row for row in manifests if row["status"] == "ok"}
    retained = [row for row in resolved if row["decision"].startswith("accept")]

    ids = [row["interval_id"] for row in retained]
    if len(ids) != len(set(ids)):
        errors.append("retained regions contain duplicate interval IDs")
    if len(retained) != 36:
        errors.append(f"expected 36 retained regions, found {len(retained)}")

    output_rows: list[dict[str, str]] = []
    by_video: dict[str, list[tuple[float, float, str]]] = defaultdict(list)
    label_counts: Counter[str] = Counter()
    creator_counts: Counter[str] = Counter()
    duration_by_label: Counter[str] = Counter()

    for row in retained:
        interval_id = row["interval_id"]
        video_id = row["video_id"]
        label = row["reviewed_label"]
        if video_id not in sources:
            errors.append(f"{interval_id}: no verified continuous source manifest")
            continue
        if label not in EXPECTED_LABELS:
            errors.append(f"{interval_id}: unsupported final label {label!r}")
        if row["predictions_used_for_decision"] != "false":
            errors.append(f"{interval_id}: label decision consulted model predictions")
        if row["needs_second_review"] != "false":
            errors.append(f"{interval_id}: required second review is unresolved")
        if row["review_status"] not in {"reviewed", "adjudicated"}:
            errors.append(f"{interval_id}: invalid final review status {row['review_status']!r}")
        start, end = float(row["start_s"]), float(row["end_s"])
        duration = float(sources[video_id]["duration_s"])
        if not 0 <= start < end <= duration:
            errors.append(f"{interval_id}: boundary [{start}, {end}) exceeds source duration {duration}")
        by_video[video_id].append((start, end, interval_id))
        label_counts[label] += 1
        creator_counts[row["creator"]] += 1
        duration_by_label[label] += end - start
        output_rows.append({
            "region_id": interval_id,
            "video_id": video_id,
            "creator": row["creator"],
            "group_id": sources[video_id]["group_id"],
            "label": label,
            "start_s": f"{start:g}",
            "end_s": f"{end:g}",
            "duration_s": f"{end - start:g}",
            "segment_type": row["segment_type"],
            "split": "locked_external_test",
            "use_for_training": "false",
            "calibration_allowed": "false",
            "threshold_selection_allowed": "false",
            "predictions_used_for_labeling": "false",
            "review_status": row["review_status"],
            "reviewer": row["reviewer"],
            "confirmation_status": row["confirmation_status"],
            "boundary_precision_s": row["boundary_precision_s"],
            "lock_status": "locked_region_classification_v1",
            "benchmark_scope": "region_classification_only",
            "notes": row["notes"],
        })

    for video_id, intervals in by_video.items():
        intervals.sort()
        for previous, current in zip(intervals, intervals[1:]):
            if current[0] < previous[1]:
                errors.append(
                    f"{video_id}: overlap {previous[2]} [{previous[0]}, {previous[1]}) "
                    f"with {current[2]} [{current[0]}, {current[1]})"
                )

    missing_labels = sorted(EXPECTED_LABELS - set(label_counts))
    if missing_labels:
        errors.append(f"missing final label coverage: {missing_labels}")
    if len(by_video) != 6:
        errors.append(f"expected six retained creator videos, found {len(by_video)}")

    archive_checks = []
    provided = {path.name: path for path in args.archive}
    for name, expected in EXPECTED_ARCHIVES.items():
        path = provided.get(name)
        if not path:
            errors.append(f"missing local archive for lock verification: {name}")
            archive_checks.append({"archive": name, "expected_sha256": expected, "status": "missing"})
            continue
        actual = sha256(path)
        status = "verified" if actual == expected else "mismatch"
        if status != "verified":
            errors.append(f"archive hash mismatch: {name}")
        archive_checks.append({
            "archive": name, "expected_sha256": expected, "actual_sha256": actual,
            "status": status,
        })

    output_rows.sort(key=lambda row: (row["video_id"], float(row["start_s"]), row["region_id"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0]) if output_rows else []
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    report = {
        "status": "locked_region_classification_v1" if not errors else "failed",
        "region_benchmark_locked": not errors,
        "full_timeline_benchmark_locked": False,
        "full_timeline_blocker": (
            "unreviewed gaps in the six complete videos are not continuous timeline ground truth"
        ),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "regions": len(output_rows),
            "creator_videos": len(by_video),
            "labels_including_unknown": len(label_counts),
            "supported_labels": len(set(label_counts) - {"unknown"}),
        },
        "regions_by_label": dict(sorted(label_counts.items())),
        "regions_by_creator": dict(sorted(creator_counts.items())),
        "duration_s_by_label": {
            label: round(value, 3) for label, value in sorted(duration_by_label.items())
        },
        "archive_checks": archive_checks,
        "input_sha256": {
            "resolved_region_adjudication": sha256(args.resolved),
            "independent_confirmation": sha256(args.confirmation),
            **{f"manifest_{index + 1}": sha256(path) for index, path in enumerate(args.manifest)},
        },
        "output_sha256": sha256(args.output),
        "prohibitions": {
            "training": True,
            "calibration": True,
            "threshold_selection": True,
            "prediction_guided_relabeling": True,
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
