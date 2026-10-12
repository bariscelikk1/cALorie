# Reviewed YouTube mixed-workout timelines

This directory contains metadata and reviewed temporal labels for six training
sources. Raw YouTube videos are intentionally excluded from Git.

| Video | Segments | Review evidence |
| --- | ---: | --- |
| Gritty Soldier (`oLsonHQJOUc`) | 29 | Creator chapters plus timestamped contact sheets |
| Tom Peto (`c4TomZjzobY`) | 37 | On-screen 40/20 countdown, transcript, and contact sheets |
| MonikaFit (`W2Bm9dfQjbk`) | 25 | Creator chapters, on-screen countdown, and contact sheets |
| Fraser Wilson (`IeGrTqW5lek`) | 41 | Reviewed contiguous exercise timeline |
| Home Fitness Challenge (`85XS8onO9Q4`) | 24 | Reviewed contiguous exercise and transition timeline |
| MadFit (`LqW9gdpctKE`) | 46 | Reviewed contiguous beginner-workout timeline |

Run `ml/notebooks/05_colab_extract_youtube_mixed_landmarks.ipynb` in a Colab
CPU runtime. It downloads the source videos temporarily, extracts MediaPipe
landmarks, and produces `calorie_youtube_mixed_landmarks_v3.zip` with one
`group_id` per original video.

Run `ml/notebooks/06_colab_extract_additional_youtube_landmarks.ipynb` to
process Fraser Wilson, Home Fitness Challenge, and MadFit. These 111 reviewed
segments were missing from the TCN v2 landmark inputs. The notebook creates a
separate archive, so the 91 segments already produced by notebook 05 are not
processed again.

Unsupported movements, transitions, rests, intros, and outros are deliberately
labelled `unknown`. This supplies rejection examples for long mixed-workout
analysis. GainsByBrains, Sunny Health, and Nobadaddiction remain separately
held-out external tests and must stay out of every training archive.
