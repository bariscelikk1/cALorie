# Long-video round 3 — plan (approved by the user 2026-11-02)

Status: written 2026-11-02. Nothing is collected or built.

## What the evidence says is weak

- Dumbbell row recall fell 41 -> 22% in round 2, squat 95 -> 88%.
- On a long video, recognition collapsed in the second half (57% -> 23% right, 68% called unknown) where the
  exercises were lying or bent over: skull crushers, kickbacks, single-arm rows, floor press, cross-body curls.
- Pose and training examples are thinnest for lying and bent-over positions.

## Why it cannot be fixed "right now" and still be believed

Both locked long-video tests are spent, so any change made today could only be checked on data we already used
(not allowed). A change is only credible with a **fresh locked test**. So round 3 has two parts: new data and a new test.

## The one change: targeted data (same recipe as Notebook 47)

- **10 new training videos** chosen for lying and bent-over work: skull crushers and tricep kickbacks, single-arm and
  bent-over rows, floor and bench press, reverse fly, with gym and home mix; new creators only (exclusion list extended).
- **6 new test videos**, hash-assigned and locked (fingerprints) before any scoring; scored once.
- Retrain exactly as Notebook 47 (three seeds on a Colab T4, three parts), on all 48 labeled long videos. Nothing else changes.

## Pass rule (set now), against the frozen v2 on the 6 new test videos, smoothed seed medians

1. Macro F1 gain >= 3 points.
2. Mean time recall over dumbbell row, tricep extension, and bench press gains >= 10 points.
3. Exercise time called unknown no more than 3 points worse.
4. Rest time called unknown no more than 5 points worse.

All four must hold for the new model to replace v2; otherwise v2 stays final. The bootstrap interval is reported, not judged.

## Separate, clearly secondary: a decoder idea

Two thresholds (easy to stay in a set, hard to leave it) needs no retraining. It would be scored on the same new test as
an extra, labeled arm and only adopted if it passes the same four rules. It is not mixed into the main change.

## Timeline and cost (realistic)

| Step | Time |
| --- | --- |
| Metadata shortlist (16 videos), your OK | 1-2 h |
| Download, pose, screening (your Mac) | 1-2 h |
| Label 16 timelines, your 10% review | half a day |
| Notebook 48 on Colab T4, three parts | 3-4 h wall time, parallel tabs |
| Score once, report | 1 h |

About 2-3 days. Limits: 6 test videos give a wide interval; weak classes may still lack data; reps and calories untouched.

## Selection log

- 2026-11-02: Exclusion list (`exclusions.csv`, 182 rows, 127 channels) = every earlier source, both locked test sets,
  all round-2 train/test/reject creators, and the creators of the 14 informal short-clip check videos. Selector:
  `ml/scripts/select_long_video_round3_v1.py` (same rules as round 2; weak classes: dumbbell row, tricep extension, bench
  press; train needs each in >=5 videos and >=2 home/>=2 gym, test needs each in >=3 and >=1 home/>=1 gym; backtracking in hash order).
- First pass (24 targeted queries, written before any result): 1,413 hits, 15 eligible creators; train filled (10), test could not (5 left).
- Revision 1 (before any new result was seen): 24 more long-tail queries appended; rules unchanged. 1,566 hits, 23 eligible creators.
- Result: 10 train (5.2 h) and 6 test (3.1 h) videos, `candidates.csv` (`role` column). Selection uses titles and descriptions only; the
  actual footage is checked at screening. Awaiting the user's OK before any download.
- **Scale-down (2026-11-02, user: "no time for 16, just a couple of videos for the weak exercises"):** the full download was stopped
  before any video finished; nothing was kept. Round 3 becomes a **mini round of 6 videos taken from the approved list**, chosen from the
  metadata alone (before any footage was seen) as the ones covering the most weak exercises: **train** `fEuM1XWZ068`, `BZiRx8zVPY8`,
  `7xDmlGYrfww`, `HlnCRJ2Z-i8`; **test** `WopbPBumelc`, `dVtAnYQynbU`. Two test videos are too few for the pass rule above to be
  decisive; the result is **informational** (reported with its limits, not used to replace v2 unless the user decides otherwise).
- **Second scale-down (2026-11-02, user: "for now only 3: 2 train, 1 test"):** the 6-video download was stopped and cleaned; round 3 now
  starts with **3 videos**: train `fEuM1XWZ068` and `BZiRx8zVPY8` (both list row, triceps, and bench press), test `WopbPBumelc`
  (the same three). One test video is an anecdote, not a test; any result is informational only.

## Execution log and predeclared training run (2026-11-02, written before any training or scoring)

- Done: 3 videos downloaded and pose-extracted, screened (all kept, see `screening.csv`), labeled second by second with
  `ml/data/ANNOTATION_GUIDE.md`, flagged rows settled by written rule (`finalize_long_video_round3_v1.py`), test video locked
  (`LOCK.json`), 26-segment 10% review sample drawn. **The user chose to skip the review**, so the sample stays unchecked
  (`user_verdict` empty) and these labels are less verified than rounds 1-2. fEuM1XWZ068 minutes 12-30 were labeled from
  10 s frames and its regular 60 s timer cycle, not from the 2 s pages.
- Run: **Notebook 48** = Notebook 47's recipe and data **plus the 2 round-3 train videos** (34 labeled long videos), 3 seeds
  (42, 137, 2026), Colab T4 in three parts (`ml/notebooks/48_long_video_round3_seed*.ipynb`, built by
  `ml/scripts/build_notebook48.py`). Control = the current final model v2 (Notebook 47). Scoring: `ml/scripts/score_nb48_round3_v1.py`,
  once, on the single locked test video `WopbPBumelc` with the same scorer, decoder, and threshold as every earlier evaluation.
- Rule (all four must hold for Notebook 48 to be called better than v2; **informational only, one test video**):
  1. smoothed Macro F1 gain >= 2 pp (seed medians);
  2. mean time recall over the weak exercises present in the test video (dumbbell row, tricep extension, bench press, bicep curl,
     shoulder press) not worse than 5 pp;
  3. supported exercise time called unknown no more than 3 pp worse;
  4. rest/transition time called unknown no more than 5 pp worse.
  The internal clip-test Macro F1 is reported only. Nothing is tuned from the result; if the rule fails, v2 stays the final model.
  Even if it passes, one video is an anecdote: the report says so and v2 stays the presented model unless the user decides otherwise.
