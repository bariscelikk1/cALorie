#!/usr/bin/env python3
"""Metadata-only search and rule-based selection for long-video test v1 (PLAN.md, section 2).

Never downloads media: yt-dlp is called with --skip-download / --flat-playlist only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path

QUERIES = [  # fixed before any result was seen
    "30 minute full body workout follow along",
    "full body home workout no equipment 30 min follow along",
    "bodyweight workout follow along squats push ups sit ups",
    "pull up bar home workout follow along full body",
    "jumping jacks full body workout 30 minutes",
    "full body dumbbell workout follow along 30 min",
    "full gym workout follow along real time",
    "gym workout follow along bench press squat deadlift",
    "follow along back workout lat pulldown rows gym",
    "push day workout follow along bench press shoulder press",
    "follow along upper body gym workout real time",
    "full body barbell workout follow along",
    # Revision 2 (user decision, 2026-10-27): one video listing only 2 supported exercises may enter if
    # one of them is pull_up. Revision 1 (2026-10-27, before any video was watched): no passing video mentioned pull-ups,
    # which the coverage rule requires. These queries are appended; earlier results are kept as saved.
    "pull up workout follow along full body",
    "calisthenics workout follow along pull ups push ups",
    "home workout with pull up bar follow along 30 minutes",
]
RESULTS_PER_QUERY = 30
MIN_S, MAX_S = 20 * 60, 45 * 60
SHORTLIST_SIZE, PICK = 20, 8
SALT = "long_video_test_v1"
EXERCISES = {
    "squat": r"\bsquats?\b",
    "sit_up": r"\bsit[\s-]?ups?\b|\bcrunch(es)?\b",
    "push_up": r"\bpush[\s-]?ups?\b|\bpress[\s-]?ups?\b",
    "pull_up": r"\bpull[\s-]?ups?\b|\bchin[\s-]?ups?\b",
    "bench_press": r"\bbench press\b|\bchest press\b",
    "jumping_jack": r"\bjumping jacks?\b|\bstar jumps?\b",
    "bicep_curl": r"\b(bicep|biceps|hammer|dumbbell|barbell)\s+curls?\b",
    "deadlift": r"\bdeadlifts?\b|\brdls?\b",
    "dumbbell_row": r"\b(bent[\s-]?over|dumbbell|barbell|single[\s-]?arm|one[\s-]?arm)\s+rows?\b",
    "lat_pulldown": r"\blat pull[\s-]?downs?\b|\bpull[\s-]?downs?\b",
    "lateral_raise": r"\blateral raises?\b|\bside raises?\b",
    "lunge": r"\blunges?\b",
    "shoulder_press": r"\bshoulder press\b|\boverhead press\b|\bmilitary press\b",
    "tricep_extension": r"\btricep(s)? extensions?\b|\bskull ?crushers?\b|\boverhead extensions?\b",
}
COVERED = ["squat", "sit_up", "push_up", "pull_up", "bench_press", "jumping_jack"]
UNCOVERED = [k for k in EXERCISES if k not in COVERED]
GYM = r"\bgym\b|\bbarbell\b|\bmachine\b|\bcable\b|\bbench press\b|\blat pull[\s-]?down"
HOME = r"\bhome\b|\bno equipment\b|\bbodyweight\b|\bliving room\b"
GROUP = r"\bclass\b|\bgroup\b|\bbootcamp\b|\bpartner\b|\bcouples?\b|\bkids\b"


def run(ytdlp: str, *args: str) -> list[dict]:
    out = subprocess.run([ytdlp, "--no-warnings", "--ignore-errors", "-J", *args], capture_output=True, text=True).stdout
    parsed = [json.loads(line) for line in out.splitlines() if line.strip()]
    return [p for p in parsed if p]  # unavailable videos come back as null


def text_of(info: dict) -> str:
    chapters = " ".join(c.get("title", "") for c in info.get("chapters") or [])
    return f"{info.get('title', '')}\n{info.get('description', '')}\n{chapters}".lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--yt-dlp", default="yt-dlp")
    args = parser.parse_args()
    excluded = list(csv.DictReader((args.out_dir / "exclusions.csv").open()))
    bad_videos = {r["video_id"] for r in excluded if r["video_id"]}
    bad_channels = {r["channel_id"] for r in excluded if r["channel_id"]}
    bad_names = {r["creator"].strip().lower() for r in excluded if r["creator"]}

    snapshot_path = args.out_dir / "search_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.exists() else None
    hits = {h["video_id"]: h for h in snapshot["hits"]} if snapshot else {}
    for query in [q for q in QUERIES if snapshot is None or q not in snapshot["queries"]]:
        for page in run(args.yt_dlp, "--flat-playlist", f"ytsearch{RESULTS_PER_QUERY}:{query}"):
            for entry in page.get("entries") or []:
                if entry.get("id") and entry["id"] not in hits:
                    hits[entry["id"]] = {"video_id": entry["id"], "query": query, "title": entry.get("title", ""),
                                         "duration_s": entry.get("duration") or 0, "channel_id": entry.get("channel_id", ""),
                                         "channel": entry.get("channel") or entry.get("uploader") or ""}
    rows = []
    for h in hits.values():
        reason = ""
        if h["video_id"] in bad_videos or h["channel_id"] in bad_channels or h["channel"].strip().lower() in bad_names:
            reason = "existing_source"
        elif not MIN_S <= float(h["duration_s"] or 0) <= MAX_S:
            reason = "duration"
        rows.append({**h, "reject_reason": reason})

    detailed = [r for r in rows if not r["reject_reason"]]
    infos = dict(snapshot["infos"]) if snapshot else {}
    missing = [r["video_id"] for r in detailed if r["video_id"] not in infos and not (snapshot and r["video_id"] in snapshot.get("unavailable", []))]
    unavailable = list(snapshot.get("unavailable", [])) if snapshot else []
    if missing:
        keep = ("id", "title", "description", "chapters", "channel", "channel_id", "license", "duration")
        fetched = {i["id"]: {k: i.get(k) for k in keep} for i in run(args.yt_dlp, "--skip-download", *[f"https://www.youtube.com/watch?v={v}" for v in missing])}
        for info in fetched.values():
            info["chapters"] = [{"title": c.get("title", "")} for c in info.get("chapters") or []]
        infos.update(fetched)
        unavailable += [v for v in missing if v not in fetched]
    snapshot_path.write_text(json.dumps({"queries": QUERIES, "hits": list(hits.values()), "infos": infos, "unavailable": unavailable}, indent=1) + "\n")
    for r in detailed:
        info = infos.get(r["video_id"])
        if not info:
            r["reject_reason"] = "metadata_unavailable"
            continue
        if info.get("channel_id") in bad_channels or (info.get("channel") or "").strip().lower() in bad_names:
            r["reject_reason"] = "existing_source"
            continue
        t = text_of(info)
        found = [k for k, pattern in EXERCISES.items() if re.search(pattern, t)]
        r.update({"exercises": ";".join(found), "setting": "gym" if re.search(GYM, t) else ("home" if re.search(HOME, t) else "unclear"),
                  "chapters": len(info.get("chapters") or []), "license": info.get("license") or ""})
        exception = len(found) == 2 and "pull_up" in found  # revision 2: at most one per set (checked in valid())
        if re.search(GROUP, t):
            r["reject_reason"] = "group_or_partner"
        elif len(found) < 3 and not exception:
            r["reject_reason"] = "fewer_than_3_supported"
        elif r["setting"] == "unclear":
            r["reject_reason"] = "setting_unclear"
        else:
            r["pullup_exception"] = exception

    passing = [r for r in rows if not r["reject_reason"]]
    # One video per channel: keep each channel's first video in hash order.
    passing.sort(key=lambda r: hashlib.sha256(f"{SALT}|{r['video_id']}".encode()).hexdigest())
    seen, eligible = set(), []
    for r in passing:
        if r["channel_id"] not in seen:
            seen.add(r["channel_id"])
            eligible.append(r)

    def valid(combo):
        ex = set(itertools.chain.from_iterable(r["exercises"].split(";") for r in combo))
        settings = [r["setting"] for r in combo]
        return (set(COVERED) <= ex and len(ex & set(UNCOVERED)) >= 4
                and settings.count("home") >= 3 and settings.count("gym") >= 3
                and sum(bool(r.get("pullup_exception")) for r in combo) <= 1)

    size, pick = SHORTLIST_SIZE, None
    while True:  # grow the shortlist in steps of 5 until a valid set exists or every eligible video is in
        shortlist = eligible[:size]
        pick = next((c for c in itertools.combinations(shortlist, PICK) if valid(c)), None)
        if pick is not None or size >= len(eligible):
            break
        size += 5
    chosen = {r["video_id"] for r in pick} if pick else set()
    shortlist_ids = {r["video_id"] for r in shortlist}
    fields = ["video_id", "channel_id", "channel", "title", "duration_s", "query", "exercises", "setting", "chapters",
              "license", "pullup_exception", "reject_reason", "shortlisted", "selected"]
    with (args.out_dir / "candidates.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for r in sorted(rows, key=lambda r: r["video_id"]):
            writer.writerow({**r, "shortlisted": r["video_id"] in shortlist_ids, "selected": r["video_id"] in chosen})
    if pick is None:
        raise SystemExit(f"No valid set of {PICK} among {len(eligible)} eligible videos (candidates.csv written); "
                         "widen the queries in a documented plan revision.")
    print(f"search hits {len(rows)} | passing {len(passing)} | one-per-channel {len(eligible)} | shortlist {len(shortlist)} | selected {len(pick)}")
    for r in pick:
        print(f"{r['video_id']}  {int(float(r['duration_s']))//60:>2} min  {r['setting']:4s}  {r['channel'][:28]:28s}  {r['exercises']}")


if __name__ == "__main__":
    main()
