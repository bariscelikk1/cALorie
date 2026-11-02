# Improvement experiments v1: protocol and pass rules (written before any run)

Date: 2026-11-02. Status: **development evidence only.** Final model v2 stays the presented model. Nothing here is a locked-test
result, and nothing here can promote a model (a fresh locked test of new videos would be needed).

## Why

v2 calls 30-46% of real exercise time `unknown`. Three research reports (Reddit found nothing; internet; academic) mostly agree the gate
decision and the decoder are the weak part, not the amount of data. Their ideas, ranked by cost, are tested here.

## Data and folds

- 44 labeled long videos (all annotation files in `ml/data/long_video_*/annotations/`), from 44 different channels, so grouping
  by creator is the same as one video per group.
- `folds.csv`: 5 folds (9, 9, 9, 9, 8 videos), made by a fixed rule (largest groups first into the lightest fold, ties by SHA-256
  of "improvement_cv_v1" + channel). Do not re-draw folds after seeing any result.
- Out-of-fold scores: for fold k, train the same recipe (Notebook 48 flow) on the other 4 folds plus the short-clip pool, then
  save per-window raw outputs for fold k with `ml/scripts/extract_window_scores.py`. Every video is then scored by a model that never saw it.
- Already done and verified: `extract_window_scores.py` reproduces the saved v2 timelines on the two round-3 test videos
  exactly (0 of 4,654 and 0 of 3,376 windows differ, all 3 seeds).

## What each experiment changes (all on saved scores, no retraining unless stated)

| ID | Change | Retrain |
| --- | --- | --- |
| E1 | Two thresholds (enter high, leave low) and a per-video threshold | no |
| E2 | Viterbi decoding (15 states, one switch cost) instead of the 9-window vote | no |
| E3 | Score the 3-seed average (what the web page uses) | no |
| E4 | Energy score on the logits as the gate score | no |
| E5 | Explicit rest/other output in the classifier | yes |

Run order: E1, E2, E1+E2, E3, E4, then E5 only if E1 and E2 are scored. Parameters (cutoffs, switch cost) are chosen leaving the
scored video out.

## Pass rules (fixed now)

Baseline = the same out-of-fold models with the old rule (mean gate score, 0.65 cutoff, 9-window vote).
E1, E2, E1+E2 pass only if all hold, pooled over the 44 videos, seed medians:

1. Smoothed Macro F1 at least +2 points over baseline.
2. Exercise time called `unknown` down at least 5 points.
3. Rest/transition time called `unknown` no more than 5 points worse.
4. Macro F1 better than baseline in at least 60% of the videos.

E3 passes if the averaged model's Macro F1 is at least the seed median and its seed spread (max minus min) shrinks.
E4 passes if pooled AUROC (exercise vs non-exercise) rises at least 0.03 over the current gate score; otherwise it is dropped.
E5 passes if Macro F1 is up at least 3 points and the mean recall of the weak classes (tricep extension, lateral raise, bicep curl,
dumbbell row, shoulder press, bench press) is not worse than 3 points.

The video-level bootstrap interval is reported, not judged. If nothing passes, v2 stays and we say so.

## What can and cannot be claimed

- Can: "variant A beats the old rule on held-out videos, interval X."
- Cannot: a locked-test result, generalization to new gyms or cameras, or that a winner chosen on this same pool is unbiased.
- Cannot: use the old v2 models here. They trained on these videos.

## E6: wide residual network on pose (Notebook 50), rule fixed 2026-11-02 before any run

Change: classifier and the three gates use WideTCN (widths 128-256-384-512, about 2.85 M parameters, 10x the current model);
everything else is identical to Notebook 49 (same 5 folds, seed 42, data, recipe, decoder). Notebook 49 is the control.
Both are scored on the same held-out videos with the old decoder (mean gate score, 0.65 cutoff, 9-window vote). Pass only if all hold:

1. Pooled out-of-fold Macro F1 at least +2 points over Notebook 49.
2. Mean recall of the weak classes (tricep extension, lateral raise, bicep curl, dumbbell row, shoulder press, bench press)
   not worse than 3 points.
3. Exercise time called `unknown` not worse than 3 points.
4. Rest/transition time called `unknown` not worse than 5 points.
5. Better Macro F1 than Notebook 49 in at least 60% of the 44 videos.

One seed per fold, so a gain under about 2-3 points cannot be told apart from seed noise; the rule is deliberately not looser. If it fails,
we keep the small model and say that size did not help. The video-bootstrap interval is reported, not judged.
