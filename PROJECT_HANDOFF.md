# cALorie — current handoff

## Active work

Continue on `feat/tcn-rebuild`. This branch is the project source of truth;
`main` is not the current state. Historical web, worker, Supabase, and
deployment files are archive material and are outside the active scope.
The target is 14 dynamic exercises plus unknown, then stable long-video
segments, repetition counting, calorie estimation, and a local Python app.
Plank is retired to unknown in post-v5 experiments.

Read `ml/EXPERIMENT_BACKBONE.md`, `ml/README.md`, `ml/AGENTS.md`, and
`ml/data/ANNOTATION_GUIDE.md` for the experiment and annotation contracts.
Read `ml/POST_V6C_ROADMAP.md` for the ordered post-G2 plan, hardware choices,
promotion gates, and proposed Notebook 23-30 sequence.
Do not use locked tests for tuning or promote unresolved draft labels.

The recognition-tuning loop is now frozen. Notebook 34 may be completed and
archived as a final development diagnostic, but its reused 1,971-window test
must not trigger another threshold/sampler/loss iteration. The faulty Notebook
29D UI path is retired, but benchmark review is not abandoned. It must continue
from correctly matched dense evidence with auditable interval/timestamp
provenance. Notebook 35 is a bounded interim diagnostic: it compares frozen
V6-C and V6-F on conservative first-pass regions without training, calibration,
threshold selection, relabeling, or promotion. The current readiness audit and
lock gates remain in `ml/data/youtube_creator_benchmark_v1/BENCHMARK_LOCK_PLAN.md`.

Current lock status: the **region-classification benchmark is locked**, while
the continuous long-video benchmark remains unlocked. Six reserved creators
and continuous pose evidence exist.
A complete correct-page Codex dense visual pass now covers all 41 regions in
`ml/data/youtube_creator_benchmark_v1/codex_dense_adjudication_v1.csv`: 32
supported regions, four compound regions retained as `unknown`, and five
locators rejected because they contain no target motion. All 14 supported
classes have retained visual evidence. This is real Reviewer-A-style work, but
it is not an independent blind human review: all rows remain
`benchmark_ready=false` and require confirmation. Notebook 29C's queue archive
SHA-256 is `3c395d3bf5b534464bb4be92e969a96d75bf1d502676e7a26658034d11b887a`.
The partial 29D run touched 27 rows but locked nothing; its three wrong-page
label changes are discarded.

Notebook `ml/notebooks/35_colab_provisional_creator_diagnostic.ipynb` requires
no upload. It downloads and verifies the archived pose evidence plus frozen
V6-C/V6-F checkpoints, scores 35 regions (26 supported, nine unknown), excludes
six unresolved regions, and exports a single diagnostic ZIP. Its metrics are
not final benchmark accuracy and cannot be used to change labels or models.

Notebook 35 was executed locally end to end on the exact pinned artifacts: all
seven input hashes passed, 561 windows were aggregated into 35 regions, and the
report ZIP passed integrity checks. V6-F exceeds V6-C on provisional region
accuracy (68.57% vs 60.00%), present-label Macro F1 (67.25% vs 46.36%), and
supported accuracy (73.08% vs 53.85%), but unknown recall drops to 55.56% from
77.78%. Paired six-creator bootstrap intervals include zero for the accuracy
and Macro-F1 improvements. The artifact is archived under
`ml/artifacts/youtube_creator_benchmark_v1/provisional_diagnostic/`; no Colab
rerun is required unless independent reproduction is desired.

The user-returned Colab reproduction arrived on 2026-10-21 and is preserved
unchanged as `calorie_provisional_creator_diagnostic_report_colab.zip`
(SHA-256 `2d095fca179f210aa340423288df2152d08cafe7da96469882bb969d891fc696`).
All 14 internal hashes pass. Metrics and all discrete predictions exactly match
the local reference across 35 regions and 561 windows. The largest probability
difference is `2.47e-06`, causing no threshold or label change. This confirms
execution reproducibility but does not upgrade the provisional labels or lock
the benchmark.

The bounded independent confirmation set is complete. Reviewer `baris`
confirmed all 17 required rows: decision and label agreement are 100%, exact
boundary agreement is 88.24%, and two boundaries were corrected. The returned
CSV is preserved unchanged; the confirmation audit passes with zero errors and
no unresolved retained second reviews.

`ml/scripts/process_creator_benchmark_confirmation.py` validates the completed
review and creates `resolved_region_adjudication_v1.csv` without mutating either
reviewer's source file. `ml/scripts/build_creator_region_benchmark.py` then
locks `locked_region_benchmark_v1.csv`: 36 non-overlapping regions, six creator
videos, 14 supported classes plus unknown, and verified source archive hashes.
Training, calibration, threshold selection, and prediction-guided relabeling
remain forbidden. The next action is the one-time frozen V6-C/V6-F region
evaluation. Full-timeline segmentation evaluation remains blocked because
unreviewed video gaps are not continuous ground truth.

Notebook `ml/notebooks/36_colab_locked_creator_region_benchmark.ipynb` is that
one-time evaluation. It pins the lock commit and every input hash, verifies the
36-region contract before inference, then compares frozen V6-C and V6-F with
their already-fixed thresholds. It performs no training, calibration,
threshold search, relabeling, or model promotion. Run it once from top to
bottom in Colab and preserve the returned
`calorie_locked_creator_region_benchmark_v1_report.zip` unchanged. Its result
is a region-classification benchmark only; it cannot establish continuous
long-video segmentation quality.

Notebook 36 is complete. The unchanged Colab archive and extracted report are
under `ml/artifacts/youtube_creator_benchmark_v1/locked_region_benchmark_v1/`;
the outer SHA-256 is
`f85531da08a989f4796e8743b53e19a2c66a85c7151fd15e21bcf263eb49594a`, and
all 13 internal hashes pass. V6-F wins the frozen comparison: 69.44% versus
52.78% accuracy, 67.11% versus 44.59% 15-label Macro F1, and 71.88% versus
53.13% supported accuracy. Paired creator-bootstrap intervals for all three
deltas remain above zero. V6-F is therefore the preferred recognition
candidate, not a production-ready model. Both systems recover only two of four
true unknown regions; V6-F still sends nine supported regions to `unknown` and
has zero recall on lateral raise, sit-up, squat, and tricep extension. Freeze
this result and continue gate/data development without using or repeatedly
consulting the locked rows.

The next arc is external **development** data, not another pass over the locked
benchmark. `ml/data/repcount_development_v1/` fixes a 30-video RepCount-A
intake: ten published source codes, each with one squat, one sit-up, and one
unsupported front raise. Post-run visual review proved that `stuN` is not a
verified person identity, so the original `stu1`-`stu7` versus `stu8`-`stu10`
person-disjoint interpretation is retired. Every row starts `metadata_only`
and `training_allowed=false`; future roles must be source-group-disjoint.

Notebook `ml/notebooks/37_colab_repcount_external_development_intake.ipynb`
automatically reads only those 30 embedded video blobs from a pinned public
RepCount-A Lance revision, so it uses neither YouTube nor manual upload. It
extracts cycle-bounded contact sheets and 15-FPS MediaPipe pose, scores the
already-frozen V6-F model at threshold `0.65`, deletes raw video before export,
and returns a single diagnostic ZIP. Its provisional metadata-alignment figures
are not benchmark accuracy and cannot select a threshold or promote labels.
Visible-motion review is required before any row can be admitted. A new
versioned experiment manifest must explicitly define training and untouched
development roles without treating the source codes as identities.

A self-contained local review screen for that exact 17-row queue is under
`ml/artifacts/youtube_creator_benchmark_v1/independent_confirmation_ui/`.
It contains the correctly matched dense RGB overviews and the four supplemental
RGB-plus-pose evidence sets, stores progress in browser local storage, and
exports `calorie_creator_independent_confirmation_completed.csv`. The normal
path is one-click confirmation; correction fields appear only for disagreements.
This replaces the upload-based Notebook 29D workflow but does not itself lock
the benchmark. Import and audit the completed CSV, adjudicate disagreements,
then build continuous per-video timelines before final evaluation.

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

## Current result — Notebook 29G rejected

Notebook 29G completed on 2026-10-18. The returned archive and all internal
hashes pass. The expected repair affected exactly two frames (136 non-finite
values) in `rowan_row_02_01`; no other pose imputation occurred. The frozen
1,971-window test remained unchanged and the only training-data delta was 52
windows from three quarantined clips in two new groups.

The gate improved from 82.03% to 83.55% Macro F1, but oracle exercise Macro F1
fell from 85.57% to 83.84%. End-to-end Macro F1 fell from **79.33% to 78.23%**
and accuracy from 82.90% to 82.45%. `dumbbell_row` end-to-end F1 fell 12.75
points and `sit_up` fell 7.25 points. Creator deltas are mixed: the large
external YouTube group improves, while several MM-Fit creators regress.

Reject the 29G checkpoint for promotion and retain frozen V6-C as the
reference. The complete evidence is archived under
`ml/artifacts/v6c_source_balance_draft_retrain/`.

The next action is not a new architecture run. Notebook 30A screened all 12
initial source-balance-v2 candidates and its unchanged output is archived under
`ml/artifacts/source_balance_v2/`; all 128 internal hashes and the outer ZIP
hash pass. Dense review advances three dumbbell-row person groups, two pull-up
groups, one sit-up group, and zero lat-pulldown groups. CHRIS HERIA and THENX
feature the same athlete and are one identity group despite distinct channels.
The original lat-pulldown candidates are rejected or held for pose cropping,
camera cuts, and actor complexity.

CPU Notebook 30B is complete. Its unchanged archive and hashes are under
`ml/artifacts/source_balance_v2_dense_and_replacements/`. Codex dense review
advances 15 canonical row/sit-up/dynamic-pull-up intervals to pose audit and
rejects or holds noncanonical row variants, kickbacks, chin-ups, static holds,
and rest/instruction frames. Of five replacement sources, Alex Crockford, Nona
Bayat, and SilverSneakers advance to dense review; Tone and Tighten is rejected
for target mismatch and Joanna Soh is held for framing. Max Euceda was the only
30B download failure and remains unresolved.

CPU Notebook 30C is complete. All four targets produced 2-FPS evidence and the
Max Euceda retry succeeded. Alex Crockford's stable 529–676 s sit-up block and
two conservative Max row passages advance. Nona Bayat and SilverSneakers are
rejected for the current pose pipeline because of lower-body cropping,
close-ups, and camera changes inside the demonstrations. The unchanged 30C ZIP
is archived under `ml/artifacts/source_balance_v2_replacement_dense_review/`.

The first CPU Notebook 30D run was blocked by YouTube bot checks for all seven
sources and produced zero pose-ready windows. Its unchanged failure report is
archived under `ml/artifacts/source_balance_v2_pose_audit_failed_download/` and
supports no model or quality conclusion. The repaired 30D completed with zero
YouTube requests. It verified 280 archived 30B files and 82 archived 30C files,
then produced coarse 2-FPS pose for all 18 windows. ZIP integrity and all 117
output hashes pass; the unchanged result is archived under
`ml/artifacts/source_balance_v2_pose_audit/`. Codex overlay triage records seven
strong windows and eleven usable-with-caution windows in
`ml/data/source_balance_v2/pose_visual_triage.csv`. Every decision remains
independently unreviewed and training-disabled. This fallback cannot replace
continuous 15-FPS source extraction. Do not retrain or iteratively tune on the
already-used internal test.

CPU Notebook 30E is ready as the source-controlled continuation. It contains
no YouTube acquisition path. The user must place the seven original source
files in `MyDrive/cALorie_source_balance_v2/videos/` or select them in Colab;
each filename must contain its pinned video ID. The notebook records SHA-256,
duration, FPS, and dimensions, then extracts continuous 15-FPS pose for the 18
windows without exporting raw video. Its machine output deliberately leaves
source identity unattested and all landmarks training-disabled pending
independent source and motion/boundary review.

The user then explicitly reprioritized model work and paused the source-video
branch. T4 Notebook 31 is the active next run. It repeats the exact V6-F
multi-stream gate recipe across seeds 42, 137, and 2026. The 1,971-window test,
frozen temporal classifier, data, split, sampler, augmentation, mean-probability
fusion, and threshold `0.65` are unchanged. The report must retain every seed,
mean/std/worst-seed results, class and creator breakdowns, and the predeclared
mean-of-seeds ensemble. Do not pick the best test seed or treat a stability pass
as production promotion.

Notebook 31 completed on 2026-10-19. End-to-end Macro F1 across seeds 42, 137,
and 2026 was 81.72%, 81.88%, and 81.33% (mean 81.64%, population standard
deviation 0.23 percentage points). The predeclared ensemble reached 82.09%,
but the research gate failed: held-out YouTube present-class F1 averaged 12.06
points below V6-C, and 220 supported test windows were rejected as unknown.
The failure is gate calibration/domain generalization rather than seed
instability. The next bounded step must select an ensemble threshold using
validation only, retain an unknown-recall floor, and expose the reused internal
test exactly once after the selection is frozen. It still cannot authorize
production promotion.

T4 Notebook 32 implements that protocol. It retrains the exact three-seed
ensemble, sweeps thresholds `0.30` through `0.80` by `0.01` on validation only,
requires validation unknown recall of at least `0.85`, and maximizes validation
end-to-end Macro F1. Supported accuracy and then the higher threshold are
deterministic tie-breakers. After freezing the selected threshold, the notebook
reports test results only for that choice and the `0.65` reference.

Notebook 32 completed on 2026-10-19 and selected threshold `0.57`. It improved
test end-to-end Macro F1 from 82.09% to 82.39%, but accuracy fell from 85.34%
to 83.76%, unknown recall fell from 92.04% to 83.61%, and total errors rose from
289 to 320. The held-out YouTube and MM-Fit w18 creator gates still failed, so
`0.57` is rejected and `0.65` remains the reference.

Notebook 33 completed on 2026-10-19. Its equal-creator sampler and 50% top-30%
group-CVaR loss failed systematically: the ensemble reached 73.53%
end-to-end Macro F1, 72.10% accuracy, 80.55% unknown recall, and 67.91%
supported accuracy versus Notebook 31's 82.09%, 85.34%, 92.04%, and 82.02%.
The three seeds were stable, so this was not an unlucky initialization.
WorkoutFitness supplied 321 of 341 training groups, many with one to three
windows, and received about 84% of total sampler mass. Bicep-curl F1 collapsed
from 95.40% to 15.57%; MM-Fit w13 and w18 also regressed heavily. The returned
archive SHA-256 is
`1627f54698687be5624bc1a571b4a0ccf24b379c0014eb0968cf773b6bfff7ac`;
all internal hashes pass, and extracted evidence is under
`ml/artifacts/v6f_creator_robust_gate/`. Do not promote these checkpoints.

T4 Notebook 34 is the active bounded correction. It keeps every Notebook 31
control and threshold `0.65`, but fixes creator mass to `sqrt(window_count)`,
caps per-window weights at four times the within-gate-label median, and mixes
20% top-30% group-CVaR with 80% ordinary cross-entropy. The recipe is frozen
across seeds 42, 137, and 2026. A local audit of the exact training rows shifts
sampler mass from Notebook 33's roughly 84% WorkoutFitness concentration to
36.5% YouTube, 36.3% MM-Fit, and 27.1% WorkoutFitness, with gate labels still
50/50. Notebook 33's reused internal-test failure informed this correction,
so Notebook 34 remains development evidence and cannot establish production
generalization or authorize promotion. Return
`calorie_v6f_soft_creator_balance_report.zip` unchanged.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/34_colab_v6f_soft_creator_balance.ipynb

The three v1 review clips received a Codex visual adjudication, explicitly not
an independent human second review. Nick's 464.5–504.0 straight-leg sit-up
interval is coherent but remains pending human approval. Rowan row 02 has
several hard camera cuts and is rejected as one continuous interval. Rowan row
03 should be split to 295.0–313.5 and 314.0–330.75 around the visible shot
change. These decisions are recorded under `ml/data/source_balance_v2/`; every
row remains quarantined and excluded from training.

## Historical experiment sequence

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
YouTube present-class regressions prevent model promotion.

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
classifier; research checkpoint scores are not complete-system scores.

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
the Drive-first path was tested locally against a hash-matched 360p file.
Local Mac MediaPipe 0.10.35 aborted at PoseLandmarker startup with a Metal
graph-service error, before producing any landmark data, so the exploratory
local runner was removed. Use revised Notebook 29F on **Colab CPU** with the
private Drive backup. Neither source videos nor the failed ZIP represent
training evidence. The successful rerun and next steps are recorded below.

## Source-balance pose rerun and exploratory T4 experiment (2026-10-17)

The rerun of CPU Notebook 29F succeeded: five source videos, 17 pose-ready
windows at 15 FPS, 5,820 frames total, and 69/69 internal hashes verified.
The source ZIP is
`ml/artifacts/source_balance_v1/calorie_source_balance_v1_pose_audit.zip`
(SHA-256 `f8393f2b8c0de03a01121e544d502245cfa0729bd75e56eeac66a936bc013bf0`).
Visual triage is in `ml/data/source_balance_v1/pose_visual_triage.csv`.
Some Goku nominal pull-up windows contain hanging knee raises, actor changes,
or camera cuts; Ryan's pulldown windows are cropped. Do not treat all 17 as
exercise labels.

Three stronger windows have first-pass 4-FPS RGB boundary review in
`ml/data/source_balance_v1/annotations/first_pass/`: two Rowan dumbbell-row
passages and one Nick sit-up passage. The structural timeline audit passes
with zero errors/warnings, but all six timeline rows remain draft and
`use_for_training=false`. The user confirmed the proposed movement names,
then explicitly said they had not yet watched the review clips, so there is
**no independent visual second review**. Short 360p video-only extracts are
outside Git at `work/source_balance_v1/review_clips/`; six boundary sheets are
committed under `ml/artifacts/source_balance_v1/first_pass_boundary_sheets/`.

`ml/scripts/build_source_balance_draft_clips.py` slices the pinned 29F pose
archive reproducibly without extracting landmarks again. Its GitHub-archived
output is `ml/artifacts/source_balance_v1/calorie_source_balance_v1_draft_clips.zip`
(SHA-256 `721d69f30ec61b4c5d6a6d1a0a9782ec44b33c6511ac068458c86e0f9b671887`):
three quarantined clips, 1,726 pose frames, **two** creator/video groups.
The manifest has `training_allowed=false`, `review_status=draft`, and
`status=quarantined`. This does not solve four-class source balance.

The user explicitly asked to continue model work without watching the clips.
Notebook 29G, `ml/notebooks/29g_colab_exploratory_source_balance_retrain.ipynb`,
is a **T4 GPU exploratory diagnostic** based on Notebook 24's exact V6-C
recipe. It explicitly opts into only these three quarantined clips; all old
V6-C groups and the 1,971 internal test windows remain frozen. The notebook
pins every input hash and marks exported checkpoint promotion as disallowed.
Do not describe its eventual result as independently validated or deploy it.
Compare end-to-end macro F1, per-class scores, creator breakdown, and unknown
rejection against the frozen V6-C report; archive the returned ZIP and push
it. If promising, obtain real independent visual review and a separate final
creator-disjoint evaluation before model promotion.

The first 29G Colab run stopped before training because Rowan clip
`rowan_row_02_01` contains two undetected pose frames (136 non-finite landmark
values). The notebook now repairs sparse non-finite values by linear temporal
interpolation per joint/channel before resampling and asserts that the full
window tensor is finite. It also exports `pose_imputation_audit.csv`; this run
should record exactly two repaired frames in one clip. The three source clips,
labels, split, model recipe, and frozen test set are otherwise unchanged.
## RepCount external development v1 returned and audited (2026-10-23)

Notebook 37 returned `calorie_repcount_external_development_v1_report.zip`
(SHA-256 `fddd4e63f1162c1b48d1d81165c6e204127226824e5af500f452161f8a7219ef`).
The archive has 71 checksum-listed files; all internal hashes pass. Pose
extraction succeeded for all 30 clips, raw video is absent, and no training,
calibration, threshold change, or locked-benchmark access occurred.

Post-run RGB contact-sheet review found that the report's 8/30 metadata
alignment is not model accuracy. Published `situp` includes heterogeneous
crunch, V-up, GHD, reverse-crunch, and sit-up variants, while one nominal squat
clip does not visibly establish a squat in the selected bounds. The corrected
first-pass visible-target agreement is 16/30, still diagnostic-only. More
importantly, `stuN` is not a verified identity: the three `stu10` clips visibly
show different people, and `stu8_49`/`stu9_56` appear to share an actor and
scene. The role partition is therefore not person-disjoint validation.

The unchanged report is archived under
`ml/artifacts/repcount_external_development_v1/`; row-level contact-sheet calls
and the blocking audit are under `ml/data/repcount_development_v1/`. Notebook
37 wording now describes `stuN` as unverified source codes. Do not launch a
RepCount retrain from the original `train_pool`. Next, perform video review for
the medium-confidence rows, define clip/source-disjoint development roles, and
only then build a quarantined training experiment. The frozen V6-F threshold
remains 0.65.

CPU Notebook 38,
`ml/notebooks/38_colab_repcount_visual_adjudication_packet.ipynb`, is the next
step. It pins the post-run review CSV from commit `6b0dca6`, fetches only the
eight medium-confidence RepCount clips from the pinned Lance revision, and
automatically returns dense 4 FPS sheets plus silent 240p/8 FPS review previews
in `calorie_repcount_visual_adjudication_v1.zip`. There are no uploads, widgets,
labels, model scores, training steps, or locked-benchmark reads. Full source
videos are deleted before packaging. Run it on Colab CPU and return its ZIP;
then adjudicate those eight rows locally before defining any training pool.

Notebook 38's first Colab run reached evidence rendering but failed on the
first JPEG save because its explicit Pillow 11.1 Python layer was incompatible
with Colab Python 3.13's already-loaded native Pillow encoder (`17 given`,
`16` accepted). The notebook no longer installs or imports Pillow. Dense-sheet
resizing, labels, tiling, and JPEG encoding now use OpenCV only. Reopen the
latest notebook and run all from a fresh CPU runtime; inputs and output
contract are unchanged.

Notebook 38 returned successfully on 2026-10-23 as
`calorie_repcount_visual_adjudication_v1.zip` (SHA-256
`335a0f6bf07d0920b0dc84954a8feec43113947239cced35f8982b6ea0ee5a63`).
The archive and all 72 internally listed files pass checksum verification. It
contains eight silent previews and 61 dense JPEG pages, with no raw video,
training, or locked-benchmark access.

Dense visual adjudication resolves all eight pending clips. `stu1_53`,
`stu3_54`, `stu5_52`, `stu6_50`, `stu8_49`, and `stu9_56` map to `sit_up`;
`stu2_67` maps to `squat`; and `stu9_12` maps to `lateral_raise`. The final
frozen V6-F diagnostic is 11/30 overall (36.7%), 6/18 on supported visible
clips (33.3%), and 5/12 unknown rejections (41.7%). It scores 6/10 on squat,
0/7 on sit-up, and 0/1 on lateral raise. This is a source-shift diagnostic,
not person-disjoint accuracy.

The final row calls are in
`ml/data/repcount_development_v1/final_visible_adjudication_v1.csv`. Keep the
two observed duplicate source groups intact: `stu8_49` with `stu9_56`, and
`stu1_69` with `stu6_59`. Every row remains `training_allowed=false`. The next
experiment must predeclare source-group-disjoint roles, remain
non-promotable, keep threshold 0.65 fixed, and leave the locked creator
benchmark untouched.

## Claude migration handoff (2026-10-24)

`CLAUDE.md` is now the migration entry point for continuing the project with
Claude. It links the active branch, draft PR, required contracts, model
artifacts, locked benchmark, RepCount evidence, direct Colab notebooks, failed
experiments, collaboration preferences, and the exact constraints for the next
development experiment. It also records the post-run correction that `stuN`
is an unverified source code rather than a person identity. The root README and
RepCount intake README now point to the current interpretation instead of the
retired person-disjoint assumption. No model, label, metric, or experiment
artifact changed in this documentation-only checkpoint.

## RepCount gate rotation v1 design predeclared (2026-10-24)

The Notebook 39 design is written down and approved by the user, but the
notebook does not exist yet. Design:
`ml/data/repcount_development_v1/gate_rotation_v1/DESIGN.md`. Fold manifest:
`ml/data/repcount_development_v1/gate_rotation_v1/folds.csv`, generated and
checked by `ml/scripts/build_repcount_gate_rotation_v1.py` (`--check` mode).

A fixed hash-selected one-third holdout was audited first and rejected: it
held only one supported clip that V6-F sends to `unknown` (`stu3_54`), so it
could not measure the research question. The user chose a 3-fold
source-group rotation instead. All 28 source groups sit in exactly one
evaluation fold, and both duplicate groups stay intact. Each clip is scored
only by gates that never trained on its group, and no RepCount clip is used
for early stopping. This replaces the "one permanent untouched subset"
reading of contract item 5. Out-of-fold support: 8 gate false-unknowns,
7 gate false-accepts, and 4 wrong-class errors, which gate retraining cannot
fix.

Only the three gate streams change, following Notebook 31's `train_gate`
recipe. The V6-E classifier, fusion, threshold 0.65, and all hyperparameters
stay frozen. A three-seed control arm (no RepCount data) separates the data
effect from retraining noise. The stopping rule is predeclared: one run, with
reruns only for crashes or bugs. The data effect counts as supported only if
the seed-median out-of-fold false-unknown count is at most 5/18 and below
the control, unknown rejection is at least the control and at least 5/12,
and internal-test Macro F1 is no more than 1.0 pp below the control.
Whatever the outcome, the run is non-promotable. The locked benchmark is
not read.

Tested locally: the fold builder is deterministic, both duplicate groups are
intact, no group spans folds, and every evidence row remains
`training_allowed=false`. Not yet tested: Notebook 39 itself, including
whether the Notebook 37 report ZIP exposes per-window pose arrays in the
expected `(T, 17, 4)` layout. Next action: build Notebook 39 against this
design, dry-run its manifest and window logic locally, push, and give the
Colab link.

## Notebook 39 built and dry-run locally (2026-10-24)

`ml/notebooks/39_colab_repcount_gate_rotation.ipynb` (generated by
`ml/scripts/build_notebook39.py`) implements the gate rotation v1 design.
Runtime: Colab T4, `Run all`, no uploads. Output:
`calorie_repcount_gate_rotation_v1_report.zip`. Inputs are pinned to Notebook
31's training commit `9874773` and to design commit `9544dfb`, and every
input is SHA-256 checked. The locked creator benchmark is not an input.

The control arm reuses Notebook 31's archived seed gates instead of
retraining them (recorded in `DESIGN.md` before any run). Treatment retrains
the three gate streams for 3 folds x 3 seeds using Notebook 31's code and
training seeds. Before training, the notebook stops unless frozen V6-F
reproduces Notebook 37's 30 clip predictions and the control gates
reproduce Notebook 31's internal-test Macro F1 within 0.3 pp. Afterwards it
evaluates the predeclared stopping rule and writes `stopping_rule.json`.

Tested locally (CPU dry run, `CALORIE_DRY_RUN=1`, one epoch, 1,500-window
base subsample, seed 42 only): every code cell ran. All input hashes passed.
The pool rebuilt to Notebook 31's exact 9,986 training and 1,971 test
windows. RepCount produced 305 windows. V6-F parity matched with a maximum
gate difference of 1.2e-7. Control parity passed for all three seeds. The
dry-run ZIP was created. Dry-run numbers are not results.

Design-relevant fact measured on the full pool, not a result: with no extra
weighting, RepCount carries about 2% of the supported sampler mass and about
5% of the unknown mass in each fold. The treatment is therefore a small
dose. A null result may mean the dose was too small, not that the data is
useless.

Not tested: the full T4 run, including its duration (27 gate trainings,
about 3x Notebook 31), and GPU/CPU numerical differences beyond the parity
tolerance. Next action: the user runs Notebook 39 on a T4 and returns the
ZIP. Archive it unchanged, verify its checksums, and analyze it against the
stopping rule without rerunning.

## RepCount-A intake v2 plan drafted (2026-10-24, not approved)

The full RepCount-A metadata (pinned `d4c2ad3`, all three JSONL hashes
verified) holds 1,040 videos. About 760 cover six supported classes
(squat, sit_up, pull_up, bench_press, push_up, jumping_jack), and about 280
are unknown candidates. The draft plan is in
`ml/data/repcount_intake_v2/INTAKE_PLAN.md`. It covers a ~60-clip pilot
before scaling, scene-embedding source groups validated on the two known v1
pairs, and train/dev/sealed-test roles that keep v1 and pilot clips out of the
sealed test. Labeling uses three tiers: automatic pose-rule gates, Claude
visual review of failures plus a 10% audit, and a 20-clip user spot-check.
It proposes a new `auto_verified` review status, limited to non-promotable
experiments. That status changes the annotation contract and awaits user
approval. No notebook has been built.

The Notebook 39 Colab link in `CLAUDE.md` is now commit-pinned. It opens in
Colab from the in-app browser. The user still sees a white screen, which
points to their browser or session, not the link.

## Intake v2 approved; Notebook 40 pilot built (2026-10-24)

The user approved `ml/data/repcount_intake_v2/INTAKE_PLAN.md`, including the
new `auto_verified` review status for non-promotable experiments only. That
status is now defined in `ml/data/ANNOTATION_GUIDE.md`. The pilot selection
`ml/data/repcount_intake_v2/pilot_selection.csv` is deterministic: built by
`ml/scripts/build_repcount_intake_v2_pilot.py` (`--check` mode) from the
pinned metadata. It has 8 clips in each of 8 buckets, spread across 7-8
source codes per bucket and excluding v1. The 30 v1 clips are included as
scene references.

Notebook 40 (CPU, `calorie_repcount_intake_v2_pilot.zip`), generated by
`ml/scripts/build_notebook40.py`, is pinned to plan commit `1319d6f`. It
returns 15-FPS pose (normalized and image-space), 12-frame contact sheets,
and 3 scene thumbnails per clip. It deletes each raw video immediately and
records per-clip failures in `source_audit.csv`. Colab link (commit-pinned):
https://colab.research.google.com/github/bariscelikk1/cALorie/blob/b1e3f527c61942cf774c266d3936ffe7c95db824/ml/notebooks/40_colab_repcount_intake_v2_pilot.ipynb

Tested locally (Python 3.12, `CALORIE_DRY_RUN=1`, 4 real clips from the
pinned mirror): every cell completed. The mirror contains all 1,040 metadata
IDs plus 1 extra. Pose, sheets, and thumbnails were written, and no raw video
remained. Bench-press clip `stu1_5` was flagged `low_pose_detection`
(74.5%): its contact sheet shows mid-clip face close-up cutaways, a real
example of edited footage that tier-1 checks must catch. Local OpenCV was
5.0 (a mediapipe dependency); Colab pins 4.11. Not tested: the full 94-clip
Colab run.

Next action: the user runs Notebook 40 on CPU and returns the ZIP. Then
archive it, compute scene embeddings and calibrate grouping on the v1 pairs,
visually review all 64 pilot clips, and finalize the tier-1 rules (once, on
pilot clips only).

## Notebook 40 pilot evidence returned (2026-10-25)

The user's browser shows a blank page for every Colab link, even though the
links render in the in-app browser. Because Notebook 40 is CPU-only, Claude
ran it on the user's Mac from the same pinned inputs. Provenance is in
`ml/artifacts/repcount_intake_v2/pilot/README.md`. The first run lost 33
clips to temporary Hugging Face errors and was discarded. The notebook now
retries blob reads (commit `e5e539151e4f037eaeab55d0c721900abde918f5`), and the rerun returned all 94 clips
with 0 errors. Archived ZIP SHA-256:
`e9bb439a62ea224120aab256809a6d3dd6e737cb487d7a7a4b7cf8c5cbf54bae`. All 414 internal hashes pass.

Pose detection: 60 pilot clips `ok`; 4 below 80% (3 bench press: `stu1_5`
with mid-clip face cutaways, `stu4_4`, `stu7_7`; 1 other: `stu5_28`).
Every other bucket had a median detection of 100%.

Next: compute scene embeddings and calibrate grouping on the v1 pairs,
visually review all 64 pilot contact sheets, and fix the tier-1 rules once
on pilot clips only. Notebook 39 (GPU) is still unrun. It could run on the
Mac's Apple GPU (MPS) if Colab stays unusable; that would need a small
device option and is not built.

## Intake v2 pilot reviewed; grouping and tier-1 rules locked (2026-10-25)

Details: `ml/data/repcount_intake_v2/PILOT_RESULTS.md`. Claude reviewed all 64
pilot contact sheets (`pilot_visual_review_v1.csv`). 51 are usable, and 13 are
not: edited cutaways, talking-head tutorials, crowded or partner scenes, and
compound moves such as muscle-ups and push-up-to-pike. For usable clips, the
published action matched the visible motion in every supported bucket.

Scene grouping (`ml/scripts/repcount_intake_v2_scene_groups.py`) uses a frozen
ResNet-50 with a 0.85 cosine merge threshold. On the 94 clips it merges
exactly the two known v1 duplicate pairs (0.929, 0.987); the closest distinct
pair is 0.794. Pairs from 0.78 to 0.90 get a visual check in the full intake.

Tier-1 rules `tier1_v1` (`ml/scripts/repcount_intake_v2_tier1.py`)
auto-accept 27 of 64 pilot clips with 0 wrong or unusable, and send all 13
unusable clips to review. Front-raise and `others` clips are always reviewed.
Because the rules were set on the pilot itself, the real error rate must come
from the 10% audit in the full intake.

Next: build CPU shard notebooks for the remaining ~950 clips (same evidence
as Notebook 40), run them locally, then group, apply tier-1, audit, review,
and assign roles. Notebook 39 (GPU) is still unrun.

## Full intake running; review checkpoint; Notebook 39 on MPS (2026-10-26)

Notebooks 41 (8 shards, 946 clips) are running on the user's Mac. Review has
started on finished clips: `ml/data/repcount_intake_v2/full_visual_review_v1.csv`
is a partial checkpoint (78 tier-1 review clips from shards 0 and 4; the
audit sample is drawn only after all shards finish). On new clips, tier-1
auto-accepted only 21 of 99 (pilot: 27 of 64), so the rules are stricter
than the pilot suggested. Three published labels were visibly wrong: bench
press `stu8_4` is a deadlift, bench press `stu7_13` is a back squat, and
front raise `stu9_17` is a behind-the-neck shoulder press.

Notebook 39 gained an opt-in `CALORIE_DEVICE=mps` (commit `d34a840`). A dry
run on the Mac's GPU passed both parity checks. The single predeclared real
run started on MPS on 2026-10-26; its result is not in yet.

## Notebook 39 result: data effect not supported (2026-10-26)

The single predeclared run finished on the Mac's GPU. Archive:
`ml/artifacts/repcount_gate_rotation_v1/` (README has the full table). The
verdict is `data_effect_not_supported`: the seed-median false-unknown count
was 6/18 against a required at most 5/18. The other four criteria passed.
Observations, not claims: unknown rejection rose from 7 to 11 of 12 (control
median), end-to-end from 13 to 18 of 30, and internal Macro F1 from 81.64% to
82.26%. Sit-ups stayed at 0/7, because accepted sit-ups are classified as
`bench_press` by the frozen V6-E classifier. So the next RepCount training
experiment must retrain the classifier as well as the gate. Per the design,
no rerun or tuning follows from this result.

## Intake v2: all evidence in; tier-1 and audit done (2026-10-27)

Evidence for 945 of 946 clips is archived (`ml/artifacts/repcount_intake_v2/full/`).
Role groups are in `full_role_groups_v1.csv`: merge at 0.84, 857 groups,
largest 15, and 670 clips eligible for the sealed test. Tier-1 `tier1_v1`
(`full_tier1_v1.csv`) auto-accepts only 201 of 945 (21%; the pilot gave 42%),
so 744 clips need review. The audit (`full_review_queue_v1.csv`, 28 clips)
found 1 wrong label (bench press `stu8_11` is a leg machine) and 2 unusable
clips (jumping jack `train1715` is a group class; squat `stu8_64` shows legs
only). No class exceeded the 1-error rule, so auto-accept stands. Bench press
sat at the limit, so its remaining 7 auto-accepts are also reviewed (stricter
than the rule). The review of the remaining 646 clips continues in
`full_visual_review_v1.csv` (133 rows so far).

## Intake v2 labeled: 718 usable clips (2026-10-27)

Claude reviewed every clip that tier-1 did not auto-accept (779 full-intake
plus 64 pilot), plus the audit sample. Final table:
`ml/data/repcount_intake_v2/intake_v2_labels_v1.csv`; summary in
`INTAKE_RESULTS.md`. 718 of 1,009 clips are usable: unknown 229, squat 99,
jumping_jack 90, bench_press 81, pull_up 80, sit_up 68, push_up 58, plus a few
lateral raises, deadlifts, and shoulder presses. Published RepCount labels
were wrong for 41 usable clips; visible motion decided every label. All rows
remain `training_allowed=false`.

Next: the user's 20-clip spot-check, then assign train/dev/sealed-test roles
by role group, then predeclare a training experiment that retrains the
classifier as well as the gate (Notebook 39 showed gate-only retraining
cannot fix sit-ups).

## Intake v2 spot-check passed (2026-10-27)

The user checked 20 hash-sampled usable clips (`spotcheck_sample_v1.csv`)
and found all 20 labels correct. Next: assign train/dev/sealed-test roles by
role group, then predeclare the classifier-plus-gate training experiment.

## Training v1 stage A: fail by 0.24 pp on the internal guard (2026-10-27)

Notebook 42 ran once on the Mac GPU; the archive is
`ml/artifacts/repcount_training_v1_stage_a/` (README has the full table). The
verdict is `stage_a_fail`: six of seven criteria passed, but internal-test
Macro F1 dropped 2.24 pp against a 2.00 pp limit. On RepCount dev the gains
were large and group-robust: Macro F1 61% to 86% (bootstrap CI +17.7 to +33.4
pp), sit-ups 0% to 80%, squats 69% to 88%, unknown rejection 82% to 94%.
The internal cost is concentrated in sit-up (−15.4) and pull-up (−16.7)
recall, plus unknown (−4.6). The sealed test remains unseen, so a
predeclared v2 with one change can still be judged honestly. Stage B did not
run.

## Training v2 stage A: PASS (2026-10-27)

Notebook 43 (Notebook 42 plus a 50% RepCount sampler cap) ran once on the
Mac GPU; the archive is `ml/artifacts/repcount_training_v2_stage_a/`. All
seven criteria held. On RepCount dev, Macro F1 rose from 61.4% to 85.4% (CI
+17.2 to +31.8 pp), sit-ups from 0% to 90%, and unknown rejection from 82% to
91%. Internal Macro F1 fell 1.61 pp (limit 2.00); internal sit-up recall
recovered (98% to 99%). Next: stage B, one scoring of the frozen v2 models on
the sealed test with the same rule, after the user's go-ahead. Still
non-promotable.

## Training v2 stage B (sealed test): FAIL on sit-ups; RepCount arc closed (2026-10-27)

Notebook 44 scored the frozen v2 models once on the 140-clip sealed test;
the archive is `ml/artifacts/repcount_training_v2_stage_b/`. Six of seven
criteria held, but the sit-up recall seed median was 42.9% (required 50%).
v2 versus V6-F on the sealed test: Macro F1 57.3% to 75.4% (CI +11.4 to +26.3
pp), squats 44% to 72%, unknown rejection 80% to 94%, real exercises called
unknown 40 to 26. Remaining sit-up misses are gate rejections, not bench-press
confusions. Dev had shown 90% sit-ups, which was optimistic. Per the v2 plan
the RepCount arc closes: v2 is not promoted, and no v3 cap sweep follows. The
sealed test is now spent. Any further attempt needs a new idea, a new plan,
and a fresh held-out set.

## Long-video test set v1 locked (2026-10-27)

8 new-creator, real-person follow-along videos (3.87 h) were selected by a
logged rule (`ml/data/long_video_test_v1/PLAN.md`, 6 screened-out videos with
reasons), processed locally, and labeled second by second: 437 segments,
about 70% `unknown` time. The user second-reviewed a 44-segment hash sample
(all correct) and approved 10 edge-case rules, which are added to the
annotation guide. The set is locked (`LOCK.json`). Next: predeclare and run
the full-session scorer (V6-F vs v2; raw and fixed smoothed decoders) once.

## Long-video evaluation 1: full sessions expose the gate (2026-10-27)

First scoring on the locked long-video set
(`ml/artifacts/long_video_test_v1/eval1/`). Smoothed 15-label Macro F1 was
V6-F 32.6% and v2 32.3%: v2 is not shown better (CI −6.2 to +7.6 pp). Both
reject more than half of real exercise time as `unknown` (V6-F 55%, v2 65%).
v2 improves push-ups (25→82%), squats, jumping jacks, downtime handling, and
flicker, but loses curls (31→7%) and lateral raises (84→7%). Sit-up, row,
lunge, shoulder press, and tricep extension are 0% for both. Main bottleneck
on real sessions: the gate is far too strict, and the uncovered classes need
data. Nothing was tuned on this set.
