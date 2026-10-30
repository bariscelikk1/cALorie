# V6-C plus YouTube long-v2 data-only retrain

Notebook 24 added the two verified Notebook 23 source groups to training while
freezing the V6-C architecture, 100-channel feature representation,
augmentation, sampler, seed, old group assignments, validation evidence, test
evidence, and threshold-selection procedure.

The returned archive has outer SHA-256
`920fc8082a853d4cea852e9b86ce25734609fcbdf3459a31918e39798842b1e9`.
Its ZIP structure and every internal entry in `SHA256SUMS.txt` pass. All 1,971
test window keys and labels match V6-C exactly. The new data contributes 464
train-only windows from two groups.

## Result

| Metric | V6-C | Data-only retrain | Delta |
| --- | ---: | ---: | ---: |
| Gate Macro F1 | 82.03% | 79.44% | -2.58 pp |
| Oracle exercise Macro F1 | 85.57% | 87.09% | +1.52 pp |
| End-to-end Macro F1 | 79.33% | 77.39% | -1.94 pp |
| End-to-end accuracy | 82.90% | 81.13% | -1.78 pp |

The new data improves the supported-only classifier but shifts the gate toward
rejection. End-to-end unknown recall rises from 74.58% to 89.28%, while lunge
recall falls from 65.79% to 41.05% and squat recall from 82.94% to 51.76%.
Creator effects are also inconsistent: the held-out YouTube group improves by
11.73 percentage points in accuracy, while the four substantial MM-Fit groups
regress by 2.40, 6.83, 11.16, and 18.49 points.

## Decision

Do not promote this checkpoint. Keep original V6-C as the reference. The run is
useful evidence that the added data helps exercise classification but exposes
gate/domain imbalance. Notebook 25 should compare the original 100-channel
V6-C representation with visibility/missingness channels under the same split,
including the new training data, and must report both original V6-C and this
data-only checkpoint as controls. Promotion still requires improvement on
unchanged creator-separated evidence without material unknown or creator
regression.
