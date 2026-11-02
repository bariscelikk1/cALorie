# Long-video round 3 — plan (DRAFT, awaiting approval)

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
