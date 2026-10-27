# Long-video test set v1 — evidence (2026-10-27)

Eight per-video ZIPs, one per selected video (`ml/data/long_video_test_v1/`),
produced locally on the user's Mac by `ml/scripts/long_video_intake_v1.py`.
Each holds 15-FPS MediaPipe pose for the full video (normalized and
image-space), overview stills every 2 s, dense stills every 0.5 s, a
per-video record, and its own `SHA256SUMS.txt`. `intake_log.jsonl` keeps the
acquisition record: the raw file's SHA-256, size, format, and duration.
**Raw video was deleted after each video and is not stored anywhere.**

These videos are a **locked test set**: never train on them or tune against
them. Labels are not added yet. Selection and screening history:
`ml/data/long_video_test_v1/PLAN.md` and `screening.csv`.
