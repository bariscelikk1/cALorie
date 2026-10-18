# Source balance v2 — independent-source intake

This folder is the active intake queue for the four source-confounded classes:
`dumbbell_row`, `sit_up`, `lat_pulldown`, and `pull_up`. It replaces neither the
v1 evidence nor the frozen V6-C checkpoint. Nothing in this folder is training
data.

`candidates.csv` contains metadata-verified YouTube candidates from distinct
creator/channel IDs. The list is intentionally redundant: three creators per
target class are retained so visual screening can reject weak sources without
immediately losing creator coverage. Titles and metadata are discovery
evidence only. Before any interval is usable, it still needs source/use review,
full-person RGB and pose screening, exact boundaries, and an independent human
motion review.

`adjudication/second_pass_codex_review.csv` records the 2026-10-18 Codex visual
adjudication of the three v1 quarantine clips. This is not an independent human
second review: the earlier first pass was also produced by Codex. Accordingly,
`independent_human_review_complete=false` and `training_allowed=false` for every
row. The record preserves useful findings without overstating review status:

- Nick's straight-leg sit-up interval is visually coherent and may be retained
  for a human decision.
- Rowan row 02 contains repeated camera cuts and should not be used as one
  training interval.
- Rowan row 03 should be split around the visible shot change before human
  review.

Run the structural guard from the repository root:

```bash
python3 ml/scripts/audit_source_balance_v2.py
```

The guard checks candidate identity separation, reserved-inventory conflicts,
per-class creator coverage, and adjudication interval safety. Passing it does
not promote a candidate or authorize training.

