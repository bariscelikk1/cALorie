#!/usr/bin/env python3
"""Merge intake v2 tier-1 decisions and visual reviews into one label table."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

RULE_SET = "tier1_v1"
AUDIT_NOTE = "tier1_v1 auto-accept; class audit passed 2026-10-27 (28 sampled clips: 1 wrong, 2 unusable; no class over the limit)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="ml/data/repcount_intake_v2")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    d = args.data_dir
    tier1 = pd.concat([pd.read_csv(d / "pilot_tier1_v1.csv"), pd.read_csv(d / "full_tier1_v1.csv")], ignore_index=True)
    review = pd.concat([pd.read_csv(d / "pilot_visual_review_v1.csv"), pd.read_csv(d / "full_visual_review_v1.csv")], ignore_index=True)
    roles = pd.read_csv(d / "full_role_groups_v1.csv")
    assert tier1.video_id.is_unique and review.video_id.is_unique
    rows = []
    for t in tier1.itertuples(index=False):
        r = review[review.video_id == t.video_id]
        if len(r):
            r = r.iloc[0]
            rows.append({"video_id": t.video_id, "published_action": t.published_action, "label": r.visible_target,
                         "visible_variant": r.visible_variant, "usable": bool(r.usable), "confidence": r.confidence,
                         "review_status": "reviewed", "annotation_source": "claude_visual_contact_sheet",
                         "issue_tags": r.issue_tags if isinstance(r.issue_tags, str) else "", "notes": r.notes})
        elif t.tier1_decision == "auto_accept":
            rows.append({"video_id": t.video_id, "published_action": t.published_action, "label": t.tier1_label,
                         "visible_variant": "", "usable": True, "confidence": "medium",
                         "review_status": "auto_verified", "annotation_source": AUDIT_NOTE, "issue_tags": "", "notes": ""})
        else:
            raise SystemExit(f"{t.video_id}: tier-1 sent it to review but no review row exists")
    labels = pd.DataFrame(rows).merge(roles[["video_id", "role_group", "sealed_test_eligible"]], on="video_id", how="left", validate="one_to_one")
    assert labels.role_group.notna().all()
    labels["training_allowed"] = False  # set only in a versioned experiment manifest
    labels.sort_values("video_id").to_csv(args.output, index=False)
    use = labels[labels.usable]
    print(f"{len(labels)} clips; usable {len(use)}; status {labels.review_status.value_counts().to_dict()}")
    print(use.label.value_counts().to_string())


if __name__ == "__main__":
    main()
