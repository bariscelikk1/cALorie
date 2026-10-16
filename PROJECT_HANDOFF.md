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

Notebook 22 and CPU Notebook 23 are complete. Notebook 23's returned package is
verified and archived under `ml/artifacts/youtube_long_v2/reviewed_clips/`.
It contains 32 clips from two new train-only groups: 20 supported clips across
nine classes and 12 unknown clips, totaling 15,195 frames. All checksums,
manifest paths, finite-array checks, and pose schemas pass. The conservative
contact-sheet audit does not claim frame-accurate full-motion review.

The next controlled experiment is Notebook 24 on a T4 GPU. It must preserve the
exact V6-C architecture, features, augmentation, seed, sampler, old group
splits, validation evidence, and test evidence. The only change is adding the
two Notebook 23 source groups to training.

Notebook 24 is implemented as
`ml/notebooks/24_colab_retrain_v6c_youtube_long_v2.ipynb`. It automatically
downloads all inputs from pinned commit
`5df5acd57785d1d03fc78c1f97cf7f85b0bbceb0`, verifies the new data archive and
critical control files, structurally tests every ZIP, and asserts that the old
window evidence and 1,971 V6-C test keys and labels are unchanged. The two new
groups contribute 464 train-only windows. The expected output is
`calorie_v6c_longv2_data_retrain_report.zip`.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/24_colab_retrain_v6c_youtube_long_v2.ipynb

Notebook 24 has now returned and is archived under
`ml/artifacts/v6c_longv2_data_retrain/`. The exact 1,971 V6-C test keys and
labels match. Adding 464 train-only windows improved oracle exercise Macro F1
from 85.57% to 87.09%, but gate Macro F1 fell from 82.03% to 79.44% and
end-to-end Macro F1 fell from 79.33% to 77.39%. End-to-end unknown recall rose
to 89.28% while lunge and squat recall fell sharply. The held-out YouTube group
improved, but all four substantial MM-Fit creators regressed. Do not promote
the Notebook 24 checkpoint; original V6-C remains the reference.

The next experiment is T4 Notebook 25: a controlled visibility/missing-mask
ablation. It should retain the Notebook 24 training evidence and compare the
100-channel V6-C input against added visibility/detection channels, while
reporting both original V6-C and Notebook 24 as controls.

Notebook 25 is implemented as
`ml/notebooks/25_colab_visibility_missingness_ablation.ipynb`. It trains two
separate 134-channel variants: visibility plus per-joint missing masks, then the
same input with train-only body-part/frame pose-failure augmentation. Both use
the frozen Notebook 24 evidence, sampler, model family, and 1,971-window test.
The notebook audits visibility by source because MM-Fit has synthetic
visibility values, saves augmentation previews before training, and exports
aggregate, per-class, and creator-level comparisons against both controls.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/25_colab_visibility_missingness_ablation.ipynb

Runtime: T4 GPU. Expected output:
`calorie_v6d_visibility_missingness_ablation_report.zip`.

Notebook 25 has returned and is archived under
`ml/artifacts/v6d_visibility_missingness/`. Visibility plus missing masks raised
gate Macro F1 to 84.78% and end-to-end Macro F1 to 80.88%, 1.55 points above
original V6-C. Oracle exercise F1 fell to 83.26%, and several substantial
MM-Fit creators still regressed. MM-Fit has synthetic all-one visibility, so
the added channels can reveal source identity. Do not promote the full model;
retain the representation as a gate-specific hypothesis for Notebook 27.
The separate pose-failure augmentation is rejected because gate F1 collapsed
to 71.66%.

Notebook 26 should implement complete-action temporal sampling on the
100-channel V6-C representation with Notebook 24 evidence. Validation and test
windows stay unchanged. This avoids stacking temporal changes on an unpromoted
visibility representation.

Notebook 26 is implemented as
`ml/notebooks/26_colab_complete_action_temporal_resampling.ipynb`. It retains
every Notebook 24 fixed window and adds at most six deterministic cycle
candidates per supported training clip. Candidate duration is estimated from
pose-motion autocorrelation; samples are resampled to 64 cumulative-motion
phase positions. Architecture, 100-channel features, augmentation, sampler,
validation, and test stay frozen. The report includes a temporal-cycle audit
and comparisons with both original V6-C and Notebook 24.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/26_colab_complete_action_temporal_resampling.ipynb

Runtime: T4 GPU. Expected output:
`calorie_v6e_complete_action_temporal_report.zip`.

Notebook 26 has returned and is archived under
`ml/artifacts/v6e_complete_action_temporal/`. It added 3,035 train-only cycle
candidates while preserving all 1,971 test keys. Oracle exercise Macro F1 rose
to 89.11%, the strongest classifier result so far. Gate Macro F1 remained below
V6-C at 80.18%, so end-to-end Macro F1 reached only 79.56%. MM-Fit w18 accuracy
regressed by 10.96 points. Do not promote the full checkpoint; carry its
exercise classifier as a provisional frozen component into the gate-only
Notebook 27 experiment.

Notebook 27 is implemented as
`ml/notebooks/27_colab_multistream_open_set_gate.ipynb`. It freezes Notebook
26's temporal exercise classifier and trains three binary TCN gates over joint
coordinates, bone vectors, and velocity. Validation compares mean probability,
weakest-stream-weighted probability, and a prototype-distance fusion. Selection
requires at least 85% validation unknown rejection; only the selected fusion
and threshold define the primary unchanged-test result.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/27_colab_multistream_open_set_gate.ipynb

Runtime: T4 GPU. Expected output:
`calorie_v6f_multistream_open_set_gate_report.zip`.

Notebook 23: `ml/notebooks/23_colab_review_build_youtube_long_v2.ipynb`

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/23_colab_review_build_youtube_long_v2.ipynb

Runtime: CPU. Expected output:
`calorie_youtube_long_workouts_v2_reviewed_clips.zip`.

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

The broader execution contract is now explicit in root and ML `AGENTS.md`:
Codex prepares labels, audits, manifests, code, and GitHub artifacts locally;
the user selects the stated CPU/T4 runtime and presses `Run all`; the notebook
automatically obtains verified inputs, performs remote compute, and downloads
one named output ZIP. Manual uploads, file pickers, mandatory widgets, pasted
repair cells, and code edits are regressions in the normal workflow. Returned
ZIPs are verified, analyzed, archived, and pushed before the next notebook is
handed off.

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
Notebook JSON and all Python cells parse locally. The returned report passes
ZIP and internal checksum verification. Its two continuous arrays contain
55,787 finite 17 x 4 frames at 15 FPS. Detection is 99.52% and 99.56%; the 20
supported intervals have at least 99.44% detection. Four pose-quality flags are
all in `unknown` material. A second inspection of all 118 contact sheets found
no obvious label mismatch, but it does not approve motion boundaries.

The user's first Notebook 22 run downloaded the Legally Swole source correctly
at 1280x720 and 30 FPS (56,949 frames), then the single fixed-format `yt-dlp`
command failed on the Daniel Nikolic source without exposing stderr. The next
Notebook 22 revision preserves completed downloads, adds retry/backoff and
three exact-720p format/client strategies, validates the decoded resolution,
and prints the final 30 lines of each failed `yt-dlp` attempt. Rerun only the
download cell in the same Colab runtime so the completed first video is reused.

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

## Notebook 23 implementation (2026-10-16)

Notebook 23 automatically downloads the 31.98 MB Notebook 22 archive from
pinned commit `5146096fed1282fc3b82a8878687613cf3ccfe33` and verifies outer
and internal hashes. It reuses Notebook 22 video files when the same Colab
runtime is alive; otherwise it downloads 360p copies only for review clips.
Training arrays always come from the 720p-derived continuous landmarks. A
local dry run verified target selection and conservative slicing for 32 clips:
20 supported clips across nine classes and 12 unknown clips. Notebook JSON and
all Python cells parse; Colab video download, widget interaction, and final ZIP
export remain to be run by the user.

The first user run reached the review-video cell but current YouTube extraction
exposed only limited formats because no JavaScript runtime was installed; the
old `android_vr` fallback then returned a PO-token HTTP 403. The repaired
Notebook 23 installs `yt-dlp[default]`, downloads the official temporary Deno
runtime, enables `ejs:github`, and tries default, `tv`, then `web_embedded`
clients. The latter clients are current token-free fallbacks according to the
official yt-dlp PO-token guide. The Deno release asset URL was checked, notebook
JSON parses, and the new command markers are validated; the complete Colab
download still requires a user rerun.

The next run reached the final export assertion because `Run all` continued
past the interactive widget before the user could save 32 decisions. This was
an unnecessary manual burden. Notebook 23 now pre-populates all 32 conservative
decisions from the already completed 118-sheet second label audit and records
their exact provenance, so `Run all` reaches the ZIP automatically. Manual
changes remain possible through the widget before rerunning only the export
cell.
