# Long-video training v1 — plan (approved 2026-10-27)

Status: approved 2026-10-27. Data collected and labeled; section 2 done (see `ml/artifacts/long_video_train_v1/dev_diagnosis_v1/`).

## What evaluation 1 showed (locked long-video test, measurement only)

- Both models reject more than half of real exercise time as `unknown`
  (V6-F 55%, v2 65%). On full sessions, the gate is the main failure.
- Five classes score 0% for both: sit-up, dumbbell row, lunge, shoulder
  press, tricep extension. v2 also lost curls (31→7%) and lateral raises
  (84→7%).
- Training-pool check: those classes come almost entirely from **one lab
  dataset, MM-Fit**. MM-Fit share: sit-up 100%, row 95%, tricep 90%, shoulder
  press 89%, lunge 78%, lateral raise 84%, curl 76%. This is the same source
  memorization that RepCount fixed for its 6 classes.
- The training data is short trimmed clips. Real sessions have previews,
  overlays, timers, rests, and camera cuts, and the gate has never trained
  on continuous footage like that.

The locked test may not be used to diagnose or tune. Everything below uses
new data; the locked set is only consulted once at the end (evaluation 2).

## 1. New long-video data: train and dev (not test)

- **16 new follow-along videos**, 20–45 min each, about 8 hours. Selection
  uses the same rules and scripts as the test set: new creators only (the
  test channels are now also excluded), real person, one performer,
  screened for talking, edits, crowds, and animation.
- **Coverage targets** chosen for the weak classes: across the set, each of
  curl, row, lunge, shoulder press, tricep extension, lateral raise, and
  sit-up must appear in at least 4 videos (from titles, descriptions,
  chapters). A mix of home and gym.
- **Roles by video, fixed by hash before labeling:** 11 train and 5 dev. Dev is
  used for every decision (diagnosis, decoder, threshold). Train is used only
  for training.
- **Labeling:** same method as the test set (every second, 2 s pages, the 10
  rules). User second review of a 10% hash sample. Expected user time: about
  1 hour.

## 2. Diagnose on dev first (before any training)

Score V6-F and v2 on the 5 dev videos and report: gate-score distributions
for exercise vs downtime time; per-class confusion; where the rejected time
falls (overlays, side views, small figures, specific classes). This tells us
whether the gate is miscalibrated (a threshold problem) or truly blind (a
data problem). It is reported to the user before section 3 runs.

## 3. Experiment: one change

**Change:** add the 11 train videos' continuous labeled windows (every 32
frames) to the training pool and retrain the classifier and the 3 gates,
with the v2 recipe (RepCount data, 50% cap). Long-video windows enter the
sampler like any other source group, one group per video. Everything else is
fixed: architecture, features, threshold 0.65, early stopping on V6-A
validation.

**Arms:** v2 (control) vs v2 + long-video train (treatment), 3 seeds each.

**Predeclared pass rule on dev (5 videos, smoothed decoder):**
1. Supported exercise time called `unknown` drops by at least 15 points
   versus control.
2. Smoothed 15-label Macro F1 improves by at least 5 points, with a
   video-level bootstrap interval above zero.
3. Rest/transition time called `unknown` stays within 10 points of control.
4. Internal clip test Macro F1 is no more than 2 points below control.
5. RepCount sealed-test numbers are not re-scored (that set is spent).

**If it passes:** score once on the locked long-video test (evaluation 2,
same scorer and metrics as evaluation 1).
**If it fails:** report it; one documented follow-up is allowed (for
example, a dev-chosen threshold), then stop.

## 4. Limits

- 11 training videos is a small amount of new data. It can show direction,
  not finish the job.
- The 0% classes may need more sources than 11 videos give. Section 2 will
  show which classes still lack examples.
- Rep counting and calories are still not built; this targets recognition
  only.
- Same evidence boundary as before: raw video is deleted, and stills and
  pose stay in the repo.

## Effort

About 8 hours of video: roughly 4 hours of local processing, about 160
label pages (my side), about 1 hour of your review, then about 1 hour of
training on the Mac GPU.

## Selection log

- 2026-10-27: The exclusion list (`exclusions.csv`) covers 55 channels:
  every earlier source, the 8 locked-test creators, and the 2 animated test
  channels. Screened-out test videos are never reused. The first 12 queries
  gave 9 eligible videos (201 of 302 hits were from already-used creators).
- Revision 1: 12 more queries appended (514 hits). 16 videos are picked
  greedily in hash order, meeting every coverage rule (`selected=True` in
  `candidates.csv`). Awaiting the user's OK before download.
- Screening (user rule: replace mostly-talking, edited, multi-person, or
  animated videos with the next valid set by the same rule): rejected
  `2lGaGusBPEI` (rest-timer screens, talking, cuts), `JofVPb0wtv8` and
  `UKfNi0IIndA` (two performers, same channel), `mpZBFMfOfAw` (three
  performers), and `wRR8HUMdh00` (split screen with a second figure). Every
  decision is in `screening.csv`.
- Revision 2: after those rejects no valid set had 4 lateral-raise videos;
  3 lateral-raise queries appended (549 hits). The new 16 meet every rule.
- Operational note: one lane was stopped by mistake (a process match on a
  rejected ID); its 3 unprocessed videos were rerun. No data was lost.
- Final 16 (all screened and kept; 6 rejects replaced by rule): 8.31 h.
  Roles by hash (`roles.csv`, salt `long_video_train_v1_roles`): **dev**
  `Ferc_0UlN4g`, `R4S-eSPDXIg`, `5vmnb_T_YH4`, `uawtllYyD5g`, `_cqwrzDHXsc`;
  the other 11 are **train**. Evidence is in
  `ml/artifacts/long_video_train_v1/`. Next: label all 16 timelines.

## Section 3 implementation details (fixed 2026-10-27, before any training)

Notebook 45 (`ml/notebooks/45_long_video_training_v1.ipynb`) is Notebook 43
(the v2 recipe) with one change: the 11 train videos' windows join the pool.

- **Windows:** 64 frames every 32 frames from frame 0 over each train video.
  A window's label is the majority `current_tcn_label` over its frames; it is
  kept only if that label covers at least 75% of the frames and at least 50%
  of the frames have a detected pose. No phase windows are added.
- **Sampler:** one source group per video (`longvideo:<id>`), same
  square-root group tempering; the 50% RepCount cap is unchanged and applied
  after, as in v2. Long-video windows go into both the gate pool (supported
  vs unknown) and, if supported, the classifier pool.
- **Control:** the frozen v2 seeds 42, 137, 2026 from Notebook 43 (same recipe,
  same seeds). Parity: their internal-test Macro F1 must reproduce Notebook 43
  within 0.003, and their dev numbers must reproduce the dev diagnosis within
  0.005.
- **Scoring:** the evaluation-1 full-session scorer
  (`score_long_video_test_v1.py`), smoothed decoder, pooled over the 5 dev
  videos; seed medians per arm. The bootstrap resamples the 5 dev videos
  (2,000 draws). Internal-test rule uses the seed mean, as in v2.
- Early stopping stays on V6-A validation; dev, the locked tests, and the
  RepCount sealed test are never used for training or stopping.

## Follow-up 1: gate balance (approved by the user 2026-10-28)

Chosen after Notebook 45 failed the gate criterion, so it is a post-hoc
follow-up and is labeled that way. The plan allows exactly one; after it,
this arc stops whatever the result.

**Evidence behind it.** In Notebook 45's gate sampler, long-video windows
held 29.7% of the `unknown` class but only 8.9% of the `supported` class. The
gate mostly learned "this kind of footage means unknown".

**One change (Notebook 46).** After the existing weights and the 50% RepCount
cap, rescale the gate sampler so long-video windows hold exactly **25%** of
each gate class (supported and unknown); the other windows in each class are
scaled to keep the class mass. RepCount stays under its 50% cap (expected
about 41% of supported and 45% of unknown); the notebook asserts both.

**Fixed:** the Notebook 45 classifiers are reused frozen (they passed);
only the 3 gates are retrained per seed (42, 137, 2026). Same windows,
features, augmentation, threshold 0.65, fusion, and early stopping on V6-A
validation.

**Pass rule:** identical to section 3, against the same frozen v2 control on
the 5 dev videos (smoothed, seed medians):
1. Exercise time called `unknown` drops by at least 15 points.
2. Macro F1 gains at least 5 points, with a 5-video bootstrap CI above zero.
3. Downtime called `unknown` stays within 10 points of control.
4. Internal test Macro F1 is no more than 2 points below control.
Also reported, not judged: the same numbers against Notebook 45.

**If it passes:** evaluation 2, once, on the locked long-video test.
**If it fails:** report it and close this arc; the next step would need new
data or a new design, planned separately.
