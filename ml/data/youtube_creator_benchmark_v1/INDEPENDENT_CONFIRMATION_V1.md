# Independent confirmation v1

The 17-row independent confirmation queue was completed by reviewer `baris`
using the local visible-motion review UI. The returned file is preserved
unchanged as `independent_confirmation_completed_v1.csv` with SHA-256
`ee234ee1379ad6aa5210d0f0e0c23f4058250897c4e96b2eb71d2aa77dc78199`.

## Result

- 17/17 required rows are complete with no blank decision fields.
- Decision agreement with the Codex dense pass is 17/17.
- Label agreement is 17/17.
- Exact boundary agreement is 15/17 (88.24%).
- `michelle_lateral_01` ends at 1968 s instead of 1972 s.
- `ojs_squat_01` starts at 103 s instead of 93 s, excluding jumping jacks.
- All four compound TIFF regions remain `unknown`.
- No unresolved retained second reviews remain.

`process_creator_benchmark_confirmation.py` validates the returned CSV and
materializes `resolved_region_adjudication_v1.csv`. The original Codex pass and
the returned independent file remain immutable inputs; corrections are applied
only in the resolved table.

## Scope of the lock

`locked_region_benchmark_v1.csv` contains 36 retained, non-overlapping regions
from six reserved creator videos. It covers all 14 supported labels plus
`unknown`. The region lock permits exactly one frozen evaluation of already
fixed models on these regions. It does not permit training, calibration,
threshold selection, prediction-guided relabeling, or model selection.

This is not a continuous long-video segmentation benchmark. Unreviewed gaps in
the six source videos do not yet have continuous timeline ground truth, so
long-video segmentation and transition metrics remain unlocked.
