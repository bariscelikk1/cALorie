# cALorie provisional creator diagnostic

This report compares frozen V6-C and V6-F on 35 provisional first-pass regions from six reserved creators. It is not a locked benchmark. No result in this package may be used for training, calibration, threshold selection, or model promotion. Six unresolved regions were excluded. See metrics.json and provisional_segment_contract.csv.

The directory preserves two successful executions:

- `calorie_provisional_creator_diagnostic_report.zip` is the locally verified
  reference run (SHA-256 recorded in `ARCHIVE_SHA256.txt`).
- `calorie_provisional_creator_diagnostic_report_colab.zip` is the unchanged
  user-returned Colab reproduction from 2026-10-21 (SHA-256 recorded in
  `COLAB_REPRODUCTION_SHA256.txt`).

All 14 internal Colab hashes pass. Its metric, contract, pose-audit, class,
creator, and bootstrap files are byte-identical to the reference. Every
discrete prediction is identical across 35 regions and 561 windows. Only
floating-point inference values and rendered confusion-matrix bytes differ;
the maximum absolute probability delta is `2.47e-06`, with no threshold or
label change.
