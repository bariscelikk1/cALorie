# Source balance v2 dense and replacement evidence

`calorie_source_balance_v2_dense_and_replacements.zip` is the unchanged output
of CPU Notebook 30B. Its outer SHA-256 is recorded in `SHA256SUMS.txt`; all 305
files also passed the archive's internal SHA-256 manifest.

Run summary:

- pinned input commit: `93e366bc574b886bff33c29b880ef1051fb11f10`
- 16/17 dense regions produced 2-FPS evidence
- 5/5 replacement sources produced 5-second full-timeline evidence
- `dFzUjzfih7k` (Max Euceda) was unavailable in 30B because the requested
  format failed with HTTP 403; no earlier evidence was substituted
- no raw video or landmarks were exported
- no interval is independently reviewed or enabled for training
- outer ZIP SHA-256:
  `948d0ef9314b2292a4d80fdb1283b9bb935d7458e2c0fc3be3a56646c4c5a0e9`

The Codex evidence review is recorded in
`ml/data/source_balance_v2/dense_visual_review.csv` and
`replacement_screening_review.csv`. Proposed intervals are inputs to pose and
independent human review, not approved labels.
