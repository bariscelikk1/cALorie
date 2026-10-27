# Long-video test v1 — evaluation 2 (2026-10-28)

The second and final scoring of the locked 8-video, 3.87 h set, with
`ml/scripts/score_long_video_test_v1_eval2.py` (commit `3c93747`, predeclared
in `ml/data/long_video_test_v1/PLAN.md`) on the Mac GPU. Lock hashes were
verified; V6-F and v2 reproduced evaluation 1 exactly.

The final model is Notebook 46 (frozen; it **did not pass** the 15-point dev
gate bar). Scored for the final report only; nothing was tuned from it.

**Answer: the final model is better than V6-F.** Smoothed pooled 15-label
Macro F1: 47.6% vs 32.6% (+15.0 pp; video bootstrap 95% CI +2.2 to
+25.2 pp). Versus v2: +15.3 pp (CI +5.7 to +22.9 pp).

| Smoothed decoder | V6-F | v2 | Final (NB46) |
| --- | ---: | ---: | ---: |
| Macro F1 (15 labels) | 32.6% | 32.3% | 47.6% |
| Accuracy (time) | 63.1% | 67.7% | 73.2% |
| Exercise-block F1 | 0.24 | 0.25 | 0.32 |
| Supported exercise time called unknown | 55.1% | 65.1% | 39.4% |
| Rest/transition time called unknown | 77.9% | 87.5% | 84.8% |
| Label switches/min (truth 0.84) | 1.49 | 1.15 | 1.56 |

Per-class time recall, V6-F → final: bench press 18 → 79%, pull-up 73 → 93%,
push-up 25 → 80%, squat 59 → 71%, jumping jack 82 → 97%, deadlift 97 → 92%,
sit-up 0 → 49%, lunge 0 → 44%, dumbbell row 0 → 30%, shoulder press 0 → 23%,
lat pulldown 80 → 63%, lateral raise 84 → 42%, bicep curl 31 → 28%, tricep
extension 0 → 0%.

Limits: 8 videos (wide CI); 39% of real exercise time is still rejected;
tricep extension is never recognized; lateral raise and lat pulldown lost
ground versus V6-F. Evaluations used on this set: 2.
