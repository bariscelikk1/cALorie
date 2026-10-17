# V6-C source-balance draft retrain — rejected diagnostic

Notebook 29G completed on 2026-10-18. It retained the exact V6-C architecture,
features, augmentation, sampler, seed, and frozen 1,971-window internal test,
then added only three quarantined first-pass clips from two new source groups.
Those clips contributed 52 training windows: 34 `dumbbell_row` windows from
`youtube:jTRwWrnVGuE` and 18 `sit_up` windows from
`youtube:6MYtjzEF6IA`.

The returned download was normalized to
`model/calorie_v6c_source_balance_draft_retrain_report.zip`. Its outer SHA-256
is `eb83a491733dfdd153d90a9c40aa5a31fc8cff616f246a28cf3e4c88ca369f46`.
ZIP integrity and all 22 internal entries listed in `SHA256SUMS.txt` pass.

## Result

| Metric | V6-C | 29G | Delta |
| --- | ---: | ---: | ---: |
| Gate Macro F1 | 82.03% | 83.55% | +1.52 pp |
| Oracle exercise Macro F1 | 85.57% | 83.84% | -1.73 pp |
| End-to-end Macro F1 | 79.33% | 78.23% | -1.10 pp |
| End-to-end accuracy | 82.90% | 82.45% | -0.46 pp |
| Unknown recall | 74.58% | 79.33% | +4.75 pp |

The validation-selected gate threshold moved from 0.675 to 0.525. The stronger
gate and unknown rejection did not compensate for the weaker exercise
classifier.

The added target classes did not improve on the frozen internal test:

- `dumbbell_row` end-to-end F1 fell from 83.95% to 71.20%; recall stayed at
  72.34%, so the loss is primarily precision.
- `sit_up` end-to-end F1 fell from 100.00% to 92.75%; recall fell from 100.00%
  to 87.07%.

Creator results are mixed rather than uniformly improved. The large external
`youtube:fegQSC-nUtg` group gains 4.25 accuracy points, while MM-Fit `w11` and
`w18` lose 5.28 and 4.79 points respectively. The experiment therefore does
not establish source-balanced generalization.

`pose_imputation_audit.csv` records the expected repair: 136 non-finite values
across exactly two frames in `rowan_row_02_01`, repaired by per-joint/channel
linear temporal interpolation. No other pose repair occurred.

## Decision

Reject this checkpoint for promotion. Keep frozen V6-C as the reference and
retain 29G only as diagnostic evidence. The three added clips are still
`review_status=draft`, `training_allowed=false`, and `status=quarantined`;
independent second review remains incomplete.

The next work is data quality and creator coverage, not another architecture
change: independently review the exact motion boundaries, discard or relabel
ambiguous clips, and obtain more creator-disjoint evidence for the weak/source-
confounded classes before another controlled retrain. Do not iteratively tune
against the already-used 1,971-window internal test.
