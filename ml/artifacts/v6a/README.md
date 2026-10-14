# cALorie experiment artifacts — V6-A equal-group sampler

V6-A tested the first post-v5 sampling correction while keeping the two-stage
TCN architecture fixed. It retired plank into `unknown`, preserved the
historical source-group split, excluded known draft groups, sampled class ->
source group -> window, and applied Notebook 13 hard-positive weights only to
matching training windows.

## Result: completed, not promoted

The implementation audit passed: the gate sampler assigned exactly equal total
weight to supported and unknown, the exercise sampler assigned equal total
weight to every active exercise, 172 active hard-positive training windows
matched, and validation/test received no mined weights.

The fully uniform group level was too aggressive. It gave tiny source groups as
much probability as long, information-rich groups and reduced generalization.
On the internal test:

- gate Macro F1: **61.75%**;
- oracle 14-exercise Macro F1: **84.75%**;
- end-to-end 14-class-plus-unknown Macro F1: **71.63%**;
- end-to-end unknown recall at the interim 0.10 threshold: **27.41%**.

For an apples-to-apples diagnostic, the archived v5 predictions were remapped to
the active 14-class taxonomy on the exact same 1,971 test windows. V5 reached
**88.11%** oracle exercise Macro F1 and **76.70%** end-to-end Macro F1, both
higher than V6-A. This remapping is a diagnostic comparison; the original v5
metrics remain unchanged.

V6-A is therefore retained as negative evidence and will not become the V6-B
base. V6-A.1 keeps the hierarchy but assigns group probability proportional to
the square root of its window count. This still limits long-video dominance
without making a one-window group equal to a large, diverse group.

See `model/` for the checkpoint, split assignments, sampler audit, reports,
plots, predictions, and original ZIP.
