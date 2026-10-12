# cALorie experiment artifacts — v4 two-stage candidate

V4 separates rejection from exercise identity:

1. a binary TCN gate predicts supported exercise versus `unknown`, and
2. a second TCN classifies accepted windows among 15 supported exercises.

Both models use the same source-group-separated split and normalized 64-frame
pose windows. A validation-only sweep selected a gate threshold of **0.10**.
The locked GainsByBrains labels were not used for training or calibration.

## Internal results

- gate Macro F1: **77.24%**
- gate balanced accuracy: **77.81%**
- oracle exercise-classifier accuracy: **80.42%**
- oracle exercise-classifier Macro F1: **70.66%**
- end-to-end accuracy: **71.37%**
- end-to-end balanced accuracy: **75.70%**
- end-to-end Macro F1: **63.37%**

The internal test fold contains no plank windows, so it cannot support a plank
claim. The checkpoint remains a candidate until Notebook 09 evaluates it on
the frozen long-video benchmark. See `model/` for the combined checkpoint,
reports, confusion matrices, threshold sweep, histories, and raw predictions.

`SHA256SUMS.txt` identifies every archived file.
