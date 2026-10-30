# Long-video round 2 — evidence (2026-10-28)

14 per-video ZIPs (8 train, 6 test; roles in `ml/data/long_video_round2_v1/roles.csv`; `Xyea2DCicKU` and
`74B9SxqtMug` and `o3xDawAnb-M` are screening replacements), produced locally by
`ml/scripts/long_video_intake_v1.py --prefix long_video_round2_v1`: 15-FPS pose for the full video, 2 s overview
and 0.5 s dense stills, and a per-video checksum list. Raw video was deleted after each video. `intake_log.jsonl`
holds the acquisition records, including the three screening rejects (`kla05C_4eio`, `1Mbuyc5uW4s`,
`tPnVxUmFcqI`), whose ZIPs were not kept. The six test videos are locked by
`ml/data/long_video_round2_v1/LOCK.json`.
