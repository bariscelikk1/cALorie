#!/usr/bin/env python3
"""Fail closed on source-balance-v2 intake and adjudication records."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "ml/data/source_balance_v2"
CANDIDATES = V2 / "candidates.csv"
SUPPLEMENTAL = V2 / "supplemental_candidates.csv"
ADJUDICATION = V2 / "adjudication/second_pass_codex_review.csv"
SCREENING = V2 / "screening_review.csv"
DENSE_TARGETS = V2 / "dense_review_targets.csv"
DENSE_VISUAL_REVIEW = V2 / "dense_visual_review.csv"
REPLACEMENT_SCREENING = V2 / "replacement_screening_review.csv"
REPLACEMENT_DENSE_REVIEW = V2 / "replacement_dense_visual_review.csv"
POSE_AUDIT_TARGETS = V2 / "pose_audit_targets.csv"
POSE_VISUAL_TRIAGE = V2 / "pose_visual_triage.csv"
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
    supplemental = read_rows(SUPPLEMENTAL)
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

    all_intake = candidates + supplemental
    require_unique([row["video_id"] for row in all_intake], "combined intake video ID")
    require_unique([row["channel_id"] for row in all_intake], "combined intake channel ID")
    require_unique(
        [identity(row["creator"]) for row in all_intake], "combined intake creator"
    )
    for row in supplemental:
        video_id = row["video_id"]
        assert row["target_class"] in {"sit_up", "lat_pulldown"}, video_id
        assert row["role"] == "replacement_train_candidate", video_id
        assert row["status"] == "metadata_only", video_id
        assert row["license_status"] == "unreviewed", video_id
        assert row["training_allowed"].casefold() == "false", video_id
        assert video_id not in reserved_ids, f"Reserved supplemental video ID: {video_id}"
        assert row["channel_id"] not in reserved_channels, (
            f"Reserved supplemental channel ID: {row['channel_id']}"
        )
        assert identity(row["creator"]) not in reserved_creators, (
            f"Reserved supplemental creator: {row['creator']}"
        )
        assert row["source_url"].endswith(video_id), video_id
        assert float(row["duration_s"]) > 0, video_id

    coverage = ", ".join(
        f"{target}={len(creators_by_class[target])}" for target in sorted(TARGETS)
    )
    print(
        f"Candidate audit passed: {len(candidates)} initial + {len(supplemental)} "
        f"replacement videos; {coverage}."
    )


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


def audit_screening() -> None:
    candidates = read_rows(CANDIDATES)
    candidate_by_id = {row["video_id"]: row for row in candidates}
    reviews = read_rows(SCREENING)
    require_unique([row["video_id"] for row in reviews], "screening video ID")
    assert set(candidate_by_id) == {row["video_id"] for row in reviews}, (
        "Screening rows must cover the candidate manifest exactly"
    )
    allowed_decisions = {
        "advance_dense_review",
        "hold_noncanonical_and_identity_alias",
        "reject_pose_framing",
        "hold_camera_actor_complexity",
        "hold_partial_body",
    }
    advanced_groups: dict[str, set[str]] = {target: set() for target in TARGETS}
    review_by_id = {}
    for row in reviews:
        video_id = row["video_id"]
        review_by_id[video_id] = row
        assert row["target_class"] == candidate_by_id[video_id]["target_class"]
        assert row["screening_decision"] in allowed_decisions, video_id
        assert row["independent_human_review_complete"].casefold() == "false", video_id
        assert row["training_allowed"].casefold() == "false", video_id
        assert row["person_identity_group"], video_id
        if row["screening_decision"] == "advance_dense_review":
            assert row["candidate_intervals_s"], video_id
            advanced_groups[row["target_class"]].add(row["person_identity_group"])
        else:
            assert not row["candidate_intervals_s"], video_id

    # Distinct channels can still feature the same person. Preserve this known alias.
    assert review_by_id["8PwoytUU06g"]["person_identity_group"] == review_by_id[
        "XgI_p8bKg78"
    ]["person_identity_group"]

    targets = read_rows(DENSE_TARGETS)
    require_unique([row["review_id"] for row in targets], "dense review ID")
    duration_by_id = {
        row["video_id"]: float(row["duration_s"]) for row in candidates
    }
    for row in targets:
        video_id = row["video_id"]
        assert video_id in review_by_id, video_id
        assert review_by_id[video_id]["screening_decision"] == "advance_dense_review", video_id
        assert row["target_class"] == review_by_id[video_id]["target_class"], video_id
        assert row["training_allowed"].casefold() == "false", row["review_id"]
        start, end = float(row["start_s"]), float(row["end_s"])
        assert 0 <= start < end <= duration_by_id[video_id] + 1.0, row["review_id"]

    coverage = ", ".join(
        f"{target}={len(advanced_groups[target])}" for target in sorted(TARGETS)
    )
    print(
        f"Screening audit passed: {len(reviews)} videos, {len(targets)} dense targets; "
        f"advanced person groups {coverage}."
    )


def audit_dense_and_replacements() -> None:
    targets = read_rows(DENSE_TARGETS)
    target_by_id = {row["review_id"]: row for row in targets}
    dense = read_rows(DENSE_VISUAL_REVIEW)
    require_unique([row["review_id"] for row in dense], "dense visual review ID")
    assert set(target_by_id) == {row["review_id"] for row in dense}, (
        "Dense visual reviews must cover the target manifest exactly"
    )
    dense_decisions = {
        "advance_pose_audit",
        "hold_noncanonical_variant",
        "reject_noncanonical_variant",
        "reject_target_mismatch",
        "unavailable_retry_required",
    }
    advanced_intervals = 0
    for row in dense:
        review_id = row["review_id"]
        target = target_by_id[review_id]
        assert row["video_id"] == target["video_id"], review_id
        assert row["target_class"] == target["target_class"], review_id
        assert row["review_decision"] in dense_decisions, review_id
        assert row["independent_human_review_complete"].casefold() == "false", review_id
        assert row["training_allowed"].casefold() == "false", review_id
        intervals = parse_intervals(row["proposed_intervals_s"])
        if row["review_decision"] == "advance_pose_audit":
            assert intervals, f"Advanced dense review has no intervals: {review_id}"
            advanced_intervals += len(intervals)
        else:
            assert not intervals, f"Non-advanced dense review has intervals: {review_id}"
        prior_end = float(target["start_s"])
        for start, end in intervals:
            assert float(target["start_s"]) <= start < end <= float(target["end_s"]), (
                review_id,
                start,
                end,
            )
            assert start >= prior_end, f"Overlapping dense intervals: {review_id}"
            prior_end = end

    supplemental = read_rows(SUPPLEMENTAL)
    supplemental_by_id = {row["video_id"]: row for row in supplemental}
    replacements = read_rows(REPLACEMENT_SCREENING)
    require_unique([row["video_id"] for row in replacements], "replacement review video ID")
    assert set(supplemental_by_id) == {row["video_id"] for row in replacements}, (
        "Replacement reviews must cover the supplemental manifest exactly"
    )
    replacement_decisions = {
        "advance_dense_review",
        "hold_pose_framing",
        "reject_target_mismatch",
    }
    advanced_replacements = 0
    for row in replacements:
        video_id = row["video_id"]
        source = supplemental_by_id[video_id]
        assert row["creator"] == source["creator"], video_id
        assert row["target_class"] == source["target_class"], video_id
        assert row["screening_decision"] in replacement_decisions, video_id
        assert row["independent_human_review_complete"].casefold() == "false", video_id
        assert row["training_allowed"].casefold() == "false", video_id
        intervals = parse_intervals(row["candidate_intervals_s"])
        if row["screening_decision"] == "advance_dense_review":
            assert intervals, f"Advanced replacement has no locator: {video_id}"
            advanced_replacements += 1
        else:
            assert not intervals, f"Held/rejected replacement has a locator: {video_id}"
        prior_end = 0.0
        for start, end in intervals:
            assert 0 <= start < end <= float(source["duration_s"]) + 1.0, (
                video_id,
                start,
                end,
            )
            assert start >= prior_end, f"Overlapping replacement intervals: {video_id}"
            prior_end = end

    print(
        f"30B review audit passed: {len(dense)} dense regions with "
        f"{advanced_intervals} proposed pose intervals; {advanced_replacements}/"
        f"{len(replacements)} replacements advanced; training disabled."
    )


def audit_replacement_dense_and_pose_queue() -> None:
    candidates = read_rows(CANDIDATES)
    supplemental = read_rows(SUPPLEMENTAL)
    source_by_id = {row["video_id"]: row for row in candidates + supplemental}
    replacement_screening = read_rows(REPLACEMENT_SCREENING)
    advanced_replacement_ids = {
        row["video_id"]
        for row in replacement_screening
        if row["screening_decision"] == "advance_dense_review"
    }
    expected_review_ids = {
        *(f"replacement_{video_id}" for video_id in advanced_replacement_ids),
        "max_row_retry",
    }
    reviews = read_rows(REPLACEMENT_DENSE_REVIEW)
    require_unique([row["review_id"] for row in reviews], "30C review ID")
    assert {row["review_id"] for row in reviews} == expected_review_ids
    allowed_decisions = {
        "advance_pose_audit",
        "reject_pose_framing",
        "reject_camera_pose_inconsistency",
    }
    proposed_by_review: dict[str, list[tuple[float, float]]] = {}
    for row in reviews:
        review_id = row["review_id"]
        video_id = row["video_id"]
        assert video_id in source_by_id, video_id
        assert row["target_class"] == source_by_id[video_id]["target_class"], review_id
        assert row["review_decision"] in allowed_decisions, review_id
        assert row["independent_human_review_complete"].casefold() == "false", review_id
        assert row["training_allowed"].casefold() == "false", review_id
        intervals = parse_intervals(row["proposed_intervals_s"])
        if row["review_decision"] == "advance_pose_audit":
            assert intervals, f"Advanced 30C review has no interval: {review_id}"
            proposed_by_review[review_id] = intervals
        else:
            assert not intervals, f"Rejected 30C review has an interval: {review_id}"
        prior_end = 0.0
        for start, end in intervals:
            assert 0 <= start < end <= float(source_by_id[video_id]["duration_s"]) + 1.0
            assert start >= prior_end, f"Overlapping 30C intervals: {review_id}"
            prior_end = end

    dense_reviews = read_rows(DENSE_VISUAL_REVIEW)
    for row in dense_reviews:
        if row["review_decision"] == "advance_pose_audit":
            proposed_by_review[row["review_id"]] = parse_intervals(
                row["proposed_intervals_s"]
            )

    pose_targets = read_rows(POSE_AUDIT_TARGETS)
    require_unique([row["window_id"] for row in pose_targets], "pose-audit window ID")
    actual: dict[str, list[tuple[float, float]]] = {}
    for row in pose_targets:
        window_id = row["window_id"]
        review_id = row["source_review_id"]
        assert review_id in proposed_by_review, window_id
        assert row["video_id"] in source_by_id, window_id
        assert row["target_class"] == source_by_id[row["video_id"]]["target_class"], window_id
        assert row["independent_human_review_complete"].casefold() == "false", window_id
        assert row["training_allowed"].casefold() == "false", window_id
        start, end = float(row["start_s"]), float(row["end_s"])
        assert start < end, window_id
        actual.setdefault(review_id, []).append((start, end))

    assert set(actual) == set(proposed_by_review), (
        "Pose queue must cover every advanced 30B/30C review exactly"
    )
    for review_id, expected in proposed_by_review.items():
        assert actual[review_id] == expected, f"Pose queue interval mismatch: {review_id}"

    print(
        f"30C review audit passed: {len(reviews)} dense targets; "
        f"{len(pose_targets)} pose windows queued; training disabled."
    )


def audit_pose_visual_triage() -> None:
    targets = read_rows(POSE_AUDIT_TARGETS)
    target_by_id = {row["window_id"]: row for row in targets}
    triage = read_rows(POSE_VISUAL_TRIAGE)
    require_unique([row["window_id"] for row in triage], "pose triage window ID")
    assert set(target_by_id) == {row["window_id"] for row in triage}, (
        "Pose triage must cover the 30D target queue exactly"
    )
    allowed_tiers = {"strong", "usable_with_caution"}
    for row in triage:
        window_id = row["window_id"]
        target = target_by_id[window_id]
        assert row["video_id"] == target["video_id"], window_id
        assert row["target_class"] == target["target_class"], window_id
        assert row["coarse_pose_tier"] in allowed_tiers, window_id
        assert row["decision"] == "retain_for_independent_review_and_source_acquisition"
        assert 0 <= float(row["detection_rate"]) <= 1, window_id
        assert 0 <= float(row["visible_joint_rate_33"]) <= 1, window_id
        assert 0 <= float(row["full_body_frame_rate"]) <= 1, window_id
        assert row["reviewer"] == "codex_visual_screening", window_id
        assert row["independent_human_review_complete"].casefold() == "false", window_id
        assert row["training_allowed"].casefold() == "false", window_id

    tier_counts = Counter(row["coarse_pose_tier"] for row in triage)
    assert tier_counts == {"strong": 7, "usable_with_caution": 11}, tier_counts
    print(
        "30D triage audit passed: 18/18 coarse-pose windows retained; "
        "strong=7, usable_with_caution=11; independent review incomplete "
        "and training disabled."
    )


def main() -> None:
    audit_candidates()
    audit_adjudication()
    audit_screening()
    audit_dense_and_replacements()
    audit_replacement_dense_and_pose_queue()
    audit_pose_visual_triage()


if __name__ == "__main__":
    main()
