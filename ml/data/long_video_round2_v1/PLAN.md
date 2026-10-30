# Long-video round 2 — plan (approved by the user 2026-10-28)

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

## Selection log

- 2026-10-28: Exclusion list (`exclusions.csv`, 130 rows, 75 channels) = every
  earlier source, the 8 locked-test videos and creators, the 16 round-1 train/dev
  videos, and the 5 round-1 screening rejects (kept in `screening.csv`).
  Selector: `ml/scripts/select_long_video_round2_v1.py`.
- Saved round-1 search results leave only 10 eligible creators (train 8 / test 2
  picked, five weak classes unmet). Revision 1: 24 queries appended
  (aimed at tricep, lateral raise, curl, row, shoulder press; written before any
  new result). 835 hits, 15 eligible creators: still short.
- Revision 2: 26 more long-tail queries, written before any new result (494 of
  835 earlier hits were already-used creators). 1,135 hits, 27 eligible creators,
  13 of them list lateral raises.
- Selector fix: plain hash-order greedy missed a valid set, so the search
  now backtracks in the same hash order (first valid set by hash rank). Rules
  unchanged: train needs each weak class in >=4 videos and >=2 home/>=2 gym;
  test needs >=3 per weak class and >=1 home/>=1 gym; one video per channel,
  test never shares a channel with train.
- Result: 8 train (4.4 h) and 6 test (2.6 h) videos, `candidates.csv` (`role`
  column). Awaiting the user's OK before any download.

## Notebook 47 (built 2026-10-28, offline; passed a local dry run)

`ml/scripts/build_notebook47.py` -> `ml/notebooks/47_long_video_round2.ipynb`.
Notebook 46's sampler (v2 pool, 50% RepCount cap, long-video windows at 25% of
each gate class) with one change: it trains on every labeled long video. The
classifier and the three gates are retrained, three seeds. Control: the frozen
Notebook 46 model (internal-test parity within 0.003 is asserted). The old
locked long-video test v1 videos are training data from here on (plan
section 2); the 6 round-2 test videos are verified against `LOCK.json` and can
never be in the training list. The notebook runs the predeclared four-part rule
and refuses a real run until round-2 data and `LOCK.json` are in the repository
(a round-1 dev stand-in exercises the code path in a dry run only).
- **Download and screening (2026-10-28, user approved):** 14 videos downloaded
  in 4 lanes (`ml/scripts/long_video_intake_v1.py --prefix long_video_round2_v1`),
  screened at 1 frame per 10 s (`screening.csv`). Reject: **`kla05C_4eio`**
  (VitruvianPhysique, test): a vlog, mostly talking to camera with many cuts and
  unrelated meme and movie clips. Replacement by the same rules (the other five
  test videos stay fixed; the first eligible creator in test-pool hash order
  that completes the coverage needs): **`o3xDawAnb-M`** (PushYourself w/ Tony
  Jay, 21 min, home; lists row, lateral raise, shoulder press, triceps, curl).
- Reject: **`1Mbuyc5uW4s`** (train): a gym vlog, the creator talks to camera
  for long stretches with many handheld angles and cuts. Replacement by the same
  rules (the other seven train videos stay fixed; first eligible creator in
  train-pool hash order that completes the coverage needs, which was one more
  lateral-raise video): **`74B9SxqtMug`** (Tiffany's Training, 25 min, home;
  curl, lateral raise, triceps).
- Reject: **`tPnVxUmFcqI`** (train): a motivational montage of archival
  bodybuilding clips (dozens of different people, constant cuts); metadata
  looked like a workout but the footage is not a follow-along. Replacement by
  the same rules (the other seven train videos stay fixed; coverage needs were
  already met, so the first eligible creator in train-pool hash order):
  **`Xyea2DCicKU`** (Matt Jones, 23 min, home; squat, curl, deadlift, row, lunge).
- **Labeling and review (2026-10-28):** all 14 timelines labeled second by second
  (704 segments, 6.9 h; strict audit clean). User spot-check of a 10% hash sample
  (71 segments, 42 train and 29 test): 71/71 correct. User approved rules 19-23
  (`ANNOTATION_GUIDE.md`) and accepted the 12 pose-identified `74B9SxqtMug`
  segments; all 43 flagged rows adjudicated by
  `ml/scripts/adjudicate_long_video_round2_v1.py`. The 6 test videos are locked in
  `LOCK.json` (labels and evidence hashes) before any scoring. Evaluations used on
  this test set: 0. Next: Notebook 47.
- **Evaluation 1 on the round-2 test (predeclared 2026-10-30, before scoring):** the three Notebook 47 seed
  ZIPs (`ml/artifacts/long_video_round2_training_v1/`, trained on a Colab T4; checksums, lock hashes, and
  train/test disjointness verified) against frozen Notebook 46, scored once with
  `ml/scripts/score_nb47_round2_v1.py` using the four-part rule in PLAN.md section 3. Evaluations used on
  this test set after this run: 1.
- **Evaluation 1 result (2026-10-30):** Notebook 47 replaces Notebook 46: all four criteria pass (Macro F1
  +4.8 pp, bootstrap interval +1.9 to +7.8; weak-class recall 48.3 → 61.7%; exercise time called unknown
  35.0 → 30.1%; rest called unknown +0.2 pp). Dumbbell row recall fell 41 → 22%. Details:
  `ml/artifacts/long_video_round2_test_v1/eval1/README.md`. The test set is spent; do not tune on it. Final
  model v2: `ml/artifacts/final_model_v2/`.
