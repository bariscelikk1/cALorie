#!/usr/bin/env python3
"""Assign train/dev/sealed-test roles for RepCount-A training v1 (TRAINING_PLAN_V1.md, section 1)."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd

SALT = "repcount_intake_v2_roles"
TEST_CLASSES = ["unknown", "squat", "jumping_jack", "bench_press", "pull_up", "sit_up", "push_up"]
SEALED_FRACTION, DEV_FRACTION = 0.20, 0.15
MIN_SEALED_PER_CLASS = 10
V1_LABELS = Path("ml/data/repcount_development_v1/final_visible_adjudication_v1.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="ml/data/repcount_intake_v2")
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if output differs instead of writing it")
    args = parser.parse_args()
    d = args.data_dir

    labels = pd.read_csv(d / "intake_v2_labels_v1.csv")
    usable = labels[labels.usable].copy()
    v1 = pd.read_csv(V1_LABELS)
    roles = pd.read_csv(d / "full_role_groups_v1.csv")
    seen = set(pd.read_csv(d / "pilot_selection.csv").video_id) | set(v1.video_id)
    seen_groups = set(roles.loc[roles.video_id.isin(seen), "role_group"])
    counts = usable.label.value_counts()
    sealed_target = {c: round(SEALED_FRACTION * counts[c]) for c in TEST_CLASSES}
    dev_target = {c: round(DEV_FRACTION * counts[c]) for c in TEST_CLASSES}
    order = sorted(usable.role_group.unique(), key=lambda g: hashlib.sha256(f"{SALT}|{g}".encode()).hexdigest())
    members = {g: m for g, m in usable.groupby("role_group")}

    role, sealed_have, dev_have = {}, dict.fromkeys(TEST_CLASSES, 0), dict.fromkeys(TEST_CLASSES, 0)
    for g in order:
        m = members[g]
        if (m.sealed_test_eligible.all() and g not in seen_groups and (m.review_status == "reviewed").all()
                and set(m.label) <= set(TEST_CLASSES)
                and all(sealed_have[c] + int((m.label == c).sum()) <= sealed_target[c] for c in set(m.label))):
            role[g] = "sealed_test"
            for c in m.label:
                sealed_have[c] += 1
    for g in order:
        m = members[g]
        if g in role or not set(m.label) <= set(TEST_CLASSES):
            continue
        if all(dev_have[c] + int((m.label == c).sum()) <= dev_target[c] for c in set(m.label)):
            role[g] = "dev"
            for c in m.label:
                dev_have[c] += 1

    out = usable[["video_id", "label", "review_status", "role_group"]].copy()
    out["source"] = "intake_v2"
    out["role"] = out.role_group.map(role).fillna("train")
    v1_rows = v1[["video_id", "visible_target"]].rename(columns={"visible_target": "label"}).merge(
        roles[["video_id", "role_group"]], on="video_id", validate="one_to_one")
    v1_rows["review_status"] = "adjudicated"
    v1_rows["source"] = "development_v1"
    v1_rows["role"] = v1_rows.role_group.map(role).fillna("train")  # follow the group; never sealed (seen groups)
    out = pd.concat([out, v1_rows], ignore_index=True).sort_values("video_id")

    errors = []
    if out.video_id.duplicated().any():
        errors.append("duplicate video_id")
    if (out.groupby("role_group").role.nunique() > 1).any():
        errors.append("a role group spans roles")
    if out[(out.role == "sealed_test") & out.video_id.isin(seen)].shape[0]:
        errors.append("pilot or v1 clip in sealed test")
    if (out[out.role == "sealed_test"].review_status != "reviewed").any():
        errors.append("non-reviewed clip in sealed test")
    low = {c: n for c, n in sealed_have.items() if n < MIN_SEALED_PER_CLASS}
    if low:
        errors.append(f"sealed-test classes below {MIN_SEALED_PER_CLASS}: {low}")
    if errors:
        raise SystemExit("Role build failed:\n- " + "\n- ".join(errors))

    text = out.to_csv(index=False, lineterminator="\n")
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit(f"{args.output} does not match the deterministic roles")
        print(f"{args.output} matches the deterministic roles")
        return
    args.output.write_text(text)
    print(pd.crosstab(out.label, out.role, margins=True).to_string())


if __name__ == "__main__":
    main()
