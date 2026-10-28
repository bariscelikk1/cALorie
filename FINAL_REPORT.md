# cALorie — final report

Date: 2026-10-28. Branch: `feat/tcn-rebuild`.

## 1. What cALorie is

cALorie watches a workout video and works out **which exercise is happening,
second by second**. It never looks at raw pixels during recognition. It first
extracts the person's body keypoints with MediaPipe, then two small neural
networks read the motion of those keypoints:

```text
video -> MediaPipe pose (17 keypoints, 15 FPS)
      -> gate: "a supported exercise, or something else?"
      -> classifier: "which of the 14 exercises?"
      -> smoothing -> exercise timeline
```

Supported exercises (14): bench press, bicep curl, deadlift, dumbbell row,
jumping jack, lat pulldown, lateral raise, lunge, pull-up, push-up, shoulder
press, sit-up, squat, tricep extension. Everything else (rest, warm-ups,
talking, other moves) should come out as `unknown`.

## 2. What was built, and what was not

| Part | Status |
| --- | --- |
| Pose extraction (MediaPipe, normalized keypoints) | Done |
| Open-set gate (3 TCN streams: joint, bone, velocity) | Done |
| 14-class exercise classifier (TCN) | Done |
| Full-session timeline scoring and smoothing | Done |
| Labeled real-session data and locked test set | Done |
| Repetition counting | Done for 5 exercises, approximate (sealed test: 68% of clips within one rep, 39% exact) |
| Calorie estimate (MET-based) | Done, not validated (one fixed MET per exercise, ±35% range) |
| Small local web page (video in, timeline out) | Done, minimal (`ml/app/`); averages the three seeds |
| Full app (accounts, history, phone) | **Not built** |

## 3. The final model

The final model (`ml/artifacts/final_model_v1/`, see its `MODEL_CARD.md`)
comes from Notebook 46. It has three copies trained with different random
seeds (42, 137, 2026); results are the median of the three.

- **Classifier:** the v2 recipe (earlier lab and YouTube clips plus RepCount
  clips, with RepCount capped at 50% of each class) plus continuous windows
  from 11 real follow-along workout videos (Notebook 45).
- **Gate:** retrained with the same data, but long-video windows forced to
  exactly 25% of both the "exercise" and the "unknown" examples (Notebook 46).
- **Fixed settings:** 64-frame windows (4.3 s), gate threshold 0.65,
  mean-probability gate fusion, smoothed decoder (majority vote over 9
  windows, runs under 4 s merged into a neighbor).

**Honest label:** the model was frozen by decision, not by passing every
rule. On the dev videos it missed one predeclared bar: the share of exercise
time wrongly called `unknown` fell by 10.3 points, and 15 were required.

## 4. Results

### Locked long-video test (the main result)

8 full follow-along workout videos (3.9 hours) from creators never used
anywhere else, labeled every second, locked before any model saw them, and
scored only twice in total. Evaluation 2 is the final model.

| Smoothed timeline | V6-F (old best) | v2 | **Final** |
| --- | ---: | ---: | ---: |
| Macro F1 (15 labels) | 32.6% | 32.3% | **47.6%** |
| Accuracy over time | 63.1% | 67.7% | **73.2%** |
| Exercise-block F1 | 0.24 | 0.25 | **0.32** |
| Real exercise time called `unknown` | 55.1% | 65.1% | **39.4%** |
| Rest/transition time called `unknown` | 77.9% | 87.5% | 84.8% |

Final minus V6-F: **+15.0 points Macro F1** (video-bootstrap 95% interval
+2.2 to +25.2). Final minus v2: +15.3 points (+5.7 to +22.9). Both intervals
stay above zero, so the improvement is not luck from these 8 videos.

Per-exercise share of time recognized correctly (V6-F → final):

| Exercise | V6-F | Final |
| --- | ---: | ---: |
| Jumping jack | 82% | 97% |
| Pull-up | 73% | 93% |
| Deadlift | 97% | 92% |
| Push-up | 25% | 80% |
| Bench press | 18% | 79% |
| Squat | 59% | 71% |
| Lat pulldown | 80% | 63% |
| Sit-up | 0% | 49% |
| Lunge | 0% | 44% |
| Lateral raise | 84% | 42% |
| Dumbbell row | 0% | 30% |
| Bicep curl | 31% | 28% |
| Shoulder press | 0% | 23% |
| Tricep extension | 0% | 0% |
| Unknown (rest etc.) | 78% | 85% |

### Other evidence

- **Dev videos** (5 real sessions, used for decisions): smoothed Macro F1
  35.7% vs 25.7% for v2.
- **Internal clip test** (1,971 short clips, reused many times, so it is only
  a "did nothing break" check): Macro F1 about 83% vs 80% for v2 and 81.7% for
  V6-F.

## 5. How we got here

| Step | What happened |
| --- | --- |
| V6-C / V6-F | TCN classifier and multi-stream gate; ~82% on short clips, but only 67% region Macro F1 on a locked 6-creator benchmark. |
| RepCount intake (Notebooks 40-44) | 718 new labeled clips. Big gains on squat and sit-up clips, but failed the sit-up bar on its sealed test. |
| Long-video test (evaluation 1) | First full-session test: both models rejected more than half of real exercise time. The gate was the main failure. |
| Long-video data | 16 more real sessions (8.3 h), labeled every second by rule; user spot-check 95/95 correct. |
| Dev diagnosis | The gate could barely tell exercise from rest (AUROC ~0.63): a data problem, not a threshold problem. |
| Notebook 45 | Added the 11 training videos. Classifier improved a lot; gate did not (it saw 3x more long-video rest than exercise). |
| Notebook 46 | Rebalanced the gate. Best model of the project; frozen as final. |

Failed experiments were kept as evidence, not rewritten as successes. The
full history is in `PROJECT_HANDOFF.md`.

## 6. How the evaluation was kept honest

- Every experiment wrote its pass rule down and pushed it **before** running.
- Data was split by person, creator, and video, so no source appears in both
  training and testing.
- The locked tests were never used for training, thresholds, or labels.
- Every input and output is pinned by SHA-256 checksums; reruns reproduced
  earlier numbers exactly before any comparison.
- Labels follow `ml/data/ANNOTATION_GUIDE.md` (18 written edge-case rules);
  the user checked random samples (44/44 and 95/95 correct).

## 7. Limitations

- **39% of real exercise time is still missed** (called `unknown`).
- **Tricep extension is never recognized.** Lateral raise, curl, row, and
  shoulder press are weak (23-45%). Lateral raise and lat pulldown got worse
  than V6-F.
- The final model **did not pass** the predeclared 15-point gate bar on dev.
- The locked test has only 8 videos, so the uncertainty is wide.
- Results are for single-person, front-facing follow-along videos. Crowds,
  edits, and unusual camera angles were excluded.
- Reps and calories are approximate: reps only for five exercises (sealed test 68% within one rep, 39% exact), calories not validated at all. The web page is minimal and was tested end to end on one 45-second clip, where it recognized the lunges but also mislabeled some intro and rest moments as pull-ups.

## 8. If the project continues

1. More real-session videos for the weak classes (tricep extension, lateral
   raise, curl, row, shoulder press), labeled with the same guide.
2. A new locked test, because this one has been used twice.
3. Better rep counting (per-exercise signals, more classes, data for the eight
   unchecked exercises) and a way to validate calories (for example a wearable
   or lab reference).
4. Per-user settings and saved history in the web page.

## 9. Reproduce

- Final model files and card: `ml/artifacts/final_model_v1/`.
- Final test scorer: `ml/scripts/score_long_video_test_v1_eval2.py`
  (`python ml/scripts/score_long_video_test_v1_eval2.py <repo> <out> --device mps`).
- Training: `ml/notebooks/45_long_video_training_v1.ipynb`, then
  `ml/notebooks/46_long_video_gate_balance.ipynb` (built by
  `ml/scripts/build_notebook45.py` / `build_notebook46.py`).
- Environment: `ml/requirements-macos.txt`.

## Terms used above

- **Pose / keypoints:** body points (shoulders, elbows, hips, knees, and so on)
  found in each video frame.
- **TCN:** temporal convolutional network, a small neural network that reads a
  sequence over time.
- **Gate:** the part that decides "known exercise or not" before the
  classifier names it.
- **Seed:** the starting random number for training; three seeds show the
  result is not luck.
- **Macro F1:** a 0-100% score averaged over every class, so rare exercises
  count as much as common ones.
- **Exercise-block F1:** how well whole exercise sets are found as blocks
  (counted when they overlap the true block by at least half).
- **Bootstrap interval:** the range the true gain likely falls in, estimated
  by resampling the test videos; above zero means a real improvement.
- **AUROC:** how well a score separates two groups (0.5 is a coin flip, 1.0
  is perfect).
- **Dev set:** videos used to make decisions; **locked test:** videos used
  only for the final score.
- **MET:** a standard estimate of how much energy an activity uses.
