# YouTube long-workout v2 continuous landmarks

This directory preserves the user-returned Notebook 22 report and the local
pose audit performed on 2026-10-16. The source archive is
`calorie_youtube_long_workouts_v2_review_landmarks.zip` with SHA-256:

`f97bf6844f465e7c4bc09f3131bd41edbcda32e20f334ae59a2dfc95b5a48506`

The ZIP passed `unzip -t`; every entry listed in its internal
`SHA256SUMS.txt` also passed verification.

## Pose audit result

| Source | Frames at 15 FPS | Detection rate | Longest missing run | Median joints with visibility >= 0.5 |
| --- | ---: | ---: | ---: | ---: |
| Legally Swole `zxqCV_eQHZY` | 28,475 | 99.515% | 0.73 s | 15/17 |
| Daniel Nikolic `Fk1wnNX4wQ8` | 27,312 | 99.557% | 1.47 s | 16/17 |

All 55,787 frames have finite 17 x 4 landmark tensors after Notebook 22's
recorded interpolation. Four of 118 intervals have detection below 95% or a
missing run above one second; all four are `unknown` intro/outro or transition
material. The 20 supported intervals cover 715 seconds. Their minimum interval
detection rate is 99.44%, so no supported interval is rejected for pose loss.

`pose_interval_audit.csv` contains the interval-level detection, missing-run,
and visibility measurements. `pose_audit_summary.json` is the compact
machine-readable summary. `continuous_landmark_manifest.csv` is copied from
the verified Notebook 22 report.

## Visual review scope

All 118 start/middle/end contact sheets were inspected again against their
fine and canonical labels. No obvious supported/unknown or canonical-class
mismatch was found. This is a label-level contact-sheet audit, not a claim of
full-motion boundary approval. Three snapshots cannot prove first/last motion
frames or complete repetitions.

Every interval therefore remains `use_for_training=false`. Notebook 23 must
perform an independent full-motion boundary review, adjudicate changes, make
the timeline precision honest, run the strict audit, and only then slice clean
training clips and a source-group-preserving manifest.
