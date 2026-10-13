# cALorie experiment artifacts — v5 hard-negative inputs

This version begins a controlled correction of the two-stage v4 gate. Notebook
09 showed that movement-like unsupported exercises often passed the gate even
though ordinary rest and transitions were easier to reject.

## Workout/Fitness gate evidence

`landmarks/calorie_workoutfitness_gate_hardneg_v1.zip` was produced by Notebook
10 from previously unused Workout/Fitness classes. It contains:

- **144** landmark clips and a matching manifest;
- **140** clips with `status == ok` and four low-detection clips retained for
  audit but filtered before training;
- **84 hard-negative clips** mapped to `unknown` from chest fly machine, hip
  thrust, leg extension, leg raises, Russian twist, T-bar row, and tricep dips;
- **60 supported-variant clips** mapped to bench press, bicep curl, deadlift,
  and tricep extension;
- **95.52%** mean pose-detection rate;
- one unique group ID per original short video.

The frozen GainsByBrains video and its labels were not used. Notebook 11 adds
this archive to the six v4 inputs while preserving the same architecture,
window size, optimizer, sampler, and validation-only threshold selection. This
makes the next run a controlled test of whether better gate evidence improves
external rejection without destroying supported recognition.

## Two-stage v5 internal result

Notebook 11 trained the same two-stage architecture with the seventh archive.
Validation selected a gate threshold of **0.90** without access to the locked
external video. On the new group-separated internal test split:

- gate accuracy: **84.07%**
- gate balanced accuracy: **82.53%**
- gate Macro F1: **82.17%**
- oracle exercise-classifier accuracy: **92.13%**
- oracle exercise-classifier Macro F1: **83.78%**
- end-to-end accuracy: **83.05%**
- end-to-end balanced accuracy: **72.54%**
- end-to-end Macro F1: **73.43%**

The split changed when new groups were added, so these values are not a direct
promotion over v4. Gate validation Macro F1 peaked at epoch 13 and exercise
validation Macro F1 at epoch 14; early stopping restored those checkpoints.
Notebook 12 performs the meaningful comparison on the unchanged locked video.

## Locked external result

Notebook 12 evaluated v5 on the unchanged 917-second GainsByBrains benchmark.
At the checkpoint's validation-selected **0.90** gate threshold, stable-window
accuracy reached **77.10%**, unsupported-exercise rejection reached **100%**,
and transition rejection reached **100%**. This is a large correction of v4's
false-positive behavior. Supported-exercise accuracy fell to **28.51%**,
showing that the internal threshold is too strict outside its training domains.

A diagnostic sweep shows that **0.60-0.65** would recover roughly **47%**
supported accuracy while retaining at least **97.65%** unknown rejection, but
the locked test cannot be used to select the production threshold. The next
step is calibration on a separate mixed-workout validation set and additional
hard-positive plank variants. See `evaluation/gainsbybrains_external_v1/` for
the full report and the v4/v5 comparison.

See `model/` for the combined checkpoint, reports, threshold sweep, histories,
raw predictions, and original report ZIP. See `evaluation/` for the locked
external benchmark.
