# cALorie experiment artifacts — V6-A.1 tempered sampler

V6-A.1 corrected the failed fully uniform group level from V6-A. Classes retain
equal sampling mass, while source groups inside each class receive mass
proportional to the square root of their window count. Notebook 13
hard-positive modifiers remain normalized within their original training group.

## Internal result

- gate Macro F1: **80.39%**;
- oracle 14-exercise Macro F1: **84.81%**;
- end-to-end Macro F1: **76.76%**;
- end-to-end unknown recall: **82.39%**;
- interim validation-selected gate threshold: **0.825**.

On the exact same 1,971 test windows, the active-14 v5 diagnostic reached
**76.70%** end-to-end Macro F1 and V6-A.1 reached **76.76%**. V6-A.1 therefore
recovers the V6-A regression and provides a neutral, auditable sampling base,
but it does not establish a meaningful accuracy improvement over v5. Its oracle
exercise Macro F1 (**84.81%**) remains below the active-14 v5 diagnostic
(**88.11%**).

V6-B must reuse `model/split_assignments.csv` directly and change only train-time
augmentation. See `model/` for the checkpoint, assignments, sampler audit,
reports, plots, predictions, and original ZIP.
