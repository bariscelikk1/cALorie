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

Notebook 27 has returned and is archived under
`ml/artifacts/v6f_multistream_gate/`. Validation selected mean stream
probability at threshold 0.65 while satisfying 90.96% validation unknown
rejection. On the unchanged test, gate Macro F1 is 83.95%, frozen temporal
exercise Macro F1 is 89.11%, end-to-end Macro F1 is 81.72%, and accuracy is
84.17%. This is the strongest aggregate candidate. MM-Fit w13 and held-out
YouTube present-class regressions prevent production promotion.

The user explicitly reprioritized the next work: build a comprehensive locked
creator benchmark before self-supervised pretraining. The existing creator
comparison contains only lunge, push-up, squat, and unknown, so it cannot
support a 14-class promotion decision. The new candidate package is under
`ml/data/youtube_creator_benchmark_v1/`. It projects all 14 supported classes
across four previously unused creators (BullyJuice, TIFF x DAN, Buddy Fitness,
and STRIQfit), with roughly 140 minutes of source video. Every row is external
test only: training, calibration, and threshold selection are forbidden.
Coverage is metadata-derived until visible-motion review.

Notebook 28 is now reserved for CPU evidence extraction: temporary 360p
downloads, metadata capture, compact full-timeline contact sheets, and
continuous 15 FPS landmarks. Notebook 29 now gathers denser RGB evidence for
independent interval review; only after the labels are audited and locked can
Notebook 30 compare frozen V6-C and V6-F. Self-supervised pretraining remains
deferred.

Notebook 28 is implemented as
`ml/notebooks/28_colab_extract_creator_benchmark_v1.ipynb`. From a fresh Colab
CPU runtime, `Run all` downloads the candidate contract from pinned commit
`062f43d86208f06930ae87297c421abe82e164b9`, verifies hashes and source
exclusions, downloads 360p temporary videos with multiple diagnostic
fallbacks, creates dense compact contact sheets, and extracts continuous 15 FPS
landmarks. It never runs a classifier and excludes raw videos from the ZIP.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/28_colab_extract_creator_benchmark_v1.ipynb

Runtime: CPU. Expected output:
`calorie_creator_benchmark_v1_evidence.zip`.

The first Notebook 28 run reached STRIQfit `Kw89u6WtPC8` after downloading the
earlier sources, but all three old download attempts failed: Colab's Node was
below yt-dlp's supported JavaScript-runtime requirement, progressive/DASH
requests returned unavailable or HTTP 403, and web-safari exposed only images.
The revised notebook installs current Deno automatically, passes its absolute
path to yt-dlp, enables EJS through npm, and tries default, web-embedded,
Android VR, web-safari HLS, and generic exact-360p strategies with diagnostics.
This is a download-path fix only; benchmark sources, resolution, labels, and
model policy are unchanged.

The next run downloaded the sources but failed at the first contact-sheet seek
with `Could not decode frame at 0.50s`. A valid container/height probe is not
enough because Colab OpenCV may not decode the selected VP9/AV1/HLS-derived
stream. Notebook 28 now tests OpenCV seeking at two timestamps and, only when
needed, transcodes the temporary source with ffmpeg to H.264/yuv420p 360p
video without audio. Contact sheets and landmark extraction then consume the
same verified decode-safe path. Raw and normalized videos remain outside the
output ZIP.

The conditional decoder check still proved nondeterministic: the contact-sheet
cell again failed at the first OpenCV seek. Notebook 28 now normalizes every
source once, without trying to reuse the original codec for extraction. It
also removes OpenCV random seeking from contact-sheet generation entirely:
ffmpeg extracts timestamped JPEGs sequentially, and OpenCV reads only those
JPEG files. MediaPipe consumes the normalized H.264 stream sequentially.

A history audit then compared Notebooks 05-07, 22, and 23. The older successful
360p extraction notebooks requested format `134` directly (video-only H.264).
Notebook 23 later adapted to YouTube's EJS changes by downloading the official
Deno release ZIP and trying default, `tv`, and `web_embedded` clients while
using ffmpeg for visual review clips. Notebook 28 now reuses that proven
pattern: format 134 first, Notebook 23 fallbacks second, Deno from the GitHub
release asset, EJS from GitHub, unconditional H.264 normalization, and
sequential ffmpeg contact-frame extraction.

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

## Notebook 28 returned evidence (2026-10-16)

The user returned `calorie_creator_benchmark_v1_evidence.zip`. Its outer
SHA-256 is
`3c9930fc3086b68240082668648722836c8959c373a58268347788d7ab24b3c4`;
ZIP integrity and every internal checksum pass. Four finite `frames x 17 x 4`
arrays contain 132,602 frames at 15 FPS. BullyJuice, TIFF x DAN, and STRIQfit
provide 125,151 frames across 139.05 minutes at a weighted 99.10% direct pose
detection rate.

All 85 contact sheets were inspected. Buddy Fitness `PY6DrbX4W4o` is an
instructional slide deck made from drawings and still diagrams rather than a
filmed person. Its apparent 81.39% pose detection is therefore meaningless for
this benchmark, and the entire source is rejected. The other three sources
show real people and retain source-level visible support for 11 of 14 classes;
exact action intervals are not yet approved.

The rejected source removes `deadlift`, `lat_pulldown`, and `sit_up` coverage.
Three unused replacement creators were checked against the exclusion inventory,
official chapters, and downloaded full-video storyboards: Michelle Briehler
`phFvFuLUFEw`, Criticalbench `lKHGBuanBsY`, and TRAIN WITH GAINSBYBRAINS
`7-mVPCVJMtI`. Their storyboards visibly show real people and the missing
motions. The next compute unit is CPU Notebook 28B, which extracts only these
three gap-fill sources. It preserves the locked-test rules and requires only
`Runtime -> Run all`.

## Notebook 28B gap-fill extraction (2026-10-16)

`ml/notebooks/28b_colab_extract_creator_benchmark_gapfill.ipynb` is the CPU
`Run all` notebook for those three replacements. It pins manifest commit
`4beaa4fa120f4a6995c760673d81c27e43ad5eee`, verifies all three input hashes,
and asserts the exact replacement IDs before any download. It reuses Notebook
28's Deno/EJS-enabled yt-dlp fallbacks, 360p H.264 normalization, sequential
ffmpeg contact-sheet generation, and continuous 15 FPS MediaPipe extraction.

The sole download is
`calorie_creator_benchmark_v1_gapfill_evidence.zip`. It excludes raw videos
and model predictions. After the user returns it, verify outer and internal
hashes, inspect every contact sheet, reject unsuitable sources or intervals,
and merge accepted evidence with the three retained Notebook 28 sources. Do
not train, calibrate, choose thresholds, or inspect model predictions until
the six-source interval labels and coverage audit are frozen.

## Notebook 28B returned evidence; interval labels remain draft (2026-10-16)

The user returned `calorie_creator_benchmark_v1_gapfill_evidence.zip`; outer
SHA-256 is
`4d0f3efed5216f0f46e96478c9777fc652814a346046f5866309357efc38e050`.
ZIP integrity and all 64 internal checksums pass. The three arrays add 91,525
finite frames over 101.69 minutes with a 97.97% weighted source detection rate.

All 52 new contact sheets were reviewed independently of model predictions.
All three sources show real people, but the 10-second contact-sheet spacing
does not justify exact action boundaries. The previous `locked_intervals_v1.csv`
overstated annotation certainty and was replaced by
`ml/data/youtube_creator_benchmark_v1/candidate_intervals_v1.csv`. Its 37
draft locators propose 14 classes over 1,664 seconds; 99.88% minimum pose
detection describes these broad regions, not label purity. Dense pose review
found substantial standing/talking inside a Criticalbench deadlift region.

No six-source benchmark scores are valid yet. Collect denser RGB evidence,
visually label motion boundaries, independently review uncertain intervals,
and run the temporal annotation audit before freezing labels. Preserve all six
sources for external test only. Once labels really are locked, compare the
already frozen V6-C and V6-F models without training, calibration, or threshold
selection on these sources. Report accuracy, supported Macro F1, per-class
recall, unknown rejection, creator metrics, and confusion matrices.

Notebook 29 (`ml/notebooks/29_colab_dense_creator_rgb_review.ipynb`) is the
CPU `Run all` step to obtain denser RGB evidence without manual uploads. It
pins commit `752e741c96a1647b880e6222aa4989a03e0b18bb`, verifies the
candidate and source CSV hashes, reuses Notebook 28B's Deno/EJS and 360p
download fallbacks, and produces one ZIP with 2 FPS contact sheets and five
seconds of context around each of the 37 draft regions. The ZIP contains no
raw video or model predictions. Review it before any label lock.

## Notebook 29 returned; dense RGB first pass (2026-10-17)

The user returned `calorie_creator_benchmark_dense_review_evidence.zip`.
Outer SHA-256:
`5f2f28a7a89177d1e6675d742bf60c9a4851f657baee89d710694716022e9301`.
ZIP integrity and all 367 internal checksums pass. It has 363 contact-sheet
pages for the 37 draft regions, no raw video or model predictions. The first
pass inspected overview montages containing two sampled tiles per page (726
tiles total); it did not inspect every 2-FPS frame. The ZIP and review table
are in `ml/artifacts/youtube_creator_benchmark_v1/dense_review_evidence/`.

First-pass outcomes: 26 regions have plausible target cores but need trimming;
five have no supported target action; two proposed lateral raises are compound
upright-row-to-90-degree-raise movements and stay unknown; two floor twist
presses need bench-press variant adjudication; two broad Michelle RDL regions
need splitting. Criticalbench's second deadlift region contains explanation,
and four TIFF x DAN candidate push-up regions show cooldown/stretching.
GAINSBYBRAINS changes from sit-ups to other abdominal movements inside the
broad candidate. Only 12 of 14 classes currently have plausible unambiguous
core support; bench press may become a 13th after adjudication, while lateral
raise needs a newly reviewed interval. All labels remain draft, and no valid
six-source promotion score exists.

Next: review full 2-FPS pages around proposed edges, independently repeat
ambiguous labels, build continuous timelines (unknown for rest/transition),
run the annotation audit, then lock labels before frozen-model scoring. Keep
the six source videos outside all training and threshold work.

Full-timeline Michelle Briehler storyboards revealed standard dumbbell bench
press around minutes 4–6 and seated lateral raises around minutes 32–35 that
the initial 37-region selection missed. Four draft locators are in
`ml/data/youtube_creator_benchmark_v1/supplemental_candidates_v1.csv`, commit
`0e2ae05fd5a82ea6e55afbc068b6ab7ebd1b53f9`. CPU Notebook 29B
(`ml/notebooks/29b_colab_supplement_creator_rgb_review.ipynb`) reuses or
downloads only that existing external-test video and returns 2-FPS RGB sheets
for those four regions. These are not final labels; wait for its ZIP before
revising class coverage. The first Notebook 29B run was blocked by YouTube's
"Sign in to confirm you're not a bot" challenge on Colab, across all four
download variants. This is an access block, not a missing video format.
Notebook 29's earlier ZIP proves that its source was decoded there, but the
raw source was deliberately not exported and Colab storage may have expired.
The repaired Notebook 29B first reuses a live Notebook 29 Colab cache, then
looks for `MyDrive/cALorie/source_videos/phFvFuLUFEw.mp4` (360p preferred,
saved 720p accepted), and only then tries yt-dlp. It stops after the first
bot challenge. Do not put the raw video in GitHub or the review ZIP.

## Supplemental pose review from archived landmarks (2026-10-17)

The user correctly noted that creator videos were collected to extract
landmarks, and those landmarks already exist. The accepted gap-fill evidence
ZIP, archived at `ml/artifacts/youtube_creator_benchmark_v1/gapfill_evidence/`,
contains all 33,796 continuous 15 FPS landmark frames for Michelle Briehler
`phFvFuLUFEw` (ZIP SHA-256 `4d0f3efed5216f0f46e96478c9777fc652814a346046f5866309357efc38e050`).
No new pose extraction or video download is needed for the four supplemental
regions. `ml/scripts/render_creator_supplement_pose_review.py` reproduced 43
2 FPS pose contact-sheet pages and copied four existing 10-second RGB context
pages into `ml/artifacts/youtube_creator_benchmark_v1/supplemental_pose_review/`.
The ZIP is also available in the user-facing outputs folder. All internal
checksums and ZIP structure were verified. The bench regions visibly show
repeated supine presses, while the seated arm-elevation regions require more
careful canonical-label and boundary review. Do not treat these four draft
locators as locked labels. Notebook 29B's dense RGB rerun is optional only if
pose plus archived coarse RGB cannot settle visual ambiguities; it is not the
normal path for landmark extraction. The creator sources stay external test
only, and no model score may be promoted before independent interval review.

CPU Notebook 29C (`ml/notebooks/29c_colab_creator_label_review_queue.ipynb`)
is the next reproducible `Run all` step. It downloads only five small CSV/JSON
inputs from pinned commit `9f09b3dcba4376285fab0a6260821111c721d765`,
checks their SHA-256 hashes, combines 37 existing first-pass regions with four
supplemental pose-reviewed locators, and produces a 41-row draft review queue,
independent-review template, draft class coverage, overlap diagnostics, and
one ZIP. It does not download video, run pose extraction, score checkpoints,
or mark any row final. Local execution verified 41 rows across six creators and
found one first-pass core three seconds outside its earlier coarse locator
(`ojs_squat_02`), which is flagged for review rather than silently clipped.
The final external test remains on hold until independent motion/boundary
review and the timeline audit actually pass.

## Independent model and product review (2026-10-17)

`ml/INDEPENDENT_REVIEW_2026-10-17.md` audits the saved V6-C/V6-F results,
per-class support, creator shift, benchmark status, and worker integration.
Its priority is to lock the six-creator labels on CPU, score frozen candidates
once, then decide whether new creator-diverse training data or model changes
are warranted. The current web worker still runs its earlier heuristic
classifier; research checkpoint scores are not deployed product scores.

## Source/class confounding intervention (2026-10-17)

`ml/data/source_balance_v1/` now records eight **metadata-only** training
candidate videos from distinct new creators for dumbbell row, sit-up, lat
pulldown, and pull-up. `ml/scripts/audit_source_balance.py` checks their IDs
and creator names against existing and locked external inventories, and shows
that the long-v2 retrain added only one creator for row/pulldown while pull-up
and sit-up remained single-source. No candidate was downloaded, visually
reviewed, labeled, or trained; all have `training_allowed=false`. Next perform
CPU visual/pose screening and independent labels before a T4 data-only retrain.
The CPU `Run all` contact-sheet screen is
`ml/notebooks/29d_colab_screen_source_balance_candidates.ipynb`; it gracefully
records unavailable sources and packages one ZIP without raw video.
The first 29D revision had a cache-path collision: both the source-balance
candidate CSV and locked-benchmark candidate CSV were saved as the same local
`candidates.csv`, causing a false video-ID overlap assertion before screening.
The input cache now preserves repository-relative paths and rechecks all four
hashes. Rerun 29D from the top; no new labels or model outputs were created by
the failed run.

Notebook 29D returned `calorie_source_balance_v1_screening.zip` on 2026-10-17.
It is archived under `ml/artifacts/source_balance_v1/`, with outer and all
internal hashes verified. All eight 360p sources yielded 71 contact-sheet pages.
Source-level visual triage and 17 coarse dense-review locators are in
`ml/data/source_balance_v1/`. Rowan Row and Goku Pump are the most promising
row/pull-up candidates; Ryan, Michael, Sydney, and Nick need variant review;
Jeff is low yield and Howcast has major body-cropping risk. Nothing from this
batch is yet a locked label or training example. The next step is CPU dense
RGB review around the 17 locators, then pose audit and independent labeling.
`ml/notebooks/29e_colab_dense_source_balance_review.ipynb` is the next CPU
`Run all` step for those locators. It keeps all candidates out of training.

Notebook 29E returned `calorie_source_balance_v1_dense_review.zip` on
2026-10-17. The archive is under `ml/artifacts/source_balance_v1/` (outer
SHA-256 `0f868ab7fb27d0b812bd512a29393549f7eb8d7f6ddf27875ab77d57cc66052c`);
all 187 internal hashes pass. All 17 2-FPS RGB regions were extracted. Human
contact-sheet first-pass decisions are recorded in
`ml/data/source_balance_v1/dense_visual_first_pass.csv` as **draft locators**, not
verified labels. Rowan Row has the strongest sustained dumbbell-row candidate
around 295–332 s. Goku Pump has apparent pull-ups, especially near 295–345 s,
but multiple people and edits require actor-specific clips. Nick Walker has
side-view sit-up-looking sets near 463–504 s; a later twisting variant needs
canonical review. Ryan's pulldown material is brief or cropped. Sydney's
weighted torso raises and other abdominal work need variant review; Howcast
is too cropped/cut, and Michael's full pull-ups are not established in the
reviewed interval. Nothing is eligible for training yet. Next: CPU continuous
pose-quality audit on the promising candidate windows, independent motion and
boundary review per `ml/data/ANNOTATION_GUIDE.md`, then only audited clips can
enter a T4 data-only V6-C retrain. The four-class multi-creator gap remains open.

CPU Notebook 29F (`ml/notebooks/29f_colab_audit_source_balance_pose_candidates.ipynb`)
implements that pose audit for the 17 first-pass windows in five videos. It
automatically fetches checksum-pinned manifests from commit `5315822`, reuses
29D/29E cached 360p sources or downloads them, and exports 15 FPS pose arrays,
1 FPS overlay sheets, quality metrics, and a failure manifest in one ZIP. The
setup was locally executed against the pinned files and produced the expected
five sources / 17 windows; every code cell was syntax-checked. Full Colab
video/MediaPipe execution awaits the user's Run all and returned ZIP. Every
output remains draft and excluded from training.

The user's first 29F ZIP had `pose_ready=0` because a new Colab runtime lost
the 29D/29E video cache, and YouTube bot-authentication blocked all five
sources. The ZIP itself and six internal hashes are sound; it is archived as
`ml/artifacts/source_balance_v1/calorie_source_balance_v1_pose_audit_colab_blocked.zip`.
The five exact 360p source files were then downloaded successfully on the Mac
and preserved outside Git under
`/Users/bariscelik/Documents/Codex/2026-10-14/se/work/source_balance_v1/videos/`.
They are also privately backed up in the user's Google Drive folder
`cALorie_source_balance_v1` (ID `1dztxSj58OfKoSvCzQj5dnmpNq0-Mi7Hd`).
The revised Notebook 29F checks file hashes and uses Drive before YouTube;
the new `ml/scripts/run_source_balance_pose_audit_local.py` can extract from
the local preserved files. Neither source videos nor failed ZIP represent
training evidence. Full local pose extraction was still in progress at this
handoff checkpoint.
