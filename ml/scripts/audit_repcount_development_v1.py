#!/usr/bin/env python3
"""Fail-closed structural audit for the RepCount development intake."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


EXPECTED_ACTIONS = {
    "squat": "squat",
    "situp": "sit_up",
    "front_raise": "unknown",
}
TRAIN_PEOPLE = {f"stu{i}" for i in range(1, 8)}
VALIDATION_PEOPLE = {f"stu{i}" for i in range(8, 11)}


def audit(path: Path) -> dict:
    frame = pd.read_csv(path)
    errors: list[str] = []

    if len(frame) != 30:
        errors.append(f"expected 30 rows, found {len(frame)}")
    if frame.video_id.duplicated().any():
        errors.append("video_id must be unique")
    if set(frame.person_id) != TRAIN_PEOPLE | VALIDATION_PEOPLE:
        errors.append("expected exactly stu1 through stu10")
    if set(frame.source_action) != set(EXPECTED_ACTIONS):
        errors.append("unexpected source_action set")
    for source_action, target_label in EXPECTED_ACTIONS.items():
        subset = frame[frame.source_action == source_action]
        if len(subset) != 10 or subset.person_id.nunique() != 10:
            errors.append(f"{source_action} must have one row per person")
        if not subset.target_label.eq(target_label).all():
            errors.append(f"{source_action} target mapping must be {target_label}")

    train = frame[frame.development_role == "train_pool"]
    validation = frame[frame.development_role == "dev_validation"]
    if set(train.person_id) != TRAIN_PEOPLE or len(train) != 21:
        errors.append("train_pool must contain three rows for stu1 through stu7")
    if set(validation.person_id) != VALIDATION_PEOPLE or len(validation) != 9:
        errors.append("dev_validation must contain three rows for stu8 through stu10")
    if set(train.person_id) & set(validation.person_id):
        errors.append("person leakage between train_pool and dev_validation")
    if not frame.review_status.eq("metadata_only").all():
        errors.append("all rows must remain metadata_only before visual review")
    if not frame.training_allowed.astype(str).str.lower().eq("false").all():
        errors.append("training must remain forbidden")

    return {
        "rows": int(len(frame)),
        "people": int(frame.person_id.nunique()),
        "actions": sorted(frame.source_action.unique()),
        "train_pool_rows": int(len(train)),
        "dev_validation_rows": int(len(validation)),
        "person_disjoint": not bool(set(train.person_id) & set(validation.person_id)),
        "training_allowed_rows": int(
            frame.training_allowed.astype(str).str.lower().eq("true").sum()
        ),
        "errors": errors,
        "audit_pass": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("ml/data/repcount_development_v1/candidates.csv"),
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = audit(args.input)
    text = json.dumps(result, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text, end="")
    if not result["audit_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
