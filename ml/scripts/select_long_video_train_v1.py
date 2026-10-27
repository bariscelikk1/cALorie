#!/usr/bin/env python3
"""Metadata-only search and rule-based selection for long-video training v1 (16 videos).

Reuses the test-set selection helpers; never downloads media. Rules (PLAN.md, section 1):
new creators only (test channels included in the exclusions), 20-45 min, one performer,
>=3 listed supported exercises, home/gym known, one video per channel; across the 16,
each weak class appears in >=4 videos and there are >=4 home and >=4 gym videos.
Picked greedily in SHA-256 hash order of video ID.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import select_long_video_test_v1 as base  # noqa: E402

QUERIES = [  # fixed before any result was seen; aimed at the weak classes
    "dumbbell full body workout follow along 30 min rows lunges shoulder press",
    "upper body dumbbell workout follow along biceps triceps shoulders",
    "arms workout follow along bicep curls tricep extensions 30 minutes",
    "shoulder workout follow along lateral raises overhead press",
    "back workout follow along dumbbell rows",
    "lower body dumbbell workout follow along lunges squats",
    "abs and full body workout follow along sit ups lunges",
    "gym full body workout follow along machines dumbbells",
    "home dumbbell workout follow along 40 minutes full body",
    "strength training follow along beginner dumbbells 30 min",
    "total body strength workout follow along no repeats dumbbells",
    "push pull workout follow along dumbbells",
    # Revision 1 (2026-10-27, before any video was watched): the first 12 queries were dominated by
    # already-used channels (201 of 302 hits), leaving 9 eligible videos. Appended, saved results kept.
    "workout with me dumbbell rows curls lunges real time",
    "real time arm workout dumbbells no talking",
    "30 minute dumbbell upper body workout at home with me",
    "full body workout with dumbbells over 40 follow along",
    "kettlebell and dumbbell full body follow along workout",
    "beginner gym workout real time machines and dumbbells",
    "dumbbell shoulder and arm workout real time follow along",
    "seated dumbbell workout follow along full body",
    "resistance band and dumbbell workout follow along 30 min",
    "sit ups crunches and dumbbell workout follow along",
    "triceps biceps shoulders dumbbell workout 30 minutes",
    "back and shoulders dumbbell workout follow along home",
]
RESULTS_PER_QUERY = 30
PICK = 16
WEAK = ["bicep_curl", "dumbbell_row", "lunge", "shoulder_press", "tricep_extension", "lateral_raise", "sit_up"]
MIN_PER_WEAK, MIN_SETTING = 4, 4
SALT = "long_video_train_v1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--yt-dlp", default="yt-dlp")
    args = parser.parse_args()
    excluded = list(csv.DictReader((args.out_dir / "exclusions.csv").open()))
    bad_videos = {r["video_id"] for r in excluded if r["video_id"]}
    bad_channels = {r["channel_id"] for r in excluded if r["channel_id"]}
    bad_names = {r["creator"].strip().lower() for r in excluded if r["creator"]}
    screening_path = args.out_dir / "screening.csv"
    screened_out = ({r["video_id"] for r in csv.DictReader(screening_path.open()) if r["verdict"] == "reject"}
                    if screening_path.exists() else set())
    animated = ({r["video_id"] for r in csv.DictReader(screening_path.open()) if r["verdict"] == "reject" and "animated" in r["reason"]}
                if screening_path.exists() else set())

    snap_path = args.out_dir / "search_snapshot.json"
    snap = json.loads(snap_path.read_text()) if snap_path.exists() else None
    hits = {h["video_id"]: h for h in snap["hits"]} if snap else {}
    for query in [q for q in QUERIES if snap is None or q not in snap["queries"]]:
        for page in base.run(args.yt_dlp, "--flat-playlist", f"ytsearch{RESULTS_PER_QUERY}:{query}"):
            for e in page.get("entries") or []:
                if e.get("id") and e["id"] not in hits:
                    hits[e["id"]] = {"video_id": e["id"], "query": query, "title": e.get("title", ""), "duration_s": e.get("duration") or 0,
                                     "channel_id": e.get("channel_id", ""), "channel": e.get("channel") or e.get("uploader") or ""}
    animated_channels = {h["channel_id"] for h in hits.values() if h["video_id"] in animated}
    rows = []
    for h in hits.values():
        reason = ""
        if h["video_id"] in screened_out:
            reason = "screened_out"
        elif h["channel_id"] in animated_channels:
            reason = "screened_out_channel_animated"
        elif h["video_id"] in bad_videos or h["channel_id"] in bad_channels or h["channel"].strip().lower() in bad_names:
            reason = "existing_source"
        elif not base.MIN_S <= float(h["duration_s"] or 0) <= base.MAX_S:
            reason = "duration"
        rows.append({**h, "reject_reason": reason})

    infos = dict(snap["infos"]) if snap else {}
    unavailable = list(snap.get("unavailable", [])) if snap else []
    missing = [r["video_id"] for r in rows if not r["reject_reason"] and r["video_id"] not in infos and r["video_id"] not in unavailable]
    if missing:
        keep = ("id", "title", "description", "chapters", "channel", "channel_id", "license", "duration")
        fetched = {i["id"]: {k: i.get(k) for k in keep} for i in base.run(args.yt_dlp, "--skip-download", *[f"https://www.youtube.com/watch?v={v}" for v in missing])}
        for i in fetched.values():
            i["chapters"] = [{"title": c.get("title", "")} for c in i.get("chapters") or []]
        infos.update(fetched)
        unavailable += [v for v in missing if v not in fetched]
    snap_path.write_text(json.dumps({"queries": QUERIES, "hits": list(hits.values()), "infos": infos, "unavailable": unavailable}, indent=1) + "\n")

    for r in rows:
        if r["reject_reason"]:
            continue
        info = infos.get(r["video_id"])
        if not info:
            r["reject_reason"] = "metadata_unavailable"; continue
        if info.get("channel_id") in bad_channels or (info.get("channel") or "").strip().lower() in bad_names:
            r["reject_reason"] = "existing_source"; continue
        t = base.text_of(info)
        found = [k for k, p in base.EXERCISES.items() if re.search(p, t)]
        r.update({"exercises": ";".join(found), "setting": "gym" if re.search(base.GYM, t) else ("home" if re.search(base.HOME, t) else "unclear"),
                  "chapters": len(info.get("chapters") or [])})
        if re.search(base.GROUP, t):
            r["reject_reason"] = "group_or_partner"
        elif len(found) < 3:
            r["reject_reason"] = "fewer_than_3_supported"
        elif r["setting"] == "unclear":
            r["reject_reason"] = "setting_unclear"

    passing = sorted((r for r in rows if not r["reject_reason"]), key=lambda r: hashlib.sha256(f"{SALT}|{r['video_id']}".encode()).hexdigest())
    seen, eligible = set(), []
    for r in passing:
        if r["channel_id"] not in seen:
            seen.add(r["channel_id"]); eligible.append(r)

    def needs(chosen):
        count = {w: sum(w in c["exercises"].split(";") for c in chosen) for w in WEAK}
        settings = [c["setting"] for c in chosen]
        n = {f"weak:{w}": max(0, MIN_PER_WEAK - count[w]) for w in WEAK}
        n.update({"home": max(0, MIN_SETTING - settings.count("home")), "gym": max(0, MIN_SETTING - settings.count("gym"))})
        return n

    chosen = []
    for r in eligible:  # greedy in hash order: take a video if it reduces an unmet need, or if slots remain beyond the needs
        if len(chosen) == PICK:
            break
        before = needs(chosen)
        after = needs(chosen + [r])
        helps = any(after[k] < before[k] for k in before)
        slots_left = PICK - len(chosen) - 1
        if helps or slots_left >= max(before.values(), default=0):
            chosen.append(r)
    final_needs = needs(chosen)
    ok = len(chosen) == PICK and not any(final_needs.values())
    ids = {r["video_id"] for r in chosen} if ok else set()
    fields = ["video_id", "channel_id", "channel", "title", "duration_s", "query", "exercises", "setting", "chapters", "reject_reason", "selected"]
    with (args.out_dir / "candidates.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n"); w.writeheader()
        for r in sorted(rows, key=lambda r: r["video_id"]):
            w.writerow({**r, "selected": r["video_id"] in ids})
    print(f"hits {len(rows)} | passing {len(passing)} | one-per-channel {len(eligible)} | chosen {len(chosen)} | unmet {[k for k, v in final_needs.items() if v]}")
    if not ok:
        raise SystemExit("No valid 16-video set; a logged query revision is needed.")
    for r in chosen:
        print(f"{r['video_id']}  {int(float(r['duration_s']))//60:>2} min  {r['setting']:4s}  {r['channel'][:26]:26s}  {r['exercises']}")


if __name__ == "__main__":
    main()
