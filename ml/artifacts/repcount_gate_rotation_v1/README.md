# RepCount gate rotation v1 — Notebook 39 result (2026-10-26)

`calorie_repcount_gate_rotation_v1_report.zip` is the unchanged output of the
single predeclared run (SHA-256 `1e704966aacf727aaa18e2d7d74a0e7ad24c9f3d83d480f1ae1b20613e9965f0`; internal `SHA256SUMS.txt` verified).
It ran on the user's Mac (Apple M2 GPU via `CALORIE_DEVICE=mps`, commit
`d34a840`) because Colab cannot render in the user's browser. Both parity
checks passed before training.

**Verdict (predeclared rule): `data_effect_not_supported`.** One of five
criteria failed: the seed-median supported false-unknown count was 6/18, and
the rule required at most 5/18.

| Seed-median out-of-fold (30 clips) | Frozen V6-F | Control | Treatment |
| --- | ---: | ---: | ---: |
| Supported false-unknown (lower is better) | 8 | 9 | 6 |
| Unknown rejected, of 12 | 5 | 7 | 11 |
| Unknown let through as an exercise | 7 | 5 | 1 |
| End-to-end correct, of 30 | 11 | 13 | 18 |
| Sit-up correct, of 7 | 0 | 0 | 0 |
| Squat correct, of 10 | 6 | 6 | 7 |

Internal-test end-to-end Macro F1: control mean 81.64%, treatment mean 82.26%
(guardrail passed).

**Why sit-ups stay at 0/7:** when the retrained gate accepts a sit-up, the
frozen V6-E classifier labels it `bench_press` (lying supine). In
`stu6_50` that happened in all three seeds. Gate-only retraining cannot
fix this. Sit-ups need classifier training data.

**Not claimed:** this does not count as a success. The unknown-rejection and
end-to-end gains are observations under a failed predeclared rule, on 30 clips
from one dataset, and are non-promotable. No rerun or tuning follows.
