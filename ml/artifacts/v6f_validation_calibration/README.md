# V6-F validation-only gate calibration

This directory preserves the unchanged Notebook 32 report returned on
2026-10-19. `SHA256SUMS.txt` verifies every original report file; this README is
repository context and is intentionally outside the original manifest.

Validation selected threshold `0.57` under the predeclared unknown-recall floor
of `0.85`. On the reused 1,971-window internal development test, end-to-end
Macro F1 increased from 82.09% to 82.39%, but accuracy fell from 85.34% to
83.76% and unknown recall fell from 92.04% to 83.61%. Total errors increased
from 289 to 320. The held-out YouTube and MM-Fit w18 creator gates still failed.

Threshold `0.57` is rejected as the new default. Threshold `0.65` remains the
research reference. The next bounded experiment changes gate training rather
than thresholding: equal creator mass plus a group-CVaR objective, repeated over
the same three seeds with the temporal exercise classifier frozen.

