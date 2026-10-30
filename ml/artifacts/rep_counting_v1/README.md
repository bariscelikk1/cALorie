# Rep counting v1 (2026-10-28)

Generic peak counter (`ml/app/reps_and_calories.py`): first principal component
of the segment's hip-centered keypoints, smoothed, then peak counting. No model
training. Scored by `ml/scripts/score_rep_counting_v1.py` on RepCount-A clips
that have published human rep counts (our extracted pose, true class used, so
this tests the counter and not the classifier). Plan: `ml/app/REPS_AND_CALORIES_PLAN.md`.

Order: grid search of 96 settings on the 73 **dev** clips (`tuning_grid_dev.csv`);
the top setting was frozen and committed (315ec17); then train clips scored once
as a sanity check; then the **sealed-test** clips scored once.
Frozen: smoothing 0.6 s, minimum gap 0.4 s, minimum prominence 40%.

| Role | Clips | Exact count | Within 1 rep | Mean abs error |
| --- | ---: | ---: | ---: | ---: |
| dev (tuned on) | 73 | 53% | 80% | 1.9 |
| train (sanity) | 326 | 50% | 75% | 2.9 |
| **sealed test (once)** | **94** | **39%** | **68%** | **2.0** |

Sealed test within-one-rep by class: sit-up 79%, squat 83%, bench press 62%,
jumping jack 67%, push-up 58%, pull-up 56%. Dev was optimistic by about 11
points, as expected after tuning on it.

Rule for the page, decided on dev before the sealed test (at least 50% of dev
clips within one rep): reps are shown for jumping jack, pull-up, push-up,
sit-up and squat. Bench press (42% on dev) and the eight classes with no
RepCount clips show "reps not validated". The sealed result did not change that
list (decision stays as set on dev).

Limits: clips are short single-exercise videos, not full sessions; a wrong
exercise label gives wrong reps; counts can be off by several reps on long sets.
Files: `summary_*.csv`, `per_clip_*.csv`, `tuning_grid_dev.csv`, `SHA256SUMS.txt`.
