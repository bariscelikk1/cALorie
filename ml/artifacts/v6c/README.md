# cALorie experiment artifacts — V6-C kinematic features

V6-C freezes the V6-A.1 split and sampler, Notebook 13 hard-positive weights,
accepted V6-B augmentation, TCN temporal blocks, and evaluation protocol. It
changes only the input representation from 34 normalized x/y coordinates to
100 channels: coordinates, frame velocity, directed bone vectors, and eight
joint angles.

## Internal result

- gate Macro F1: **82.03%**;
- oracle 14-exercise Macro F1: **85.57%**;
- end-to-end Macro F1: **79.33%**;
- end-to-end balanced accuracy: **82.38%**;
- end-to-end accuracy: **82.90%**;
- end-to-end unknown recall: **74.58%**;
- interim validation-selected gate threshold: **0.675**.

On the identical 1,971 internal test windows, V6-B reached 79.18% gate Macro
F1, 86.17% oracle exercise Macro F1, and 78.97% end-to-end Macro F1. V6-C
therefore improves the gate by 2.84 points and end-to-end Macro F1 by 0.36
points, while the standalone exercise classifier falls by 0.60 points. It is a
useful gate/feature candidate rather than an unconditional replacement for
every V6-B component.

A diagnostic combination of the V6-C gate and V6-B exercise classifier reaches
81.15% end-to-end Macro F1 at V6-C's existing threshold on this internal test.
That combination is not promoted from test evidence. Notebook 17 evaluates
V6-B, V6-C, and the modular hybrid on separate creator groups and calibrates
thresholds without loading the locked long-video test.

See `model/` for the checkpoint, assignments, sampler audit, reports, plots,
predictions, augmentation preview, and original ZIP.
