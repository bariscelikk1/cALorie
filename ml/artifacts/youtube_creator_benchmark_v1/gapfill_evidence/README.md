# Creator benchmark v1 gap-fill evidence audit

The user returned `calorie_creator_benchmark_v1_gapfill_evidence.zip` from CPU
Notebook 28B. Its outer SHA-256 is recorded in `ARCHIVE_SHA256.txt`. ZIP
integrity and all 64 internal checksums passed before review.

The three continuous landmark arrays contain 91,525 finite `frames x 17 x 4`
samples across 101.69 minutes. Their source-level direct pose detection ranges
from 96.87% to 99.98%; the frame-weighted rate is 97.97%. All 52 contact-sheet
pages were inspected without consulting any model prediction.

All three sources show real people and are retained for selected intervals:

- Michelle Briehler: conservative visible RDL/deadlift and lat-pulldown work
  segments;
- Criticalbench: a second creator's visible deadlift demonstration segments;
- TRAIN WITH GAINSBYBRAINS: the visible continuous sit-up set inside the
  official 16:18-18:18 chapter.

`ml/data/youtube_creator_benchmark_v1/locked_intervals_v1.csv` combines these
decisions with the three accepted Notebook 28 sources. The resulting frozen
table has 37 intervals, all 14 supported classes, 1,664 seconds and 24,960
15-FPS frames. The minimum direct-detection rate across any retained interval
is 99.88%. Gaps, setup, talking, rests, transitions, compound unsupported
motions, and ambiguous variants are not labeled as supported actions.

This is locked external-test evidence. It is forbidden for training,
calibration, threshold selection, model selection, or inspecting predictions
while changing labels. The next valid step is to build immutable arrays and
run the already frozen V6-C and V6-F candidates without retuning.
