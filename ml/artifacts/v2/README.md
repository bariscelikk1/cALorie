# cALorie experiment artifacts — v2 inputs

This directory begins the second TCN experiment with reviewed, long-form
YouTube workout data. The source MP4 files are excluded from GitHub. The
landmark archive is the compact, reproducible training input produced by
`05_colab_extract_youtube_mixed_landmarks.ipynb`.

## YouTube mixed-workout landmarks

`landmarks/calorie_youtube_mixed_landmarks_v3.zip` contains 91 reviewed
segments from three source videos. Each NPZ stores a 15 FPS sequence with 17
normalized pose landmarks and four values per landmark (`x`, `y`, `z`, and
visibility). All segments from one source video share a `group_id`, so the
training notebook cannot split neighboring segments from the same video across
train, validation, and test sets.

Validation results:

- 91 readable NPZ files and 39,652 sampled frames
- 90 `ok` segments and one three-second `unknown` intro with low detection
- 98.97% mean pose-detection rate
- no invalid shapes, NaNs, infinities, or manifest/frame-count mismatches
- 69 `unknown` segments and 22 supported-exercise segments

The high `unknown` count is intentional: unsupported exercises, rests,
previews, and transitions teach the classifier to reject movements outside its
supported classes. Notebook 03 uses weighted sampling so this majority class
does not dominate training batches.

The extracted manifest is included beside the ZIP for review. `validation.json`
records the machine-readable audit, and `SHA256SUMS.txt` identifies the exact
files committed here.

## TCN v2 candidate

`model/calorie_tcn_report.zip` is the first model trained with all four
landmark archives. It contains the checkpoint and its complete development
report. The main report files are also extracted beside it for review.

- Test accuracy: **0.8072**
- Balanced accuracy: **0.8293**
- Macro F1: **0.7408**
- Best validation Macro F1: **0.7069** at epoch 10
- Classes: **15 exercises + unknown**

The lower aggregate score is informative rather than directly comparable with
v1. Group splitting held the entire MonikaFit YouTube source out of training.
All 275 of its test windows were independently labelled `unknown`; the model
correctly rejected 62 (**22.5%**) and forced most remaining windows into
`pull_up`, `bicep_curl`, or `squat`. On the same test run, MM-Fit window
accuracy was 95.3% and Workout/Fitness window accuracy was 75.2%.

This result confirms that source-group separation works and exposes the domain
generalization problem hidden by ordinary short-clip scores. It is a candidate
checkpoint until it is evaluated on the frozen GainsByBrains, Sunny Health,
and Nobadaddiction long-video tests. Those external videos remain excluded
from training.

## Locked long-video result

The candidate has now been evaluated on the frozen GainsByBrains test using the
same labels, boundary guard, and 0.55 threshold as v1. Stable accuracy fell from
42.32% to 32.46%, supported-exercise accuracy fell from 66.52% to 49.32%, and
unsupported-exercise rejection fell from 32.65% to 20.70%. Transition rejection
improved from 26.19% to 34.92%.

See `evaluation/gainsbybrains_external_v1/` for the raw inference export,
scored predictions, per-movement results, and direct v1/v2 comparison. V2 is
retained as an experiment, but the locked evidence does not support promoting
it over v1.
