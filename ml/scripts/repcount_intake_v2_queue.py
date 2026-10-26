#!/usr/bin/env python3
"""Build the tier-2 review queue (tier-1 failures + 10% audit) and compact review pages."""

from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

AUDIT_SALT = "repcount_intake_v2_audit"
AUDIT_FRACTION = 0.10
AUDIT_MINIMUM = 3
CLIPS_PER_PAGE = 4
TILE_W, TILE_H, BAR_H = 640, 308, 22


def audit_sample(tier1: pd.DataFrame) -> pd.Series:
    """Deterministic per-bucket sample of auto-accepted clips (at least 3 when available)."""
    picked = []
    accepted = tier1[tier1.tier1_decision == "auto_accept"]
    for _, group in accepted.groupby("rule_bucket"):
        n = min(len(group), max(AUDIT_MINIMUM, math.ceil(AUDIT_FRACTION * len(group))))
        order = group.video_id.map(lambda v: hashlib.sha256(f"{AUDIT_SALT}|{v}".encode()).hexdigest())
        picked += group.assign(_order=order).sort_values("_order").video_id.head(n).tolist()
    return tier1.video_id.isin(picked)


def render_pages(queue: pd.DataFrame, sheet_dirs: list[Path], out_dir: Path) -> None:
    sheets = {p.stem: p for d in sheet_dirs for p in d.glob("*.jpg")}
    out_dir.mkdir(parents=True, exist_ok=True)
    for page, start in enumerate(range(0, len(queue), CLIPS_PER_PAGE)):
        canvas = np.zeros((2 * (TILE_H + BAR_H), 2 * TILE_W, 3), dtype=np.uint8)
        for slot, row in enumerate(queue.iloc[start:start + CLIPS_PER_PAGE].itertuples(index=False)):
            sheet = cv2.resize(cv2.imread(str(sheets[row.video_id])), (TILE_W, TILE_H), interpolation=cv2.INTER_AREA)
            x, y = (slot % 2) * TILE_W, (slot // 2) * (TILE_H + BAR_H)
            label = f"{start + slot + 1}. {row.video_id} | {row.rule_bucket} | {row.queue_reason}"
            cv2.putText(canvas, label[:78], (x + 6, y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1, cv2.LINE_AA)
            canvas[y + BAR_H:y + BAR_H + TILE_H, x:x + TILE_W] = sheet
            cv2.rectangle(canvas, (x, y), (x + TILE_W - 1, y + BAR_H + TILE_H - 1), (90, 90, 90), 1)
        assert cv2.imwrite(str(out_dir / f"page_{page:03d}.jpg"), canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tier1_csv", type=Path)
    parser.add_argument("queue_csv", type=Path)
    parser.add_argument("--pages", type=Path, help="write review pages here")
    parser.add_argument("--sheets", type=Path, nargs="*", default=[], help="report/sheets directories")
    parser.add_argument("--exclude", type=Path, help="CSV of video_ids already reviewed (e.g. the pilot)")
    args = parser.parse_args()
    tier1 = pd.read_csv(args.tier1_csv)
    if args.exclude:
        tier1 = tier1[~tier1.video_id.isin(pd.read_csv(args.exclude).video_id)]
    audit = audit_sample(tier1)
    queue = tier1[(tier1.tier1_decision == "review") | audit].copy()
    queue["queue_reason"] = np.where(audit[queue.index], "audit_of_auto_accept", queue.tier1_fail_reasons.fillna(""))
    queue = queue.sort_values(["rule_bucket", "queue_reason", "video_id"]).reset_index(drop=True)
    queue[["video_id", "rule_bucket", "tier1_decision", "tier1_label", "queue_reason"]].to_csv(args.queue_csv, index=False)
    print(f"queue: {len(queue)} clips ({int(audit.sum())} audit, {int((tier1.tier1_decision == 'review').sum())} tier-1 review)")
    print(queue.groupby(["rule_bucket", queue.queue_reason.eq("audit_of_auto_accept")]).size().to_string())
    if args.pages:
        render_pages(queue, args.sheets, args.pages)
        print(f"pages: {math.ceil(len(queue) / CLIPS_PER_PAGE)} in {args.pages}")


if __name__ == "__main__":
    main()
