#!/usr/bin/env python3
"""Select the RepCount-A intake v2 pilot deterministically from pinned metadata."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import urllib.request
from pathlib import Path


METADATA_REVISION = "d4c2ad3df38dfef3d1fca6f7b3fdfad6a38128e5"
METADATA_HASHES = {
    "train": "a7fe063a71a502f1bd5e590a5d582c73455d1bb9f5d391ab8d9f0f2c5365d59d",
    "validation": "55b0b013f8eb5273cc40b84288bbbf538fdde4877ce22acf0cbe1b4a71531675",
    "test": "bbdafa6c81af396465b3e4a20c3d24a058a9d116fa67fa2dd91082eb5599fe3d",
}
SALT = "repcount_intake_v2_pilot"
PER_BUCKET = 8
BUCKETS = {
    "squat": "squat", "squant": "squat",
    "situp": "sit_up",
    "pull_up": "pull_up", "pullups": "pull_up",
    "bench_pressing": "bench_press", "benchpressing": "bench_press",
    "push_up": "push_up", "pushups": "push_up",
    "jump_jack": "jumping_jack", "jumpjacks": "jumping_jack",
    "front_raise": "unknown_front_raise", "frontraise": "unknown_front_raise",
    "pommelhorse": "unknown_other", "battle_rope": "unknown_other", "others": "unknown_other",
}
V1_LABELS = Path("ml/data/repcount_development_v1/final_visible_adjudication_v1.csv")
FIELDS = ["video_id", "role", "published_action", "pilot_bucket", "source_code",
          "published_count", "metadata_split", "selection_rank"]


def load_metadata() -> list[dict]:
    rows = []
    for split, expected in METADATA_HASHES.items():
        url = f"https://huggingface.co/datasets/lmms-lab-eval/repcount/resolve/{METADATA_REVISION}/{split}.jsonl"
        payload = urllib.request.urlopen(url, timeout=120).read()
        actual = hashlib.sha256(payload).hexdigest()
        if actual != expected:
            raise SystemExit(f"{split}.jsonl hash mismatch: {actual}")
        for line in payload.decode().splitlines():
            row = json.loads(line)
            row["metadata_split"] = split
            rows.append(row)
    return rows


def source_code(video_id: str) -> str:
    return video_id.split("_")[0] if video_id.startswith("stu") else "none"


def select(rows: list[dict], v1_ids: set[str]) -> list[dict]:
    unmapped = {r["action_type"] for r in rows} - set(BUCKETS)
    if unmapped:
        raise SystemExit(f"unmapped published actions: {sorted(unmapped)}")
    selected = []
    for bucket in sorted(set(BUCKETS.values())):
        pool = [r for r in rows if BUCKETS[r["action_type"]] == bucket and r["video_id"] not in v1_ids]
        pool.sort(key=lambda r: hashlib.sha256(f"{SALT}|{r['video_id']}".encode()).hexdigest())
        # First pass takes one clip per source code to spread sources; then fill in hash order.
        chosen, seen = [], set()
        for row in pool:
            if source_code(row["video_id"]) not in seen:
                chosen.append(row)
                seen.add(source_code(row["video_id"]))
            if len(chosen) == PER_BUCKET:
                break
        for row in pool:
            if len(chosen) == PER_BUCKET:
                break
            if row not in chosen:
                chosen.append(row)
        if len(chosen) != PER_BUCKET:
            raise SystemExit(f"{bucket}: only {len(chosen)} clips available")
        for rank, row in enumerate(chosen):
            selected.append({
                "video_id": row["video_id"], "role": "pilot", "published_action": row["action_type"],
                "pilot_bucket": bucket, "source_code": source_code(row["video_id"]),
                "published_count": int(row["count"]), "metadata_split": row["metadata_split"],
                "selection_rank": rank,
            })
    by_id = {r["video_id"]: r for r in rows}
    for video_id in sorted(v1_ids):
        row = by_id[video_id]
        selected.append({
            "video_id": video_id, "role": "v1_scene_reference", "published_action": row["action_type"],
            "pilot_bucket": "", "source_code": source_code(video_id),
            "published_count": int(row["count"]), "metadata_split": row["metadata_split"],
            "selection_rank": "",
        })
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--check", action="store_true", help="fail if output differs instead of writing it")
    args = parser.parse_args()

    v1_ids = {row["video_id"] for row in csv.DictReader(V1_LABELS.open())}
    if len(v1_ids) != 30:
        raise SystemExit("expected 30 v1 clips")
    selected = select(load_metadata(), v1_ids)
    lines = [",".join(FIELDS)] + [",".join(str(row[f]) for f in FIELDS) for row in selected]
    text = "\n".join(lines) + "\n"
    if args.check:
        if args.output.read_text() != text:
            raise SystemExit(f"{args.output} does not match the deterministic selection")
        print(f"{args.output} matches the deterministic selection")
    else:
        args.output.write_text(text)
        print(f"wrote {args.output}: {sum(r['role'] == 'pilot' for r in selected)} pilot + "
              f"{sum(r['role'] != 'pilot' for r in selected)} v1 reference rows")


if __name__ == "__main__":
    main()
