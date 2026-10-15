# cALorie — current handoff

## Active work

Continue on `feat/tcn-rebuild`. The deployed web prototype and the newer ML
rebuild are distinct. `main` alone does not contain the current ML work.
The target is 14 dynamic exercises plus unknown, then stable long-video
segments, repetition counting, calorie estimation, and a local Python app.
Plank is retired to unknown in post-v5 experiments.

Read `ml/EXPERIMENT_BACKBONE.md`, `ml/README.md`, `ml/AGENTS.md`, and
`ml/data/ANNOTATION_GUIDE.md` for the experiment and annotation contracts.
Read `ml/POST_V6C_ROADMAP.md` for the ordered post-G2 plan, hardware choices,
promotion gates, and proposed Notebook 23-30 sequence.
Do not use locked tests for tuning or promote unresolved draft labels.

## Latest completed work

- V6-C remains the baseline candidate; full G1 ST-GCN was rejected.
- G2 Notebook 20 was run by the user. The supplied archive and readable reports
  are preserved in `ml/artifacts/g2/`, with SHA-256 checksums and analysis.
- All 1,971 G2 test window keys, labels and gate probabilities matched V6-C.
  End-to-end F1/accuracy were recomputed directly from prediction CSVs.
- Notebook 21 was created and pushed in commit `c57581b`. It loads fixed
  models and compares V6-C, all three G2 classifiers, and their equal ensemble
  on three existing excluded-source calibration groups. It uses CPU and now
  downloads the G2 ZIP automatically from pinned GitHub commit 3e3ce3c,
  verifies its SHA-256, and does not train or select thresholds.

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

Finish Notebook 22 on CPU and return
`calorie_youtube_long_workouts_v2_review_landmarks.zip`. The notebook requires
no training and does not benefit from a T4. Its current 720p run exports
full-video continuous landmarks, 118 visually prepared first-pass intervals,
contact sheets, audit evidence, and checksums without raw video. Do not train
from this archive yet: audit pose coverage, independently review every
low-confidence row plus at least 10% of the remainder, adjudicate disagreements,
run the strict audit, and then build labelled training clips in the proposed
CPU Notebook 23. The first retraining experiment is proposed Notebook 24 on a
T4 and changes only the added reviewed data while keeping V6-C fixed.

Notebook 22: `ml/notebooks/22_colab_review_extract_youtube_long_v2.ipynb`

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/22_colab_review_extract_youtube_long_v2.ipynb

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

## Notebook input preference

The user requests automatic downloads for notebook inputs already archived
on GitHub. Do not prompt for manual re-upload of those files. Pin a source
commit, verify checksums, reuse valid cached downloads, and fail clearly if
verification fails. Notebook 21 now follows this rule for the G2 report.

Automatic-download update validated with mocked HTTP: initial download, cache reuse, corrupt-cache replacement, checksum rejection, and temporary-file cleanup pass. All notebook Python cells compile; full inference remains unverified.

## Notebook 21 returned result (2026-10-15)

The user returned `calorie_g2_creator_comparison_report.zip`; it is preserved
under `ml/artifacts/g2/creator_comparison/` with extracted evidence and SHA-256
checksums. On the same 1,198 windows from three existing calibration creators,
V6-C ranked first at 30.39% present-class Macro F1. Equal ensemble scored
29.79%, BiGRU 28.48%, Adaptive GCN 28.41%, and Pose Transformer 27.40%.
Accuracy was about 49% and all systems shared 56.45% unknown recall because the
gate was frozen. Seven supported classes are absent. This confirms substantial
creator-domain weakness and does not authorize model promotion; V6-C remains
the reference while new people and missing movements are collected.

## New YouTube candidate batch (2026-10-15)

The user requested about one hour of previously unused, long YouTube workout
footage aligned with the active 14-class target. A 61:59 candidate batch is in
`ml/data/youtube_long_workouts_v2/`:

- Legally Swole `zxqCV_eQHZY` (31:38): rare weighted/machine movements,
  including deadlift, lat pulldown, row, curl, and triceps extension candidates.
- Daniel Nikolic `Fk1wnNX4wQ8` (30:21): bodyweight/HIIT source containing
  candidate push-up, squat, lunge, sit-up, jumping-jack motion and useful
  unsupported compound negatives.

Both IDs and creators are new relative to the 14-source existing manifest.
YouTube metadata and chapter lists were inspected, but full timelines were not
visually reviewed. Raw-video licenses were not declared by YouTube metadata.
Every generated timeline row is therefore draft, second-review-required,
unassigned, and excluded from training. Do not extract/promote landmarks until
complete visual review, license/use review, adjudication, and strict audit.
The draft structural audit covers 42 rows with zero errors. Its 42 warnings are
the expected coarse-boundary warnings from chapter-only metadata; see
`ml/data/youtube_long_workouts_v2/draft_annotation_audit.json`.

The first-pass visual pass expanded the two timelines from 42 chapter-derived
draft rows to 118 motion-oriented intervals: 62 for Daniel Nikolic and 56 for
Legally Swole. The structural audit reports zero errors; all 118 coarse-boundary
warnings are expected because this is still a first pass. Commit `5265a0e`
updated Notebook 22 to use these labels and request 720p sources. It keeps every
resulting row and continuous landmark source at `use_for_training=false`. The
output archive is `calorie_youtube_long_workouts_v2_review_landmarks.zip`.
Notebook JSON and all Python cells parse locally; the active Colab download and
MediaPipe extraction have not yet returned their final report.

## Post-G2 roadmap checkpoint (2026-10-15)

`ml/POST_V6C_ROADMAP.md` records the durable execution plan requested by the
user. The diagnosis is that cross-creator coverage, open-set rejection, action
boundaries, and pose missingness are now stronger bottlenecks than raw model
size. The order is: finish and independently approve the new evidence; exact
V6-C data-only retrain; visibility/missingness ablation; complete-action
temporal samples; CrossMax-inspired multi-stream gate; self-supervised temporal
pretraining; one conditional PoseC3D comparison; then boundary-aware dense
decoding. CPU/T4 choices, required artifacts, evaluation rules, stop rules, and
primary research references are included so a future assistant can continue
without reconstructing this chat.
