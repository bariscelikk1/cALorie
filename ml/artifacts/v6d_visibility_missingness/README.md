# V6-D visibility and missingness ablation

Notebook 25 compared two 134-channel variants on the frozen Notebook 24
training evidence and exact 1,971-window V6 test. The archive has outer SHA-256
`b86c12a114aa5ae157fc3939571d7a099ca965016220bd794957dbdb80988bbf`;
the ZIP structure and every internal checksum pass.

| Variant | Gate F1 | Oracle exercise F1 | End-to-end F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| Original V6-C | 82.03% | 85.57% | 79.33% | 82.90% |
| Notebook 24 data-only | 79.44% | 87.09% | 77.39% | 81.13% |
| Visibility + missing mask | **84.78%** | 83.26% | **80.88%** | 83.56% |
| Visibility/mask + pose-failure augmentation | 71.66% | 83.33% | 77.04% | **84.37%** |

Visibility and missing-mask channels recover the Notebook 24 gate regression
and exceed original V6-C aggregate end-to-end F1 by 1.55 percentage points.
They reduce oracle classifier F1 by 2.31 points and still regress substantial
MM-Fit creators w11, w13, and w18 versus original V6-C. Synthetic visibility
also identifies the MM-Fit source perfectly: all MM-Fit windows have visibility
one and missing fraction zero, unlike MediaPipe sources. The channels can
therefore encode dataset identity.

The realistic occlusion variant is rejected. Its gate F1 falls by 10.37 points
versus original V6-C despite higher raw accuracy, showing that the current
corruption severity/mixture damages class-balanced rejection.

Do not promote either full checkpoint. Retain visibility/missingness as a
gate-specific hypothesis for the later multi-stream open-set stage. Notebook 26
returns to the 100-channel V6-C representation and changes only train-time
temporal sample construction, so the next result is not stacked on an
unpromoted representation.
