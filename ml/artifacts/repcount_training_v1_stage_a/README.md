# RepCount-A training v1, stage A — Notebook 42 result (2026-10-27)

`calorie_repcount_training_v1_stage_a_report.zip` is the unchanged output of the
single predeclared stage-A run (SHA-256 `d74579f8c62ba660796b73feb7e49a45a735bc0191e3d6ce3d67f19f0d690de8`; internal checksums verified).
It ran on the user's Mac GPU (MPS) at commit `b14d141`. Both parity checks
passed before training. The sealed test and the locked benchmark were not read.

**Verdict: `stage_a_fail`.** Six of seven criteria passed. The internal-test
guard failed by 0.24 points: end-to-end Macro F1 was 81.64% for the control
and 79.40% for the treatment (−2.24 pp; the limit was −2.00). Per the plan,
stage B does not run and the sealed test stays unseen.

| RepCount dev, 107 clips (seed median) | Control (frozen V6-F) | Treatment |
| --- | ---: | ---: |
| Macro F1 over 7 labels | 61% | 86% (+24.6 pp; 95% CI +17.7 to +33.4) |
| Sit-up recall | 0% | 80% |
| Squat recall | 69% | 88% |
| Unknown rejection | 82% | 94% |
| Real exercises called unknown | 27 | 11 |

Internal-test per-class recall, treatment minus control (means): deadlift
+12.8, lat pulldown +9.5, push-up +11.1, sit-up −15.4, pull-up −16.7,
unknown −4.6, others within ±2. The mean recall of the 8 uncovered classes
rose (85.4% to 88.1%).

**Reading:** the new data fixed the target failures on new footage by a
wide, group-robust margin. It also shifted what the model calls a sit-up or
pull-up toward RepCount's style, at some cost to the original sources'
sit-ups and pull-ups, and slightly loosened unknown rejection on the
internal set. This is an honest fail under the predeclared rule, not a
success. No rerun or tuning follows from these numbers.
