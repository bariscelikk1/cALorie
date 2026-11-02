# Long-video round 3 mini — evidence (2026-11-02)

6 per-video ZIPs (train `fEuM1XWZ068`, `BZiRx8zVPY8`, `HlnCRJ2Z-i8`, `QWNYZRt_K9g`; test `WopbPBumelc`, `dVtAnYQynbU`; roles in
`ml/data/long_video_round3_v1/roles.csv`), produced locally by `ml/scripts/long_video_intake_v1.py --prefix long_video_round3_v1`:
15-FPS pose for the full video, 2 s overview and 0.5 s dense stills, and a per-video checksum list. Raw video was deleted
after each video. The test videos are locked by `ml/data/long_video_round3_v1/LOCK.json`; with two test videos any score is
informational only.

Screening rejects (ZIPs not kept): `7xDmlGYrfww` (edited compilation), `4FaqRNRHX4M` (two performers, cuts), `LL7OIZm5RAU` (animated figure); see
`ml/data/long_video_round3_v1/screening.csv`.
