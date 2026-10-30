#!/usr/bin/env python3
"""Build the predeclared 3-fold source-group rotation for RepCount gate v1."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
from pathlib import Path


SALT = "repcount_gate_rotation_v1"
N_FOLDS = 3
CLASS_ORDER = ["lateral_raise", "sit_up", "squat", "unknown"]
REQUIRED_SHARED_GROUPS = {
    "outdoor_crunch_shared_01": {"stu8_49", "stu9_56"},
    "orange_rig_squat_shared_01": {"stu1_69", "stu6_59"},
}
FIELDS = [
    "video_id",
    "source_group_id",
    "visible_target",
    "visible_variant",
    "eval_fold",
    "frozen_v6f_prediction",
    "v6f_error_type",
    "evidence_csv",
]


def error_type(target: str, prediction: str) -> str:
    if prediction == target:
        return "correct"
    if target != "unknown" and prediction == "unknown":
        return "gate_false_unknown"
    if target == "unknown":
        return "gate_false_accept"
    return "wrong_supported_class"


def build(evidence: Path) -> list[dict]:
    rows = list(csv.DictReader(evidence.open()))
    errors: list[str] = []
    if len(rows) != 30:
        errors.append(f"expected 30 rows, found {len(rows)}")
    if any(row["training_allowed"] != "false" for row in rows):
        errors.append("evidence rows must all remain training_allowed=false")
    for group, members in REQUIRED_SHARED_GROUPS.items():
        found = {row["video_id"] for row in rows if row["source_group_id"] == group}
        if found != members:
            errors.append(f"{group} must contain exactly {sorted(members)}, found {sorted(found)}")
    if {row["visible_target"] for row in rows} - set(CLASS_ORDER):
        errors.append("unexpected visible_target")
    if errors:
        raise SystemExit("Rotation build failed:\n- " + "\n- ".join(errors))

    groups: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        groups[row["visible_target"]].add(row["source_group_id"])
    fold_of: dict[str, int] = {}
    counter = 0
    for target in CLASS_ORDER:
        ordered = sorted(groups[target], key=lambda g: hashlib.sha256(f"{SALT}|{g}".encode()).hexdigest())
        for group in ordered:
            fold_of[group] = counter % N_FOLDS
            counter += 1

    manifest = []
    for row in sorted(rows, key=lambda r: (fold_of[r["source_group_id"]], r["visible_target"], r["video_id"])):
        manifest.append({
            "video_id": row["video_id"],
            "source_group_id": row["source_group_id"],
            "visible_target": row["visible_target"],
            "visible_variant": row["visible_variant"],
            "eval_fold": fold_of[row["source_group_id"]],
            "frozen_v6f_prediction": row["frozen_v6f_prediction"],
            "v6f_error_type": error_type(row["visible_target"], row["frozen_v6f_prediction"]),
            "evidence_csv": "ml/data/repcount_development_v1/final_visible_adjudication_v1.csv",
        })
    return manifest


def render(manifest: list[dict]) -> str:
    lines = [",".join(FIELDS)]
    for row in manifest:
        lines.append(",".join(str(row[field]) for field in FIELDS))
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if output differs instead of writing it")
    args = parser.parse_args()

    text = render(build(args.evidence))
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit(f"{args.output} does not match the deterministic rotation")
        print(f"{args.output} matches the deterministic rotation")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
