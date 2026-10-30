# cALorie experiment artifacts — V6-B train-only augmentation

V6-B freezes the V6-A.1 group split, square-root-tempered sampler,
Notebook 13 hard-positive weights, TCN blocks, and evaluation protocol. Its
only controlled change is train-only reflection, small rotation, temporal speed
jitter, frame dropping, and coordinate noise. Validation and test landmarks
remain unaugmented.

## Internal result

- gate Macro F1: **79.18%**;
- oracle 14-exercise Macro F1: **86.17%**;
- end-to-end Macro F1: **78.97%**;
- end-to-end balanced accuracy: **80.43%**;
- end-to-end unknown recall: **72.59%**;
- interim validation-selected gate threshold: **0.45**.

On the exact same 1,971 test windows, V6-A.1 reached **76.76%** end-to-end
Macro F1 and **84.81%** oracle exercise Macro F1. V6-B improves those scores by
2.21 and 1.36 percentage points respectively, so the augmentation block is
retained for V6-C. Gate Macro F1 fell by 1.21 points and unknown recall fell
from 82.39% to 72.59%; later independent gate calibration remains required.

The largest unresolved error is `deadlift`: only 13 true test windows exist,
while 120 `unknown` windows are predicted as deadlift. This weak class evidence
must be considered when interpreting the aggregate gain.

V6-C must reuse `model/split_assignments.csv`, the V6-A.1 sampler, and this
augmentation block while changing only the feature representation. See
`model/` for the checkpoint, assignments, sampler audit, reports, plots,
predictions, augmentation preview, and original ZIP.
