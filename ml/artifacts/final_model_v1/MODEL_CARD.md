# cALorie final model v1 (frozen 2026-10-28)

**What it is.** Notebook 46: three seeds (42, 137, 2026). Each seed is a
14-class SmallTCN exercise classifier (from Notebook 45: v2 recipe plus 11
long-video training videos) and joint, bone, and velocity SmallTCN gates
(retrained with long-video windows at 25% of each gate class). Mean-probability
gate fusion, fixed threshold 0.65. Input: 64-frame windows of 17 MediaPipe
keypoints at 15 FPS, normalized by hip center and shoulder/torso scale.
Scoring: dense windows every 8 frames, then the smoothed decoder (9-window
vote, runs under 4 s merged). Code: `ml/scripts/score_long_video_test_v1.py`
and `ml/scripts/score_long_video_test_v1_eval2.py` (`nb46_models`).

**Status.** Frozen by the user's decision for the final report. It did
**not** pass the predeclared dev gate bar (exercise time called unknown fell
10.3 pp; 15 pp was required). Not production-ready.

**Results.**
- Locked long-video test (evaluation 2, 8 videos): smoothed Macro F1 47.6%
  (V6-F 32.6%; +15.0 pp, CI +2.2 to +25.2). Exercise time called unknown 39%.
- Dev (5 videos): smoothed Macro F1 35.7% (v2 25.7%).
- Internal clip test: Macro F1 about 83% (seed mean; v2 80%).

**Known weaknesses.** Tricep extension 0%; lateral raise, curl, row, and
shoulder press 23-45%; 39% of real exercise time still rejected as unknown;
evaluated on few videos. Rep counting and calorie estimation are not built.

Files: `models/seed_<seed>_classifier_from_nb45.pt` and
`models/seed_<seed>_<joint|bone|velocity>_gate.pt`; checksums in `SHA256SUMS.txt`.
Source archive: `ml/artifacts/long_video_gate_balance_v1/`.
