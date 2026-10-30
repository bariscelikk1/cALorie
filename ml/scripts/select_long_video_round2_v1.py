#!/usr/bin/env python3
"""Metadata-only search and rule-based selection for long-video round 2 (14 videos: 8 train + 6 test).

Reuses the earlier selection helpers; never downloads media. Rules (ml/data/long_video_round2_v1/PLAN.md):
new creators only, 20-45 min, one performer, >=3 listed supported exercises, home/gym known, one video per
channel. Train pool (8): each of the five weak classes appears in >=4 videos, >=2 home and >=2 gym. Test pool (6):
each weak class in >=3 videos, >=1 home and >=1 gym. Greedy in SHA-256 hash order (separate salts); the test pool is
drawn from what remains after the train pool and never shares a channel with it.
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
import select_long_video_train_v1 as earlier  # noqa: E402

QUERIES = list(earlier.QUERIES) + [  # saved results are reused; new queries are appended with a logged revision
    # Revision 1 (2026-10-28, before any new result was seen): the saved results leave only 10 eligible creators.
    "tricep workout follow along dumbbell tricep extensions kickbacks 20 minutes",
    "triceps and shoulders dumbbell workout follow along real time",
    "lateral raises front raises rear delt workout follow along dumbbells",
    "shoulder day gym workout follow along dumbbells and cables",
    "bicep and tricep gym workout follow along 30 minutes",
    "arm day workout at the gym real time dumbbells cables",
    "back and biceps dumbbell workout follow along rows curls",
    "one arm dumbbell row and curl workout follow along",
    "upper body workout at home dumbbells follow along 35 minutes",
    "full body dumbbell strength workout 45 minutes follow along",
    "dumbbell workout for women follow along upper body sculpt",
    "dumbbell workout for men follow along arms shoulders back",
    "gym full body workout follow along dumbbells shoulder press rows",
    "push workout chest shoulders triceps follow along dumbbells",
    "pull workout back biceps follow along dumbbells",
    "full body workout follow along dumbbell overhead press curls lunges",
    "strength workout follow along 30 minutes no talking music only",
    "workout with me upper body dumbbells timer follow along",
    "home gym full body workout follow along bench dumbbells",
    "dumbbell arm and shoulder workout over 30 minutes follow along",
    "30 min upper body strength follow along shoulders triceps biceps back",
    "full body low impact dumbbell workout follow along squats rows presses",
    "senior friendly dumbbell workout follow along arms shoulders",
    "kettlebell and dumbbell upper body follow along rows presses",
    # Revision 2 (2026-10-28, before any new result was seen): after revision 1 only 15 eligible creators remain and
    # lateral raise has 4 of the 7 needed (494 of 835 hits were already-used creators). Longer-tail queries appended.
    "dumbbell shoulder workout 25 minutes lateral raises arnold press follow along",
    "boulder shoulders dumbbell workout follow along lateral raise rear delt fly overhead press",
    "side delt workout dumbbell lateral raises real time follow along",
    "capped shoulders workout at home dumbbells follow along",
    "shoulders and traps dumbbell workout follow along shrugs lateral raises",
    "bent over row single arm row dumbbell back workout follow along 30 min",
    "dumbbell back workout at home follow along rows pullovers",
    "dumbbell only back and biceps workout 30 minutes real time",
    "overhead press dumbbell workout follow along shoulder strength",
    "seated dumbbell shoulder press workout follow along",
    "tricep overhead extension skull crusher dumbbell workout follow along",
    "arm workout dumbbells follow along no repeat 30 min biceps triceps shoulders",
    "upper body hiit dumbbells follow along rows presses curls",
    "total upper body workout dumbbells follow along rows lateral raises curls",
    "full body workout with weights follow along 40 min timer lateral raise row curl",
    "toned arms and shoulders workout follow along dumbbells",
    "strong shoulders and back workout follow along dumbbells at home",
    "gym shoulder workout machine and dumbbell follow along lateral raises",
    "dumbbell push pull legs follow along full body 45 min",
    "five exercises dumbbell circuit follow along 30 minutes rows lateral raises",
    "workout along with me strength shoulders back arms real time",
    "morning dumbbell workout follow along upper body 30 min",
    "full upper body dumbbell routine follow along 20 minutes",
    "dumbbell complex workout follow along row curl press",
    "home workout dumbbells follow along intermediate full body strength rows raises",
    "gym upper body workout follow along real time cable row lateral raise curl",
]
WEAK = ["tricep_extension", "lateral_raise", "bicep_curl", "dumbbell_row", "shoulder_press"]
POOLS = [  # name, size, min videos per weak class, min home, min gym, hash salt
    ("train", 8, 4, 2, 2, "long_video_round2_train"),
    ("test", 6, 3, 1, 1, "long_video_round2_test"),
]
RESULTS_PER_QUERY = 30


def pick(eligible, size, min_weak, min_home, min_gym, salt, taken):
    pool = sorted((r for r in eligible if r["channel_id"] not in taken), key=lambda r: hashlib.sha256(f"{salt}|{r['video_id']}".encode()).hexdigest())

    def needs(chosen):
        count = {w: sum(w in c["exercises"].split(";") for c in chosen) for w in WEAK}
        settings = [c["setting"] for c in chosen]
        n = {f"weak:{w}": max(0, min_weak - count[w]) for w in WEAK}
        n.update({"home": max(0, min_home - settings.count("home")), "gym": max(0, min_gym - settings.count("gym"))})
        return n

    # Backtracking in hash order: the first valid set in lexicographic hash rank. (Logged fix, 2026-10-28: plain greedy
    # missed a valid set although 13 eligible creators list lateral raises.)
    def search(start, chosen):
        n = needs(chosen)
        if len(chosen) == size:
            return list(chosen) if not any(n.values()) else None
        if max(n.values(), default=0) > size - len(chosen):
            return None
        for i in range(start, len(pool)):
            found = search(i + 1, chosen + [pool[i]])
            if found:
                return found
        return None

    chosen = search(0, []) or []
    return chosen, needs(chosen)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--yt-dlp", default="yt-dlp")
    args = parser.parse_args()
    excluded = list(csv.DictReader((args.out_dir / "exclusions.csv").open()))
    bad_videos = {r["video_id"] for r in excluded if r["video_id"]}
    bad_channels = {r["channel_id"] for r in excluded if r["channel_id"]}
    bad_names = {r["creator"].strip().lower() for r in excluded if r["creator"]}
    screening = list(csv.DictReader((args.out_dir / "screening.csv").open()))
    screened_out = {r["video_id"] for r in screening if r["verdict"] == "reject"}
    animated = {r["video_id"] for r in screening if r["verdict"] == "reject" and "animated" in r["reason"]}

    snap_path = args.out_dir / "search_snapshot.json"
    snap = json.loads(snap_path.read_text())
    hits = {h["video_id"]: h for h in snap["hits"]}
    for query in [q for q in QUERIES if q not in snap["queries"]]:
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

    infos = dict(snap["infos"])
    unavailable = list(snap.get("unavailable", []))
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

    seen, eligible = set(), []
    for r in sorted((r for r in rows if not r["reject_reason"]), key=lambda r: r["video_id"]):
        if r["channel_id"] not in seen:
            seen.add(r["channel_id"]); eligible.append(r)
    taken, picked, unmet = set(), {}, {}
    for name, size, min_weak, min_home, min_gym, salt in POOLS:
        chosen, left = pick(eligible, size, min_weak, min_home, min_gym, salt, taken)
        picked[name], unmet[name] = chosen, [k for k, v in left.items() if v]
        taken |= {c["channel_id"] for c in chosen}
    ok = all(len(picked[n]) == s and not unmet[n] for n, s, *_ in POOLS)
    ids = {r["video_id"]: n for n, rs in picked.items() for r in rs} if ok else {}
    fields = ["video_id", "channel_id", "channel", "title", "duration_s", "query", "exercises", "setting", "chapters", "reject_reason", "role"]
    with (args.out_dir / "candidates.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n"); w.writeheader()
        for r in sorted(rows, key=lambda r: r["video_id"]):
            w.writerow({**r, "role": ids.get(r["video_id"], "")})
    print(f"hits {len(rows)} | eligible one-per-channel {len(eligible)} | train {len(picked['train'])} test {len(picked['test'])} | unmet {unmet}")
    if not ok:
        raise SystemExit("No valid 8+6 set; a logged query revision is needed.")
    for n in ("train", "test"):
        print(f"--- {n}")
        for r in picked[n]:
            print(f"{r['video_id']}  {int(float(r['duration_s']))//60:>2} min  {r['setting']:4s}  {r['channel'][:26]:26s}  {r['exercises']}")


if __name__ == "__main__":
    main()
