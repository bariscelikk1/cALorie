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
claim.

## Locked long-video result

Notebook 09 evaluated the checkpoint on the frozen 917-second GainsByBrains
video. The two-stage model reached **47.51% supported-exercise accuracy**,
**32.65% unsupported-exercise rejection**, and **53.97% transition rejection**.
Its stable-interior accuracy was **41.30%**, balanced accuracy **52.04%**, and
Macro F1 **21.37%**.

The design recovered some supported recognition compared with v3 (**33.03%**)
but lost v3's rejection strength (**79.59%** unsupported and **88.89%**
transition rejection). It also remains below v1's **66.52%** supported accuracy.
The gate threshold selected from internal validation therefore does not transfer
well enough to this recording. The result is diagnostic evidence, not a release
candidate.

Per-movement results show that jumping jack and squat kick were recognized
cleanly, while the left plank variation and pop squat were rejected as
`unknown`. Several unsupported movements passed the gate: burpee and glute
bridge were usually called push-up, while jumping rope, running in place, and
side shuffle were usually called bicep curl. See `evaluation/` for the frozen
labels, scored predictions, timeline, confusion matrix, original ZIP, and the
v1-v4 comparison table. See `model/` for the checkpoint and internal reports.

`SHA256SUMS.txt` identifies every archived file.
