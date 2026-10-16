#!/usr/bin/env python3
"""Audit source/class concentration and protect reserved creator identities."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "ml/artifacts/v6c/model/split_assignments.csv"
LONG_V2 = ROOT / "ml/artifacts/v6c_longv2_data_retrain/model/split_assignments.csv"
CANDIDATES = ROOT / "ml/data/source_balance_v1/candidates.csv"
EXISTING = ROOT / "ml/data/youtube_creator_benchmark_v1/excluded_source_inventory.csv"
LOCKED = ROOT / "ml/data/youtube_creator_benchmark_v1/candidates.csv"
MIXED = ROOT / "ml/data/youtube_mixed_workouts_v1/manifest.csv"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def identity(value: str) -> str:
    return "".join(char for char in value.casefold() if char.isalnum())


def support(path: Path) -> dict[str, dict[str, tuple[int, int]]]:
    counts: dict[str, dict[str, list]] = defaultdict(
        lambda: defaultdict(lambda: [0, set()])
    )
    for row in rows(path):
        if row["split"] != "train" or row["active_class"] == "unknown":
            continue
        cell = counts[row["active_class"]][row["source_dataset"]]
        cell[0] += 1
        cell[1].add(row["group_id"])
    return {
        label: {source: (count, len(groups)) for source, (count, groups) in by_source.items()}
        for label, by_source in counts.items()
    }


def main() -> None:
    baseline, long_v2 = support(BASELINE), support(LONG_V2)
    print("class,baseline_sources,longv2_sources,baseline_windows,longv2_windows")
    for label in sorted(baseline):
        old, new = baseline[label], long_v2[label]
        print(f"{label},{len(old)},{len(new)},{sum(v[0] for v in old.values())},"
              f"{sum(v[0] for v in new.values())}")

    reserved = rows(EXISTING) + rows(LOCKED) + rows(MIXED)
    reserved_ids = {row["video_id"] for row in reserved}
    reserved_creators = {identity(row.get("creator", "")) for row in reserved}
    candidates = rows(CANDIDATES)
    candidate_ids = [row["video_id"] for row in candidates]
    candidate_creators = [identity(row["creator"]) for row in candidates]
    assert len(candidate_ids) == len(set(candidate_ids)), "Duplicate candidate video ID"
    assert len(candidate_creators) == len(set(candidate_creators)), "Duplicate candidate creator"
    for row in candidates:
        assert row["video_id"] not in reserved_ids, row["video_id"]
        assert identity(row["creator"]) not in reserved_creators, row["creator"]
        assert row["status"] == "metadata_only", row["video_id"]
        assert row["training_allowed"].lower() == "false", row["video_id"]
    print(f"Candidate identity check passed: {len(candidates)} distinct new creators; "
          "all remain excluded from training.")


if __name__ == "__main__":
    main()
