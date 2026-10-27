# Long-video training v1 — evidence (2026-10-27)

16 per-video ZIPs (11 train, 5 dev; roles in
`ml/data/long_video_train_v1/roles.csv`), produced locally by
`ml/scripts/long_video_intake_v1.py`: 15-FPS pose for the full video, 2 s
overview and 0.5 s dense stills, and a per-video checksum list. 8.31 hours
in total. Raw video was deleted after each video. `intake_log.jsonl` holds
the acquisition records. These are **not** test data; the locked test set is
`long_video_test_v1`.
