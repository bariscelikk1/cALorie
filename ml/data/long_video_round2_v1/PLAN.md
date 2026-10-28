# Long-video round 2 — plan (DRAFT, awaiting approval)

Status: written 2026-10-28. Nothing is collected or built. Project deadline
2026-11-02, so this is a 4-day plan with a fallback.

## Why this, and what it can promise

The final model (Notebook 46) has two known weaknesses: 39% of real exercise
time is rejected, and the weak classes (tricep extension 0%, shoulder press
23%, row 30%, curl 28%, lateral raise 42%) have very little real-session data
(tricep extension: 11 min of labeled video in total). Earlier rounds showed
that more real-session data helped every time, while architecture, threshold,
and sampler tweaks did not. So round 2 changes **only the data**.

It cannot promise a better model. It can promise an honest answer on a fresh
test, with the current final model kept as the fallback.

## 1. New data (14 videos, about 7 hours)

- **8 new training videos** and **6 new test videos**, from creators never
  used before (all earlier creators are on the exclusion list). Same rules and
  scripts as before (`select_long_video_train_v1.py`, `long_video_intake_v1.py`):
  real person, one performer, no heavy editing, raw video deleted after pose.
- **Coverage for the 8 training videos:** at least 4 videos each showing
  tricep extension, lateral raise, bicep curl, dumbbell row, and shoulder
  press (target: 20+ new minutes of tricep extension and of lateral raise).
- **Test videos (6):** same mix, hash-assigned before labeling, locked before
  any model is scored, scored once.
- **Labeling:** second by second with the annotation guide (rules 1-18), as
  before. You spot-check a 10% hash sample (about 50 segments in total, about
  20 minutes).

## 2. The one change: more training data

Same recipe as Notebook 46, nothing else tuned (no dev set left to tune on, so
nothing is tuned):

- Train on **all long-video data we have labeled**: the 11 earlier train
  videos, the 5 earlier dev videos, the 8 earlier test videos (labeled and no
  longer a fair test), and the 8 new training videos. That is 32 videos, about
  3x the long-video data of Notebook 46.
- Same v2 pool (short clips + RepCount), 50% RepCount cap, long-video windows
  at 25% of each gate class, threshold 0.65, three seeds, early stopping on the
  V6-A validation split.
- This is **Notebook 47**. The old Notebook 46 model stays frozen as the
  fallback and the baseline.

## 3. Test and pass rule (set now)

One scoring of the **6 new test videos**, smoothed decoder, seed medians, same
scorer as evaluation 2. Compare Notebook 47 against the frozen Notebook 46:

1. Smoothed Macro F1 improves by at least 3 points.
2. Mean time recall over the five weak classes (tricep extension, lateral
   raise, curl, row, shoulder press) improves by at least 10 points.
3. Exercise time called unknown is no more than 3 points worse.
4. Rest called unknown is no more than 5 points worse.

All four must hold for Notebook 47 to replace Notebook 46 as the final model.
Otherwise Notebook 46 stays final and Notebook 47 is reported as a result.
A video-level bootstrap interval is reported but, with 6 videos, will be wide;
it does not decide the outcome. Old locked test (8 videos) is not re-scored on
Notebook 47: it is training data now.

## 4. Timeline

| Day | Work |
| --- | --- |
| Oct 28-29 | Exclusions, shortlist, your OK on the list; download and pose for 14 videos; screening |
| Oct 29-30 | Label 14 timelines; your 10% spot-check |
| Oct 31 | Notebook 47: build, dry run, train 3 seeds (about 1.5-2 h) |
| Nov 1 | Score once on the new test; update the report and the web page's model |
| Nov 2 | Buffer and final push |

Fallback: if labeling or training slips past Nov 1, the project ships with
Notebook 46 exactly as it is today.

## 5. Limits

- Six test videos give a wide interval; a small gain may be unprovable.
- Weak classes may still be short on data even at 3x.
- Training on the old test and dev videos means there is no untouched
  benchmark left except the 6 new videos.
- Reps and calories are not touched.
