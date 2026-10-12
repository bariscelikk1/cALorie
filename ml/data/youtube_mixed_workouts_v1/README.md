# Reviewed YouTube mixed-workout timelines

This directory contains metadata and reviewed temporal labels for the three
new `train_v3` sources. Raw YouTube videos are intentionally excluded from Git.

| Video | Segments | Review evidence |
| --- | ---: | --- |
| Gritty Soldier (`oLsonHQJOUc`) | 29 | Creator chapters plus timestamped contact sheets |
| Tom Peto (`c4TomZjzobY`) | 37 | On-screen 40/20 countdown, transcript, and contact sheets |
| MonikaFit (`W2Bm9dfQjbk`) | 25 | Creator chapters, on-screen countdown, and contact sheets |

Run `ml/notebooks/05_colab_extract_youtube_mixed_landmarks.ipynb` in a Colab
CPU runtime. It downloads the source videos temporarily, extracts MediaPipe
landmarks, and produces `calorie_youtube_mixed_landmarks_v3.zip` with one
`group_id` per original video.

Unsupported movements, transitions, rests, intros, and outros are deliberately
labelled `unknown`. This supplies rejection examples for long mixed-workout
analysis. Keep the separately held-out external-test videos out of this folder
and out of every training archive.
