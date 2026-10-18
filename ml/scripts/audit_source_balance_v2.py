#!/usr/bin/env python3
"""Fail closed on source-balance-v2 intake and adjudication records."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "ml/data/source_balance_v2"
CANDIDATES = V2 / "candidates.csv"
ADJUDICATION = V2 / "adjudication/second_pass_codex_review.csv"
RESERVED = (
    ROOT / "ml/data/source_balance_v1/candidates.csv",
    ROOT / "ml/data/youtube_creator_benchmark_v1/candidates.csv",
    ROOT / "ml/data/youtube_creator_benchmark_v1/excluded_source_inventory.csv",
    ROOT / "ml/data/youtube_mixed_workouts_v1/manifest.csv",
    ROOT / "ml/data/youtube_long_workouts_v2/candidates.csv",
)
TARGETS = {"dumbbell_row", "sit_up", "lat_pulldown", "pull_up"}
TRUE_FALSE = {"true", "false"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def identity(value: str) -> str:
    return "".join(char for char in value.casefold() if char.isalnum())


def require_unique(values: list[str], label: str) -> None:
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    assert not duplicates, f"Duplicate {label}: {duplicates}"


def parse_intervals(value: str) -> list[tuple[float, float]]:
    if not value:
        return []
    intervals = []
    for item in value.split("|"):
        start_text, end_text = item.split("-", 1)
        intervals.append((float(start_text), float(end_text)))
    return intervals


def audit_candidates() -> None:
    candidates = read_rows(CANDIDATES)
    assert candidates, "Candidate manifest is empty"
    require_unique([row["video_id"] for row in candidates], "candidate video ID")
    require_unique([row["channel_id"] for row in candidates], "candidate channel ID")
    require_unique([identity(row["creator"]) for row in candidates], "candidate creator")

    reserved_rows = [row for path in RESERVED for row in read_rows(path)]
    reserved_ids = {row.get("video_id", "") for row in reserved_rows}
    reserved_channels = {row.get("channel_id", "") for row in reserved_rows} - {""}
    reserved_creators = {
        identity(row.get("creator", "")) for row in reserved_rows if row.get("creator")
    }

    creators_by_class: dict[str, set[str]] = {target: set() for target in TARGETS}
    for row in candidates:
        video_id = row["video_id"]
        assert row["target_class"] in TARGETS, (video_id, row["target_class"])
        assert row["status"] == "metadata_only", video_id
        assert row["training_allowed"].casefold() == "false", video_id
        assert row["license_status"] == "unreviewed", video_id
        assert video_id not in reserved_ids, f"Reserved video ID: {video_id}"
        assert row["channel_id"] not in reserved_channels, (
            f"Reserved channel ID: {row['channel_id']}"
        )
        assert identity(row["creator"]) not in reserved_creators, (
            f"Reserved creator: {row['creator']}"
        )
        assert row["source_url"].endswith(video_id), video_id
        assert float(row["duration_s"]) > 0, video_id
        creators_by_class[row["target_class"]].add(row["channel_id"])

    for target, creators in creators_by_class.items():
        assert len(creators) >= 2, f"{target} has only {len(creators)} candidate creators"

    coverage = ", ".join(
        f"{target}={len(creators_by_class[target])}" for target in sorted(TARGETS)
    )
    print(f"Candidate audit passed: {len(candidates)} videos; {coverage}.")


def audit_adjudication() -> None:
    rows = read_rows(ADJUDICATION)
    assert rows, "Adjudication record is empty"
    require_unique([row["review_id"] for row in rows], "adjudication review ID")
    allowed_decisions = {
        "retain_pending_independent_review",
        "reject_whole_interval",
        "split_pending_independent_review",
    }

    for row in rows:
        review_id = row["review_id"]
        assert row["target_class"] in TARGETS, review_id
        assert row["decision"] in allowed_decisions, review_id
        assert row["independent_human_review_complete"].casefold() in TRUE_FALSE, review_id
        assert row["training_allowed"].casefold() in TRUE_FALSE, review_id
        assert row["independent_human_review_complete"].casefold() == "false", review_id
        assert row["training_allowed"].casefold() == "false", review_id

        clip_start = float(row["source_clip_start_s"])
        clip_end = float(row["source_clip_end_s"])
        assert clip_start < clip_end, review_id
        intervals = parse_intervals(row["proposed_intervals_s"])
        if row["decision"] == "reject_whole_interval":
            assert not intervals, f"Rejected row has proposed intervals: {review_id}"
        else:
            assert intervals, f"Non-rejected row lacks proposed intervals: {review_id}"
        prior_end = clip_start
        for start, end in intervals:
            assert clip_start <= start < end <= clip_end, (review_id, start, end)
            assert start >= prior_end, f"Overlapping proposed intervals: {review_id}"
            prior_end = end

    print(
        f"Adjudication audit passed: {len(rows)} quarantine clips; "
        "independent review incomplete and training disabled."
    )


def main() -> None:
    audit_candidates()
    audit_adjudication()


if __name__ == "__main__":
    main()
