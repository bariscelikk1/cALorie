# V6-E complete-action temporal resampling

Notebook 26 retained every Notebook 24 fixed window and added 3,035 train-only
cycle candidates from 650 supported clips and 220 source groups. Candidate
periods were estimated from pose-motion autocorrelation and resampled to 64
cumulative-motion phase positions. All 1,971 test keys and labels remain
identical to V6-C.

The returned archive has outer SHA-256
`5367a0d5947af7551405cc1f1f8551cf9e4b8bc50e3275e3da4bc4ea6b25d77c`.
The ZIP structure and every internal checksum pass.

| Metric | V6-C | Notebook 24 | Temporal |
| --- | ---: | ---: | ---: |
| Gate Macro F1 | 82.03% | 79.44% | 80.18% |
| Oracle exercise Macro F1 | 85.57% | 87.09% | **89.11%** |
| End-to-end Macro F1 | 79.33% | 77.39% | **79.56%** |
| End-to-end accuracy | **82.90%** | 81.13% | 81.33% |

Temporal sampling produces the strongest exercise-only classifier so far. Its
end-to-end gain over original V6-C is only 0.23 points because the gate remains
weaker. MM-Fit w18 accuracy regresses by 10.96 points, while the other three
large MM-Fit groups improve slightly and the held-out YouTube group's
present-class Macro F1 improves by 3.47 points.

Do not promote the complete checkpoint. Carry the temporal exercise classifier
as a provisional fixed classifier into Notebook 27 and change only the open-set
gate. Original V6-C remains the production reference until creator-level gate
regressions are resolved independently.
