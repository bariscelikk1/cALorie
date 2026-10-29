# Long-video round 2 test — evaluation 1 (2026-10-30)

First and only scoring of the locked 6-video round-2 test (2.6 h; creators never used before), with
`ml/scripts/score_nb47_round2_v1.py`. Frozen Notebook 46 (3 seeds) against Notebook 47 (3 seeds trained on a
Colab T4 on 32 long videos; `ml/artifacts/long_video_round2_training_v1/`). Lock hashes, ZIP checksums, and
train/test disjointness verified before scoring. Smoothed decoder, threshold 0.65, seed medians.

**Verdict: Notebook 47 replaces Notebook 46. All four predeclared criteria pass.**

| Criterion | Result | Bar | Pass |
| --- | ---: | ---: | :---: |
| Smoothed pooled Macro F1 gain | +4.8 pp (38.7 → 43.5%) | ≥ +3 pp | yes |
| Mean time recall over the five weak classes | 48.3 → 61.7% (+13.4 pp) | ≥ +10 pp | yes |
| Exercise time called unknown | 35.0 → 30.1% (−4.9 pp) | no worse than +3 pp | yes |
| Rest time called unknown | 76.3 → 76.5% (+0.2 pp) | no worse than +5 pp | yes |

Reported, not judged: video-bootstrap 95% interval for the Macro F1 gain +1.9 to +7.8 pp; internal clip test
(Notebook 47 seed mean) 85.9% Macro F1 versus about 83% for Notebook 46; accuracy 69.1 → 72.2%; block F1
0.37 → 0.43.

Time recall, Notebook 46 → Notebook 47: lateral raise 5 → 64%, bicep curl 65 → 81%, tricep extension
60 → 72%, bench press 97 → 93%, deadlift 98 → 98%, shoulder press 71 → 69%, squat 95 → 88%,
**dumbbell row 41 → 22% (worse)**, jumping jack 0 → 0% (almost no jumping-jack time in this test).
Per video (Macro F1), Notebook 47 is better on 4 of 6 videos (7bD2iKKNoCE, K59aLtJH0ok, YEG6y9r-ELM,
o3xDawAnb-M) and slightly worse on 2 (cv10-qXYE1U 25.4 → 24.9%, lMhDB_naNBY 27.7 → 23.5%).

Limits: 6 videos, so the interval is wide; six exercise classes (lunge, pull-up, push-up, sit-up, lat pulldown,
and mostly jumping jack) do not appear in this test; the round-2 videos are gym-style follow-alongs. This
test set is now used once; do not tune on it.
