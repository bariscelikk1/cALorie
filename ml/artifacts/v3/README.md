# cALorie experiment artifacts — v3 inputs

This directory preserves the reviewed long-form YouTube landmark archives that
will be added to the next TCN training run. The source MP4 files are excluded;
the compact NPZ sequences and their manifests are sufficient for Notebook 03.

## Additional YouTube landmarks

`landmarks/calorie_youtube_additional_landmarks_v1.zip` contains the reviewed
segments produced by Notebook 06.

## YouTube training batch v4

`landmarks/calorie_youtube_training_landmarks_v4.zip` contains 212 reviewed
segments from four source videos. The archive audit found:

- 212 readable NPZ files and 81,863 sampled frames
- 205 `ok` segments and seven low-detection `unknown` segments
- four independent source-video groups
- 96.79% mean pose-detection rate
- consistent `(frames, 17, 4)` landmark arrays
- no missing files, invalid shapes, NaNs, infinities, or duplicate clip IDs

Notebook 03 filters the seven low-detection segments before window generation.
This generated archive retains the older `youtube_additional_workouts_v1`
source-dataset string because extraction began before the notebook metadata fix;
its YouTube-based `group_id` values are correct, so group-separated splitting is
unaffected.

`SHA256SUMS.txt` identifies the exact archives preserved here.

## TCN v3 candidate

`model/calorie_tcn_report.zip` is the checkpoint trained after adding both v3
YouTube landmark batches to the earlier Workout/Fitness, MM-Fit, and YouTube
inputs. Its group-separated internal test report contains 2,381 windows:

- accuracy: **83.49%**
- balanced accuracy: **86.31%**
- Macro F1: **81.90%**
- best validation Macro F1: **79.96%** at epoch 37
- classes: **15 exercises + unknown**

This improves over the v2 candidate's 80.72% accuracy and 74.08% Macro F1 on
their respective internal splits. The splits changed when the new source groups
were added, so the locked GainsByBrains evaluation remains the meaningful
promotion test. The main report files are extracted beside the ZIP for review.

## Locked long-video result

The v3 candidate was evaluated on the same frozen GainsByBrains video, human
labels, boundary guard, and 0.55 confidence threshold as v1 and v2. It strongly
improved rejection but became too conservative on supported exercises:

- stable accuracy: **66.38%** (v1: 42.32%, v2: 32.46%)
- stable Macro F1: **17.96%** (v1: 19.45%, v2: 15.31%)
- supported-exercise accuracy: **33.03%** (v1: 66.52%, v2: 49.32%)
- unsupported-exercise rejection: **79.59%** (v1: 32.65%, v2: 20.70%)
- transition rejection: **88.89%** (v1: 26.19%, v2: 34.92%)

The higher total accuracy is driven by the many `unknown` windows. V3 correctly
rejects most unsupported exercises and transitions, but also rejects every
plank variation, jumping jack, and pop squat window in this test. It should not
replace v1 as the supported-exercise classifier yet. The result motivates a
two-stage design: first reject unsupported/transition windows, then classify
accepted windows among supported exercises.

See `evaluation/gainsbybrains_external_v1/` for the frozen labels, raw and
scored predictions, per-movement results, timeline, confusion matrix, and the
direct v1/v2/v3 comparison.
