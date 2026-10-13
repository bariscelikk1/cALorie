# Reviewed YouTube mixed-workout timelines

This directory contains metadata and reviewed temporal labels for ten training
sources. Raw YouTube videos are intentionally excluded from Git.

All new or revised timelines must follow `ml/data/ANNOTATION_GUIDE.md` and pass:

```bash
python3 ml/scripts/audit_timeline_annotations.py \
  ml/data/youtube_mixed_workouts_v1/annotations/reviewed
```

The current files use the legacy schema. The audit deliberately reports their
missing reviewer/confidence fields so they can be upgraded incrementally rather
than silently presented as double-reviewed ground truth.

The current audit covers **414 rows in 10 videos**. It finds no structural
errors, overlaps, gaps, or invalid canonical labels. It does flag **91 rows**
from Gritty Soldier, Tom Peto, and MonikaFit whose notes still say that visual
review is required, plus one legacy-schema warning per file. Those 91 rows must
receive a second visual review before the next promoted training run. The
machine-readable result is stored in `annotation_audit.json`.

| Video | Segments | Review evidence |
| --- | ---: | --- |
| Gritty Soldier (`oLsonHQJOUc`) | 29 | Creator chapters plus timestamped contact sheets |
| Tom Peto (`c4TomZjzobY`) | 37 | On-screen 40/20 countdown, transcript, and contact sheets |
| MonikaFit (`W2Bm9dfQjbk`) | 25 | Creator chapters, on-screen countdown, and contact sheets |
| Fraser Wilson (`IeGrTqW5lek`) | 41 | Reviewed contiguous exercise timeline |
| Home Fitness Challenge (`85XS8onO9Q4`) | 24 | Reviewed contiguous exercise and transition timeline |
| MadFit (`LqW9gdpctKE`) | 46 | Reviewed contiguous beginner-workout timeline |
| Pamela Reif (`UItWltVZZmE`) | 45 | On-screen 30-second blocks plus sequential contact sheets |
| Heather Robertson (`Gzp8IA2vW_Q`) | 41 | Four rounds, exercise names, countdown, and contact sheets |
| Caroline Girvan (`fegQSC-nUtg`) | 85 | Creator sequence plus on-screen 20/10 timer and contact sheets |
| MadFit (`2Z9g-AZinUc`) | 41 | Five workout sections, countdown, and contact sheets |

Run `ml/notebooks/05_colab_extract_youtube_mixed_landmarks.ipynb` in a Colab
CPU runtime. It downloads the source videos temporarily, extracts MediaPipe
landmarks, and produces `calorie_youtube_mixed_landmarks_v3.zip` with one
`group_id` per original video.

Run `ml/notebooks/06_colab_extract_additional_youtube_landmarks.ipynb` to
process Fraser Wilson, Home Fitness Challenge, and MadFit. These 111 reviewed
segments were missing from the TCN v2 landmark inputs. The notebook creates a
separate archive, so the 91 segments already produced by notebook 05 are not
processed again.

Run `ml/notebooks/07_colab_extract_youtube_training_v4.ipynb` in a **CPU
runtime** to process the four `train_v4` sources. It downloads the videos only
inside the temporary Colab runtime and produces
`calorie_youtube_training_landmarks_v4.zip` containing 212 reviewed segments.
The archive is cumulative for this batch and can be uploaded alongside the
earlier landmark ZIPs when retraining.

Unsupported movements, compound exercises, transitions, rests, intros, and outros are deliberately
labelled `unknown`. This supplies rejection examples for long mixed-workout
analysis. GainsByBrains, Sunny Health, and Nobadaddiction remain separately
held-out external tests and must stay out of every training archive. Heather
Robertson's no-repeat workout (`iSj7k4EXqho`) is the locked `external_test_v3`
source and must also stay out of training and threshold selection.

Growingannanas (`ROg_FeobtzI`) and HASfit (`lJGxljpd7Fc`) were inspected and
rejected because both videos show two athletes. Feeding either one to the
single-pose extractor would mix identities across frames.
