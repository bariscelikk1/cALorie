#!/usr/bin/env python3
"""Build the long-video test v1 exclusion list: every YouTube video, channel, and creator already used."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

ID_PATTERN = re.compile(r"(?:watch\?v=|youtu\.be/|youtube:)([A-Za-z0-9_-]{11})")
EXTRA_SOURCES = [Path("ml/artifacts/v6a1/model/split_assignments.csv")]  # every training YouTube group


def existing_video_ids() -> set[str]:
    ids = set()
    for path in list(Path("ml/data").rglob("*.csv")) + EXTRA_SOURCES:
        ids |= set(ID_PATTERN.findall(path.read_text(errors="ignore")))
    return ids


def existing_creator_names() -> set[str]:
    names = set()
    for path in Path("ml/data").rglob("*.csv"):
        with path.open(errors="ignore") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames and "creator" in reader.fieldnames:
                names |= {row["creator"].strip() for row in reader if row.get("creator", "").strip()}
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--yt-dlp", default="yt-dlp", help="yt-dlp executable (metadata only, never downloads)")
    args = parser.parse_args()
    ids = sorted(existing_video_ids())
    urls = [f"https://www.youtube.com/watch?v={i}" for i in ids]
    result = subprocess.run([args.yt_dlp, "--skip-download", "--ignore-errors", "--no-warnings",
                             "--print", "%(id)s\t%(channel_id)s\t%(channel)s", *urls],
                            capture_output=True, text=True)
    resolved = {line.split("\t")[0]: line.split("\t") for line in result.stdout.splitlines() if line.count("\t") == 2}
    rows = [{"kind": "video", "video_id": i, "channel_id": resolved.get(i, ["", "", ""])[1],
             "creator": resolved.get(i, ["", "", ""])[2], "resolved": i in resolved} for i in ids]
    rows += [{"kind": "creator_name", "video_id": "", "channel_id": "", "creator": n, "resolved": True}
             for n in sorted(existing_creator_names())]
    with args.output.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "video_id", "channel_id", "creator", "resolved"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    unresolved = [r["video_id"] for r in rows if r["kind"] == "video" and not r["resolved"]]
    print(f"{len(ids)} videos ({len(ids) - len(unresolved)} resolved), "
          f"{len({r['channel_id'] for r in rows if r['channel_id']})} channels, "
          f"{sum(r['kind'] == 'creator_name' for r in rows)} creator names; unresolved: {unresolved}")


if __name__ == "__main__":
    main()
