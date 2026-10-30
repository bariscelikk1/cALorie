# TCN v2 — locked GainsByBrains evaluation

This directory evaluates the TCN v2 candidate on the same 917.4-second
GainsByBrains video and frozen human labels used for TCN v1. The video remained
outside both training sets. A three-second boundary guard defines stable
interior windows, matching the v1 scoring protocol.

At the unchanged 0.55 inference threshold:

| Metric | TCN v1 | TCN v2 | Change |
| --- | ---: | ---: | ---: |
| Stable accuracy | 42.32% | 32.46% | -9.86 pp |
| Stable balanced accuracy | 49.32% | 34.88% | -14.44 pp |
| Stable Macro F1 | 19.45% | 15.31% | -4.15 pp |
| Supported-exercise accuracy | 66.52% | 49.32% | -17.19 pp |
| Unsupported-exercise rejection | 32.65% | 20.70% | -11.95 pp |
| Transition rejection | 26.19% | 34.92% | +8.73 pp |

V2 improved burpee rejection from 0% to 64%, retained 100% rejection for
`in_and_out`, and improved transition rejection. Those gains did not generalize
across other negatives: bicycle crunch was forced into `bench_press`, while
jumping rope, push back, running in place, and side shuffle were usually forced
into `bicep_curl`. Supported performance also regressed because the left plank
variation became `unknown`; the right plank variation and both recognized squat
families remained strong.

The conclusion is evidence against promoting this checkpoint as an upgrade.
The next experiment should preserve the frozen test, create diverse internal
unknown subtypes from other source videos, balance samples by class and source,
and add motion features before training TCN v3.

`mixed_video_analysis.zip` is the untouched Colab export. `raw/` exposes its
contents; `scored/` contains the human-label evaluation; and
`v1_v2_comparison.csv` records the direct metric deltas.
