# V6-F multi-stream open-set gate

Notebook 27 froze the Notebook 26 temporal exercise classifier and trained
independent joint, bone, and velocity binary gates. Validation selected mean
supported probability at threshold 0.65 under a required 85% unknown-rejection
constraint. The selected row achieved 90.96% validation unknown rejection;
test labels were not used for fusion or threshold selection.

The returned archive has outer SHA-256
`46fc78719368dfbf617f51034349ca378c39b09b8c0f782a06bf978a43a29fc3`.
Its ZIP structure and all internal checksums pass. The test contains the same
1,971 keys as V6-C and Notebook 26.

| Metric | V6-C | Notebook 26 | Multi-stream gate |
| --- | ---: | ---: | ---: |
| Gate Macro F1 | 82.03% | 80.18% | **83.95%** |
| Oracle exercise Macro F1 | 85.57% | **89.11%** | **89.11%** |
| End-to-end Macro F1 | 79.33% | 79.56% | **81.72%** |
| End-to-end accuracy | 82.90% | 81.33% | **84.17%** |

This is the strongest aggregate candidate so far. Unknown recall rises from
74.58% in V6-C to 85.91%. Lat-pulldown recall also improves, but its test
support is only seven windows. Material creator regressions remain: MM-Fit w13
accuracy is 8.58 points below V6-C, and the held-out YouTube group's
present-class Macro F1 is 8.40 points lower despite higher raw accuracy.

Retain V6-F as the leading candidate, not a production promotion. Notebook 28
may change only exercise-encoder initialization through self-supervised masked
temporal pretraining while freezing this selected gate for end-to-end
comparison.
