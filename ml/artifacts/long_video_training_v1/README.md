# Long-video training v1 — Notebook 45 result (2026-10-27)

One run of `ml/notebooks/45_long_video_training_v1.ipynb` (commit `98c0819`)
on the Mac GPU: v2 recipe plus 9,049 continuous windows from the 11
long-video train videos, 3 seeds, versus frozen v2. Both parity checks
passed. Scored on the 5 dev videos only; no locked or sealed test was read.

**Verdict: dev_fail (1 of 5 criteria failed).** The gate did not improve.

| Criterion (seed medians, smoothed) | Result | Bar | Pass |
| --- | ---: | ---: | :---: |
| Exercise time called unknown, drop | −2.3 pp (54.7 → 57.0%) | ≥ 15 pp | no |
| Macro F1 gain | +6.3 pp (25.7 → 32.0%) | ≥ 5 pp | yes |
| Gain bootstrap 95% CI (5 videos) | +1.8 to +8.4 pp | > 0 | yes |
| Downtime called unknown, change | +6.6 pp | ≥ −10 pp | yes |
| Internal test Macro F1, change | +2.2 pp | ≥ −2 pp | yes |

What improved (time recall, control → treatment): lunge 23 → 53%, shoulder
press 0 → 39%, sit-up 31 → 60%, unknown 75 → 86%; flicker fell from about
1.4 to 0.9 switches per minute. The internal clip test also rose 2.2 points.
What did not: curls (8 → 0%), lateral raises (1 → 2%), rows and tricep
extensions (0%) stay dead, and the gate still rejects more than half of real
exercise time. The classifier learned from the new videos; the gate did not.

Not promoted. Per PLAN.md section 3, one documented follow-up is allowed.
Files: `calorie_long_video_training_v1_report.zip` (models, metrics, dev
timelines; internal `SHA256SUMS.txt` verified), `SHA256SUMS.txt`, `run_log.txt`.
