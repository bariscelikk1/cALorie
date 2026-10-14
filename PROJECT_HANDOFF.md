# cALorie — current handoff

## Active work

Continue on `feat/tcn-rebuild`. The deployed web prototype and the newer ML
rebuild are distinct. `main` alone does not contain the current ML work.
The target is 14 dynamic exercises plus unknown, then stable long-video
segments, repetition counting, calorie estimation, and a local Python app.
Plank is retired to unknown in post-v5 experiments.

Read `ml/EXPERIMENT_BACKBONE.md`, `ml/README.md`, `ml/AGENTS.md`, and
`ml/data/ANNOTATION_GUIDE.md` for the experiment and annotation contracts.
Do not use locked tests for tuning or promote unresolved draft labels.

## Latest completed work

- V6-C remains the baseline candidate; full G1 ST-GCN was rejected.
- G2 Notebook 20 was run by the user. The supplied archive and readable reports
  are preserved in `ml/artifacts/g2/`, with SHA-256 checksums and analysis.
- All 1,971 G2 test window keys, labels and gate probabilities matched V6-C.
  End-to-end F1/accuracy were recomputed directly from prediction CSVs.
- Notebook 21 was created and pushed in commit `c57581b`. It loads fixed
  models and compares V6-C, all three G2 classifiers, and their equal ensemble
  on three existing excluded-source calibration groups. It uses CPU, needs
  the user's G2 ZIP upload, and does not train or select thresholds.

## G2 results and decision

| System with frozen V6-C gate | Internal end-to-end Macro F1 | Accuracy |
| --- | ---: | ---: |
| Original V6-C | 79.33% | 82.90% |
| BiGRU | 81.14% | 82.50% |
| Equal ensemble | 80.72% | 83.00% |
| Pose Transformer | 78.87% | 82.45% |
| Adaptive GCN | 77.70% | 82.14% |

BiGRU is a candidate, not a promoted replacement. Nearly the entire net F1
increase comes from lat pulldown, which has only seven test windows. Other
classes show mixed changes. Unknown recall stays 74.58% with the fixed gate.
Notebook 20's reported ensemble validation F1 is the mean of the individual
scores, not measured ensemble validation performance. Do not use it for
selection. Actual test ensemble predictions were verified. Correcting the old
validation metric requires new inference on the original validation windows;
those predictions are not in the G2 archive.

## Immediate next action

The user has been given Notebook 21 and should return
`calorie_g2_creator_comparison_report.zip`. Do not assume it has run yet.
Compare the systems on the same sources and inspect per-source and per-class
metrics. Do not compare its present-class F1 directly with the 15-label
internal test or automatically promote a model.

Notebook 21: `ml/notebooks/21_colab_compare_g2_creators.ipynb`

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/21_colab_compare_g2_creators.ipynb

The three sources were already used by Notebook 17; they are not a fresh
locked test. Their historical draft-label concerns and missing exercise
coverage remain unresolved. Notebook 21 explicitly reports provisional
results, fixes the gate at 0.675, and performs no threshold/weight sweep.
Its actual ensemble score is a new measurement on this source set; it does
not repair Notebook 20's old validation field.

## Verification and limitations

Notebook 21 Python cells parse; Git blob integrity and ZIP path checks passed.
Full inference was not run locally because old archive reads stalled and
fresh dependency downloads were too slow. No claim of end-to-end validation.
Model definitions and feature functions reuse Notebook 17/20 implementations.
G2's original ZIP includes model checkpoints but lacks split assignments;
source exclusion relies on the pinned Notebook 20 protocol and V6 split audit.

The GitHub connector can read but returned HTTP 403 on writes. Normal Git
push works and successfully published Notebook 21. Use normal Git for pushes.
Two pre-existing untracked notebooks were preserved and not committed:
`ml/notebooks/01_colab_extract_landmarks.ipynb` and
`ml/notebooks/01_kaggle_extract_landmarks.ipynb`.

## Collaboration preference

The user requests checkpoint commits and pushes after meaningful updates,
with enough durable context for another assistant/person to continue.
Explain notebook hardware explicitly (CPU or T4), provide a direct Colab link,
and name the output ZIP to send back. Prefer Turkish, clear practical steps.
