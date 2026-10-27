# Long-video test v1 — evaluation 1 (2026-10-27)

The first and only scoring so far of V6-F and v2 (3 frozen seeds) on the
locked 8-video, 3.87 h set, using the predeclared scorer
(`ml/scripts/score_long_video_test_v1.py`, commit `dc6338f`) on the Mac GPU.
The lock hashes were verified before the run.

**Answer to the primary question: not shown better.** Smoothed pooled
15-label Macro F1 was 32.6% for V6-F and 32.3% for v2 (−0.3 pp; video
bootstrap 95% CI −6.2 to +7.6 pp).

| Smoothed decoder | V6-F | v2 (seed median) |
| --- | ---: | ---: |
| Macro F1 (15 labels) | 32.6% | 32.3% |
| Accuracy (time) | 63.1% | 67.7% |
| Exercise-block F1 | 0.24 | 0.25 |
| Label switches/min (truth 0.84) | 1.49 | 1.15 |
| Rest/transition time called unknown | 77.9% | 87.5% |
| Supported exercise time called unknown | 55.1% | 65.1% |

Per-class time recall, V6-F → v2: push-up 25 → 82%, squat 59 → 71%,
jumping jack 82 → 97%, pull-up 73 → 71%, lat pulldown 80 → 87%, deadlift
97 → 90%; but bicep curl 31 → 7%, lateral raise 84 → 7%, bench press
18 → 3%. Sit-up, dumbbell row, lunge, shoulder press, and tricep extension
are 0% for both.

**Reading:** on full sessions the main failure is the gate: more than half of
real exercise time is rejected as `unknown`. v2 handles downtime better and
flickers less, and it improves push-ups, squats, and jumping jacks. But it
rejects even more supported time, and it lost curls and lateral raises
(classes RepCount does not cover). Raw block F1 is near zero for both,
because the frame-level output flickers about 6 times per minute.
Measurement only; nothing is promoted or tuned from it.
