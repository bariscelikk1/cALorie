# RepCount-A training v2, stage B — sealed test (Notebook 44, 2026-10-27)

`calorie_repcount_training_v2_stage_b_report.zip` is the unchanged output of the
single sealed-test scoring (SHA-256 `ae690cb73a94e35449ee7ebfb0677c4eaaf7a9161f4ccccc88e807b70c437c7d`; internal checksums verified), run on
the user's Mac GPU at commit `74d80ae`. No training: the frozen v2 stage-A
models reproduced their stage-A internal-test scores before scoring. The
sealed test (140 clips, 111 role groups) was read for the first and only
time. The locked benchmark was not read.

**Verdict: `stage_b_fail`.** Six of seven criteria held; sit-up recall did
not. The seed median was 42.9% against a required 50% (per seed: 36%, 43%,
57%).

| Sealed test, 140 clips (seed median) | Control (frozen V6-F) | v2 |
| --- | ---: | ---: |
| Macro F1 over 7 labels | 57.3% | 75.4% (+18.0 pp; 95% CI +11.4 to +26.3) |
| Sit-up recall | 0% | 42.9% |
| Squat recall | 44.4% | 72.2% |
| Push-up / pull-up / bench / jumping jack | 75 / 69 / 50 / 44% | 75 / 81 / 63 / 56% |
| Unknown rejection | 80.4% | 93.5% |
| Real exercises called unknown | 40 | 26 |
| Unknowns let through as an exercise | 9 | 3 |

Sit-up misses were almost all gate rejections: across the 3 seeds, 23 of 42
sealed sit-up predictions were `unknown` and 19 were `sit_up`. None became
`bench_press`. Dev had shown 90% sit-up recall, so the dev estimate was
optimistic (dev had been seen twice).

**Conclusion, as predeclared:** the RepCount training arc stops here as a
documented result. v2 is clearly better than V6-F on unseen footage on most
measures, but it did not meet the predeclared sit-up bar on the sealed test.
It is not promoted. No v3 cap sweep follows. A further attempt needs a new
idea and a new plan, and the sealed test is now spent for this data.
