# RepCount-A training v2, stage A — Notebook 43 result (2026-10-27)

`calorie_repcount_training_v2_stage_a_report.zip` is the unchanged output of the
single predeclared stage-A run (SHA-256 `83737851a0349e746a948bf1600095d494f588a1f3086e1548bd32b8fc131add`; internal checksums verified),
run on the user's Mac GPU at commit `dbb88c6`. Both parity checks passed.
The sealed test and locked benchmark were not read. The only change from v1:
RepCount is capped at 50% of each class's sampler mass.

**Verdict: `stage_a_pass`.** All seven predeclared criteria held.

| RepCount dev, 107 clips (seed median) | Control (frozen V6-F) | v2 treatment |
| --- | ---: | ---: |
| Macro F1 over 7 labels | 61.4% | 85.4% (+24.0 pp; 95% CI +17.2 to +31.8) |
| Sit-up recall | 0% | 90% |
| Squat recall | 69% | 81% |
| Push-up / pull-up / bench / jumping jack | 78 / 50 / 42 / 71% | 89 / 75 / 58 / 86% |
| Unknown rejection | 82% | 91% |
| Real exercises called unknown | 27 | 11 |

Internal 1,971-window test (means): end-to-end Macro F1 81.64% to 80.03%
(−1.61 pp, within the 2.00 limit). Sit-up recall 98.2% to 99.3% (v1 lost
15 points here). Unknown recall 88.4% to 89.5%. Uncovered-class mean recall
85.4% to 85.0%. Remaining internal losses: squat −4.5 pp and pull-up −8.3 pp
(4 windows).

**Caveat:** the dev clips were also used to judge v1, so this dev score is
slightly optimistic. Per the plan, the final judgment is stage B: one
scoring of these frozen models on the unseen sealed test (140 clips), under
the same rule. It needs the user's go-ahead.
