# G1 ST-GCN controlled comparison

Notebook 19 compared a small 17-node ST-GCN with V6-C TCN on the same frozen 1,971-window split, labels, sampler, hard-positive weights, augmentations, seed, and evaluation protocol.

## Result

| System | Gate Macro F1 | Oracle exercise Macro F1 | End-to-end Macro F1 | End-to-end accuracy | Unknown recall |
| --- | ---: | ---: | ---: | ---: | ---: |
| V6-C TCN | 82.03% | 85.57% | 79.33% | 82.90% | 74.58% |
| G1 ST-GCN | 74.52% | 88.09% | 67.93% | 64.23% | 16.85% |
| Diagnostic hybrid: V6-C gate + G1 classifier | — | 88.09% | 79.25% | 82.45% | 74.58% |

The graph classifier improved oracle exercise Macro F1 by 2.52 percentage points, but its gate was substantially weaker. Its validation-selected threshold of 0.10 accepted too many unknown windows. The complete G1 system is rejected as a replacement for V6-C. The G1 classifier remains a modular candidate, but the test-set hybrid is diagnostic evidence only and cannot be promoted without creator-separated validation.

Archive SHA-256: `df26c68984ab5a8ca16acacbba266dfd6d67fec08fa7bde0b7ca1062130050fa`.
