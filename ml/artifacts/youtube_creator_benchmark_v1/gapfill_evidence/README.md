# Creator benchmark v1 gap-fill evidence audit

The user returned `calorie_creator_benchmark_v1_gapfill_evidence.zip` from CPU
Notebook 28B. Its outer SHA-256 is recorded in `ARCHIVE_SHA256.txt`. ZIP
integrity and all 64 internal checksums passed before review.

The three continuous landmark arrays contain 91,525 finite `frames x 17 x 4`
samples across 101.69 minutes. Their source-level direct pose detection ranges
from 96.87% to 99.98%; the frame-weighted rate is 97.97%. All 52 contact-sheet
pages were inspected without consulting any model prediction.

All three sources show real people and are retained for closer interval review:

- Michelle Briehler: RDL/deadlift and lat-pulldown candidate regions;
- Criticalbench: deadlift demonstration chapter, which also contains standing
  and talking within the broad candidate regions;
- TRAIN WITH GAINSBYBRAINS: a sit-up candidate region inside the official
  16:18-18:18 chapter.

`ml/data/youtube_creator_benchmark_v1/candidate_intervals_v1.csv` combines
provisional locators from all six sources. Its 37 draft regions span 1,664
seconds and propose all 14 classes. The minimum direct-detection rate across
these broad regions is 99.88%; that is only a pose-quality diagnostic. Sparse
10-second contact sheets and creator chapters cannot prove exact boundaries
or exclude rests and talking within a region. Every row needs dense RGB
inspection and second review before it can become a benchmark label.

The *sources* are reserved as external-test evidence, but the interval labels
are not locked. They are forbidden for training, calibration, threshold
selection, or model selection. Do not inspect predictions while changing
labels. The next step is dense motion annotation and audit, followed by a
genuine label lock and frozen-model evaluation.
