# v5 hard-negative TCN — locked GainsByBrains evaluation

Notebook 12 evaluated the v5 checkpoint on the same frozen 917-second
GainsByBrains video, labels, 3-second boundary guard, and scoring script used
for v1-v4. The video and its labels were excluded from training and internal
threshold selection.

## Checkpoint result

The checkpoint carries the **0.90** gate threshold selected on its internal
validation split. On the 690 stable interior windows it achieved:

- **77.10%** accuracy;
- **51.87%** balanced accuracy;
- **31.88%** Macro F1;
- **28.51%** supported-exercise accuracy;
- **100%** unsupported-exercise rejection;
- **100%** transition, intro, and outro rejection.

Compared with v4, hard-negative training fixed the main false-positive
failure: unsupported rejection rose from **32.65% to 100%**, transition
rejection rose from **53.97% to 100%**, and stable accuracy rose from
**41.30% to 77.10%**. The internal threshold did not transfer cleanly,
however: supported recognition fell from **47.51% to 28.51%** because the gate
rejected many real exercise windows.

The clearest class-specific failures are both plank variations, which the gate
rejects as unknown, plus squat kick and some pop-squat windows. Sumo squat
pulse remains relatively strong at 72.22%, and jumping jack reaches 75.68%.

## Diagnostic threshold sweep

`diagnostic_threshold_sweep.csv` recomputes the frozen predictions at other
gate thresholds. A threshold near **0.60-0.65** would keep roughly
**97.65-99.15%** unknown rejection while recovering supported accuracy to
roughly **47%** and stable accuracy to roughly **82%**.

This sweep is diagnostic evidence, not a valid final calibration: selecting a
threshold from this locked benchmark would tune on the test set. The next
experiment should calibrate the threshold on a separate person- and
video-separated mixed-workout validation set, then run this benchmark once
without further adjustment. Plank variations should also be added as hard
positive gate examples.

The ZIP and extracted files in this directory preserve the complete Notebook
12 output. `model_comparison.csv` contains the direct v4/v5 checkpoint
comparison.
