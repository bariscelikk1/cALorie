# Source balance v2 screening evidence

`calorie_source_balance_v2_screening.zip` is the returned output of CPU
Notebook 30A. The archive is preserved unchanged. Its outer SHA-256 is recorded
in `SHA256SUMS.txt`; all 128 archived files also passed the archive's internal
SHA-256 manifest.

Run summary:

- pinned input commit: `f4e6ec9c1c83ffcb19ce754752580d66783b4939`
- 12/12 metadata candidates produced 360p contact-sheet evidence
- no raw video was exported
- no candidate was labeled or enabled for training
- outer ZIP SHA-256:
  `6f5c77a7c29be539e7de9737a9ef0254fb09e92c653d2e17f687d56344139aa5`

The Codex visual screening is recorded in
`ml/data/source_balance_v2/screening_review.csv`, with broad follow-up locators
in `dense_review_targets.csv`. It is not an independent human review. The
screening also identifies an identity alias: the CHRIS HERIA and THENX videos
feature the same athlete and therefore form one person group despite distinct
channel IDs.

Current evidence is strongest for dumbbell row, one sit-up creator, and two
pull-up creators. The three lat-pulldown candidates are rejected or held for
cropping, camera, or actor complexity. Additional sit-up and lat-pulldown
sources are required before the creator-balance collection target is met.

