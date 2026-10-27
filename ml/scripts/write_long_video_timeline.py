#!/usr/bin/env python3
"""Write a long-video test v1 timeline CSV (timeline_labels_v2 schema) from a compact spec.

Spec lines: `start_s end_s segment_type fine_label current_tcn_label confidence [2nd] # notes`
(`2nd` marks needs_second_review). Rows must tile the video exactly.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

FIELDS = ["video_id", "video_file", "start_s", "end_s", "start_time", "end_time", "segment_type", "fine_label",
          "current_tcn_label", "split", "use_for_training", "annotation_source", "boundary_precision_s", "notes",
          "annotation_confidence", "review_status", "reviewer", "needs_second_review"]


def clock(s: float) -> str:
    return f"{int(s) // 60:02d}:{s % 60:04.1f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video_id")
    parser.add_argument("duration_s", type=float)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows, previous_end = [], 0.0
    for line in args.spec.read_text().splitlines():
        if not line.strip():
            continue
        body, _, notes = line.partition("#")
        parts = body.split()
        start, end = float(parts[0]), float(parts[1])
        end = min(end, args.duration_s)
        assert abs(start - previous_end) < 1e-6, f"gap/overlap at {start} (previous end {previous_end})"
        previous_end = end
        rows.append({
            "video_id": args.video_id, "video_file": f"{args.video_id}.mp4 (deleted after pose extraction)",
            "start_s": f"{start:.1f}", "end_s": f"{end:.1f}", "start_time": clock(start), "end_time": clock(end),
            "segment_type": parts[2], "fine_label": parts[3], "current_tcn_label": parts[4],
            "split": "locked_test", "use_for_training": "false",
            "annotation_source": "claude_visual_overview_2s", "boundary_precision_s": "2.0",
            "notes": notes.strip(), "annotation_confidence": parts[5], "review_status": "reviewed",
            "reviewer": "claude_visual", "needs_second_review": "true" if "2nd" in parts[6:] else "false",
        })
    assert abs(previous_end - args.duration_s) < 2.1, f"timeline ends at {previous_end}, video is {args.duration_s}"
    rows[-1]["end_s"], rows[-1]["end_time"] = f"{args.duration_s:.1f}", clock(args.duration_s)
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {args.output}: {len(rows)} rows")


if __name__ == "__main__":
    main()
