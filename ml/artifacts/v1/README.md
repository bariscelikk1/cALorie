# cALorie experiment artifacts — v1

This directory freezes the inputs, trained checkpoint, and external-video evaluations for the initial 16-class landmark TCN. `SHA256SUMS.txt` identifies the exact files used.

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

## Short external-video evaluation

`evaluation/wikimedia_jumping_jacks_burpees/` records inference on the 45-second Wikimedia Commons video [Jumping jacks and burpees](https://commons.wikimedia.org/wiki/File:Jumping_jacks_and_burpees.webm), licensed CC BY-SA 4.0.

- Pose detection rate: **0.9971**
- Model output: 26 deadlift windows, 8 squat windows, 6 unknown windows
- Expected visible actions from the source description: jumping jacks and burpees
- Correct jumping-jack windows: **0**

This is a clear domain-generalization failure. The high held-out window score does not transfer to this external recording. The result is retained as evidence for targeted data expansion, annotation review, and a TCN v2 comparison; it must not be presented as a successful external test.

## Long mixed-workout evaluation

`evaluation/gainsbybrains_external_v1/` freezes predictions and independent
human timeline labels for a 917.4-second workout video. The source video itself
is intentionally excluded from GitHub. A three-second guard around human label
boundaries produces the stable-interior subset.

At the notebook's 0.55 confidence threshold:

- Pose detection rate: **99.9%** across 13,761 sampled frames
- Stable-interior accuracy: **42.3%**
- Stable-interior balanced accuracy: **49.3%**
- Stable-interior macro F1: **19.5%**
- Supported-exercise accuracy: **66.5%**
- Unsupported-exercise rejection: **32.7%**
- Transition, intro, and outro rejection: **26.2%**

The model recognized both plank variations and two squat families, but missed
jumping jack and pop squat and frequently forced unsupported movements into a
known class. Raising the rejection threshold to 0.80 improved unknown and
transition rejection in this test while keeping supported accuracy near 65.6%.
That value is a validation candidate, not a final threshold selected from test
data.

The long-video run proves the complete video-to-timeline pipeline works. It
also shows that the next improvement should come from diverse long-video
labels, stronger `unknown` and transition data, and error-driven retraining.
This exact video remains a locked external test for TCN v2 comparisons.
