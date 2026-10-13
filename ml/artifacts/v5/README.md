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
