# cALorie — exercise recognition from pose

cALorie reads a workout video and labels which exercise is happening, second
by second. It extracts body keypoints with MediaPipe, then two small temporal
neural networks decide whether a moment is a supported exercise and, if so,
which one.

```text
video -> MediaPipe pose -> gate (exercise or unknown) -> 14-class classifier -> exercise timeline
```

**Final result (2026-10-28):** on a locked test of 8 unseen full workout
videos (3.9 h), the final model reaches **47.6% smoothed Macro F1** and
**73% accuracy over time**, versus 32.6% for the previous best model
(+15.0 points, 95% interval +2.2 to +25.2). It is a research result, not a
production system: 39% of real exercise time is still missed, and tricep
extension is never recognized.

**Read the [final report](FINAL_REPORT.md)** for results, limits, and history.

## Supported exercises

bench press, bicep curl, deadlift, dumbbell row, jumping jack, lat pulldown,
lateral raise, lunge, pull-up, push-up, shoulder press, sit-up, squat, tricep
extension. Everything else is `unknown`.

## Status

| Part | Status |
| --- | --- |
| Pose extraction, gate, classifier, timeline scoring | Done |
| Labeled real-session data and locked test | Done |
| Small local web page (video in, exercise timeline out) | Done: `ml/app/` |
| Repetition counting, calorie estimate | Not built |

## Where things are

| Path | What it holds |
| --- | --- |
| [`FINAL_REPORT.md`](FINAL_REPORT.md) | Final results, limitations, next steps |
| [`ml/artifacts/final_model_v1/`](ml/artifacts/final_model_v1/) | Frozen final model and [model card](ml/artifacts/final_model_v1/MODEL_CARD.md) |
| [`ml/artifacts/long_video_test_v1/eval2/`](ml/artifacts/long_video_test_v1/eval2/) | Final locked-test scoring |
| [`ml/app/`](ml/app/) | The small web page and the video-to-timeline pipeline |
| [`ml/notebooks/`](ml/notebooks/) | Every experiment notebook (01-46) |
| [`ml/scripts/`](ml/scripts/) | Builders, intake, labeling, audit, and scoring scripts |
| [`ml/data/`](ml/data/) | Labels, splits, plans, and the [annotation guide](ml/data/ANNOTATION_GUIDE.md) |
| [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) | Full chronological experiment log |
| [`archive/legacy_web_app/`](archive/legacy_web_app/) | The old website, worker, and database code (not maintained) |

## Try it on your own video

```bash
pip install -r ml/requirements-macos.txt   # also needs ffmpeg
streamlit run ml/app/app.py
```

Upload one video of one person with the whole body in view. The page shows the
exercise timeline, time per exercise, and a CSV download. It runs on your
computer only. It is a research prototype: it averages the three final-model
seeds (checked on the dev videos: 35.5% Macro F1 vs 35.7% for the seed median),
it mislabels some intro and rest moments, and it does not count reps or
estimate calories. Command line: `python ml/app/calorie_pipeline.py VIDEO`.

## Reproduce the final score

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r ml/requirements-macos.txt
cd ml/scripts
python score_long_video_test_v1_eval2.py ../.. /tmp/eval2 --device mps
```

It checks the locked test's checksums, rescoring the old models must match
evaluation 1, and it writes the same tables as
`ml/artifacts/long_video_test_v1/eval2/`. Use `--device cpu` without an Apple
GPU.

## Data and license notes

Raw videos are never stored in the repository; only pose landmarks, small
review stills, labels, and metrics are kept. RepCount-A clips come from a
public mirror marked `license: other`; YouTube sources are listed in the
data folders. This project makes no medical or fitness-tracker accuracy claim.
