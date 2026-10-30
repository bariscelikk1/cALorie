# cALorie — exercise recognition from pose

cALorie reads a workout video and labels which exercise is happening, second
by second. It extracts body keypoints with MediaPipe, then two small temporal
neural networks decide whether a moment is a supported exercise and, if so,
which one.

```text
video -> MediaPipe pose -> gate (exercise or unknown) -> 14-class classifier -> exercise timeline
```

**Final result (2026-10-30):** on a locked test of 6 unseen full workouts from new creators (2.6 h), the final
model (v2) reaches **43.5% smoothed Macro F1**, up from 38.7% for the previous final model (+4.8 points, 95%
interval +1.9 to +7.8), and recognizes **62% of weak-exercise time (was 48%)**. On the earlier locked test the
previous model scored 47.6% against 32.6% for the early model. It is a research result, not a production
system: about 30% of real exercise time is still missed, and dumbbell row got worse in the last round.

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
| Rep counting (5 exercises) and MET calorie estimate in the page | Done, approximate (`ml/app/`) |

## Where things are

| Path | What it holds |
| --- | --- |
| [`FINAL_REPORT.md`](FINAL_REPORT.md) | Final results, limitations, next steps |
| [`ml/artifacts/final_model_v2/`](ml/artifacts/final_model_v2/) | Frozen final model, [model card](ml/artifacts/final_model_v2/MODEL_CARD.md), charts, and the slide deck (`cALorie_final_presentation.pptx`) |
| [`ml/artifacts/final_model_v1/`](ml/artifacts/final_model_v1/) | Previous final model (baseline) |
| [`ml/artifacts/long_video_round2_test_v1/eval1/`](ml/artifacts/long_video_round2_test_v1/eval1/) | Final locked-test scoring (v2 vs v1) |
| [`ml/artifacts/long_video_test_v1/eval2/`](ml/artifacts/long_video_test_v1/eval2/) | Earlier locked-test scoring (v1) |
| [`ml/app/`](ml/app/) | The small web page and the video-to-timeline pipeline |
| [`ml/notebooks/`](ml/notebooks/) | Every experiment notebook (01-46) |
| [`ml/scripts/`](ml/scripts/) | Builders, intake, labeling, audit, and scoring scripts |
| [`ml/data/`](ml/data/) | Labels, splits, plans, and the [annotation guide](ml/data/ANNOTATION_GUIDE.md) |
| [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md) | Full chronological experiment log |
| [`archive/legacy_web_app/`](archive/legacy_web_app/) | The old website, worker, and database code (not maintained) |

## Try it on your own video

```bash
pip install -r ml/requirements-macos.txt   # also needs ffmpeg
./ml/app/run_app.sh                        # opens http://localhost:8501
```

A dark, one-page web app that runs only on your computer: upload a workout video (long ones are fine, up to
4 GB), wait while it analyzes (roughly a quarter to a half of the video's length), and get the exercise
timeline, time per exercise, reps for five exercises, and an approximate calorie estimate, plus a CSV download.
Your video is never uploaded anywhere. It is a research prototype: it averages the three final-model seeds
(not scored separately), reps are approximate (68% of unseen clips within one rep), and calories use one fixed
MET per exercise with a ±35% range. Command line: `python ml/app/calorie_pipeline.py VIDEO`.

## Run it on another computer (Docker)

For a teacher's or friend's PC you do not need Python at all, only [Docker Desktop](https://www.docker.com/products/docker-desktop/).
Send them `dist/calorie_docker_bundle.zip` (12 MB; only what the page needs, not the whole repo). They unzip it and run:

```bash
docker compose up --build
```

then open http://localhost:8501. It runs on the CPU (slower than on a Mac) and nothing is uploaded anywhere. Details are in
`ml/app/DOCKER_README.txt` inside the bundle. Note: the Docker files were written and checked file by file, but the image itself has not
been built on a machine with Docker yet.

## Reproduce the final score (v2 vs v1 on the locked round-2 test)

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r ml/requirements-macos.txt
cd ml/scripts
python score_nb47_round2_v1.py ../.. /tmp/eval \
  ../artifacts/long_video_round2_training_v1/nb47_seed42.zip \
  ../artifacts/long_video_round2_training_v1/nb47_seed137.zip \
  ../artifacts/long_video_round2_training_v1/nb47_seed2026.zip --device mps
```

It checks the locked test's checksums and writes the same tables as
`ml/artifacts/long_video_round2_test_v1/eval1/`. Use `--device cpu` without an Apple GPU.

## Data and license notes

Raw videos are never stored in the repository; only pose landmarks, small
review stills, labels, and metrics are kept. RepCount-A clips come from a
public mirror marked `license: other`; YouTube sources are listed in the
data folders. This project makes no medical or fitness-tracker accuracy claim.
