# Long-video follow-up 1: gate balance — Notebook 46 result (2026-10-28)

One run of `ml/notebooks/46_long_video_gate_balance.ipynb` (commit `299f884`)
on the Mac GPU: Notebook 45 classifiers frozen, 3 gates retrained with
long-video windows at exactly 25% of each gate class. Parity passed. Scored on
the 5 dev videos only; no locked or sealed test was read. Post-hoc follow-up
(the only one the plan allows).

**Verdict: dev_fail (1 of 5 criteria), but close.**

| Criterion vs frozen v2 (seed medians, smoothed) | Result | Bar | Pass |
| --- | ---: | ---: | :---: |
| Exercise time called unknown, drop | 10.3 pp (54.7 → 44.3%) | ≥ 15 pp | no |
| Macro F1 gain | +10.0 pp (25.7 → 35.7%) | ≥ 5 pp | yes |
| Gain bootstrap 95% CI (5 videos) | +3.4 to +11.5 pp | > 0 | yes |
| Downtime called unknown, change | −3.8 pp | ≥ −10 pp | yes |
| Internal test Macro F1, change | +3.1 pp | ≥ −2 pp | yes |

Versus Notebook 45 (reported only): Macro F1 +3.7 pp, exercise called unknown
−12.7 pp, downtime called unknown −10.4 pp. The balance fixed the direction
of the gate error.

Time recall, v2 → Notebook 46: curl 8 → 45%, row 0 → 42%, lunge 23 → 56%,
sit-up 31 → 64%, shoulder press 0 → 29%, deadlift 32 → 47%, bench 59 → 66%;
push-up stays 95%; squat fell 73 → 59%; lateral raise (4%) and tricep
extension (0%) remain unsolved.

Per the plan, this arc is closed. Not promoted.
