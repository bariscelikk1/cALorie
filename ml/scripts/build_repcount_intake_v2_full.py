#!/usr/bin/env python3
"""Select every remaining RepCount-A video for intake v2 and assign it to a shard."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_repcount_intake_v2_pilot import BUCKETS, V1_LABELS, load_metadata, source_code  # noqa: E402

PILOT_SELECTION = Path("ml/data/repcount_intake_v2/pilot_selection.csv")
SALT = "repcount_intake_v2_full"
N_SHARDS = 8
FIELDS = ["video_id", "shard", "published_action", "bucket", "source_code", "published_count", "metadata_split"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if output differs instead of writing it")
    args = parser.parse_args()

    v1_ids = {row["video_id"] for row in csv.DictReader(V1_LABELS.open())}
    pilot_ids = {row["video_id"] for row in csv.DictReader(PILOT_SELECTION.open()) if row["role"] == "pilot"}
    if len(v1_ids) != 30 or len(pilot_ids) != 64:
        raise SystemExit("expected 30 v1 and 64 pilot clips")
    rows = [r for r in load_metadata() if r["video_id"] not in v1_ids | pilot_ids]
    rows.sort(key=lambda r: hashlib.sha256(f"{SALT}|{r['video_id']}".encode()).hexdigest())
    selected = [{
        "video_id": r["video_id"], "shard": index % N_SHARDS, "published_action": r["action_type"],
        "bucket": BUCKETS[r["action_type"]], "source_code": source_code(r["video_id"]),
        "published_count": int(r["count"]), "metadata_split": r["metadata_split"],
    } for index, r in enumerate(rows)]
    lines = [",".join(FIELDS)] + [",".join(str(row[f]) for f in FIELDS) for row in selected]
    text = "\n".join(lines) + "\n"
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit(f"{args.output} does not match the deterministic selection")
        print(f"{args.output} matches the deterministic selection")
    else:
        args.output.write_text(text)
        print(f"wrote {args.output}: {len(selected)} clips in {N_SHARDS} shards")


if __name__ == "__main__":
    main()
