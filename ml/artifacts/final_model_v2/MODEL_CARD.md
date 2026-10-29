# cALorie final model v2 (frozen 2026-10-30)

**What it is.** Notebook 47: three seeds (42, 137, 2026). Each seed is a 14-class SmallTCN exercise classifier plus
joint, bone, and velocity SmallTCN gates, all retrained from the Notebook 46 recipe (v2 short-clip pool with a
50% RepCount cap, long-video windows at 25% of each gate class) on **all 32 labeled long videos** (round-1
train, dev, and old test videos plus 8 new round-2 training videos). Mean-probability gate fusion, fixed
threshold 0.65. Input: 64-frame windows of 17 MediaPipe keypoints at 15 FPS. Scoring: dense windows every
8 frames and the smoothed decoder. Trained on a Colab T4 (`ml/notebooks/47_long_video_round2_seed*.ipynb`).

**Status.** It passed all four predeclared criteria against the previous final model (v1, Notebook 46) on the
locked round-2 test. Not production-ready.

**Results (locked round-2 test, 6 videos, smoothed seed medians).** Macro F1 43.5% (v1 38.7%, +4.8 pp, video
interval +1.9 to +7.8); weak-class recall 61.7% (v1 48.3%); exercise time called unknown 30.1% (v1 35.0%).
Internal clip test 85.9% Macro F1. Details: `ml/artifacts/long_video_round2_test_v1/eval1/README.md`.

**Known weaknesses.** Dumbbell row recall fell from 41% to 22% on the new test; squat 95 → 88%. Only 6 test
videos, all gym-style follow-alongs; several classes are not covered by that test. About 30% of real exercise
time is still rejected as unknown. Reps are approximate and calories unvalidated.

Files: `models/seed_<seed>_classifier.pt` and `models/seed_<seed>_<joint|bone|velocity>_gate.pt`; checksums in
`SHA256SUMS.txt`. The previous final model is `ml/artifacts/final_model_v1/`.
