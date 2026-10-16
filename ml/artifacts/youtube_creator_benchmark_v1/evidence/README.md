# Creator benchmark v1 evidence audit

This directory preserves the user-returned Notebook 28 archive and the local
integrity, pose, and source-content audit completed on 2026-10-16.

The source archive is `calorie_creator_benchmark_v1_evidence.zip` with SHA-256
`3c9930fc3086b68240082668648722836c8959c373a58268347788d7ab24b3c4`.
The ZIP passed `unzip -t`, and all 106 payload entries listed in its internal
`SHA256SUMS.txt` matched. It contains no raw video and no model predictions.

## Pose evidence

| Source | Frames at 15 FPS | Detection | Longest missing run | Source decision |
| --- | ---: | ---: | ---: | --- |
| BullyJuice `ojs-UW8ULhs` | 54,626 | 99.541% | 2.60 s | retain for interval review |
| TIFF x DAN `fJQmoPKvjTg` | 33,331 | 99.067% | 10.00 s | retain; exclude rests/failures by interval |
| STRIQfit `Kw89u6WtPC8` | 37,194 | 98.494% | 7.33 s | retain; pull-up sets plus hard unknowns |
| Buddy Fitness `PY6DrbX4W4o` | 7,451 | 81.385% | 10.73 s | reject entire source |

All four arrays have shape `frames x 17 x 4`, finite float32 landmarks,
strictly increasing timestamps, boolean direct-detection masks, and verified
video/group identities. The three retained real-person sources contain
125,151 frames across 139.05 minutes with a weighted 99.103% detection rate.

## Full-timeline visual decision

All 85 contact sheets were inspected. BullyJuice, TIFF x DAN, and STRIQfit
show real people performing visible motion. Buddy Fitness is an instructional
slide deck made from drawings and still exercise diagrams. A pose estimator
occasionally finding joints in those drawings does not make it valid human
motion evidence, so all Buddy Fitness frames are excluded from the benchmark.

The retained sources visibly support 11 of the 14 canonical classes at source
level. `accepted_source_coverage.csv` records only motion that was seen in the
contact sheets. Exact action boundaries and complete repetitions remain
unapproved; no frozen-model evaluation may run from this audit alone.

The rejected source removes the only projected evidence for `deadlift`,
`lat_pulldown`, and `sit_up`. Three replacement sources were therefore checked
with official chapter metadata and downloaded full-video storyboards:
Michelle Briehler `phFvFuLUFEw`, Criticalbench `lKHGBuanBsY`, and TRAIN WITH
GAINSBYBRAINS `7-mVPCVJMtI`. Notebook 28B extracts only those gap-fill sources.

The benchmark contract remains locked: these sources are never eligible for
training, calibration, threshold selection, or prediction-guided labeling.

