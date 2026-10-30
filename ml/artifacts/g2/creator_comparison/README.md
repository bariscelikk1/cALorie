# G2 existing-creator comparison

This directory preserves the output returned from Notebook 21 on 2026-10-15.
The original ZIP is stored alongside its extracted report and per-file SHA-256
checksums.

The comparison uses 1,198 windows from three existing calibration creators and
the frozen 0.675 gate threshold. It is provisional evidence rather than a new
locked test. No model was trained, no threshold was tuned, and no model may be
promoted from this result alone.

| System | Present-class Macro F1 | Accuracy | Unknown recall |
| --- | ---: | ---: | ---: |
| V6-C | 30.39% | 49.17% | 56.45% |
| Equal ensemble | 29.79% | 49.17% | 56.45% |
| BiGRU | 28.48% | 49.08% | 56.45% |
| Adaptive GCN | 28.41% | 48.83% | 56.45% |
| Pose Transformer | 27.40% | 49.17% | 56.45% |

V6-C ranks first on this source set. Seven supported classes are absent, the
historical timeline concerns remain unresolved, and the windows are correlated
within creators. Keep V6-C as the current reference while collecting new
people and movements.

The returned archive SHA-256 is
`0692184a289d39d6a56a61c451f16266a8c8e619c10c949bfa076b3b32d2e46f`.
