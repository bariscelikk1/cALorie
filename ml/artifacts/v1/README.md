# cALorie experiment artifacts — v1

This directory freezes the inputs, trained checkpoint, and first external-video evaluation for the initial 16-class landmark TCN. `SHA256SUMS.txt` identifies the exact files used.

## Landmark datasets

| Artifact | Content |
| --- | --- |
| `landmarks/calorie_workoutfitness_landmarks_v1.zip` | Workout/Fitness MediaPipe sequences; 378 clips, of which training retains 368 with status `ok` |
| `landmarks/calorie_mmfit_landmarks_v1.zip` | MM-Fit exercise sets in the common 17-joint format; 616 clips from 21 workout/person groups |
| `landmarks/calorie_mmfit_unknown_v1.zip` | MM-Fit non-exercise gaps; 252 four-second `unknown` clips from the same 21 groups |

The training notebook filters manifests to `status == ok`, constructs 64-frame windows, and keeps group IDs separated between train, validation, and test splits.

## TCN v1

`model/calorie_tcn_report.zip` contains the trained `tcn_model.pt` checkpoint and complete evaluation report. The most useful report files are also extracted beside it for GitHub review.

- Test accuracy: **0.8763**
- Balanced accuracy: **0.8697**
- Macro F1: **0.8281**
- Classes: **15 exercises + unknown**
- Window: **64 frames**, stride **32 frames**

These are development results. Workout/Fitness has no reliable person IDs, and the plank test support comes from one independent video despite containing 53 windows.

## First external-video evaluation

`evaluation/wikimedia_jumping_jacks_burpees/` records inference on the 45-second Wikimedia Commons video [Jumping jacks and burpees](https://commons.wikimedia.org/wiki/File:Jumping_jacks_and_burpees.webm), licensed CC BY-SA 4.0.

- Pose detection rate: **0.9971**
- Model output: 26 deadlift windows, 8 squat windows, 6 unknown windows
- Expected visible actions from the source description: jumping jacks and burpees
- Correct jumping-jack windows: **0**

This is a clear domain-generalization failure. The high held-out window score does not transfer to this external recording. The result is retained as evidence for targeted data expansion, annotation review, and a TCN v2 comparison; it must not be presented as a successful external test.
