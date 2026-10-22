# cALorie ML

New long-video labels must follow `data/ANNOTATION_GUIDE.md` and pass the
timeline audit before landmark extraction:

```bash
python3 ml/scripts/audit_timeline_annotations.py path/to/annotation/csvs --strict
```

For an independently repeated subset, add `--second-root path/to/review/csvs`
to report time-sampled canonical-label agreement. The audit checks temporal
coverage, overlaps, canonical labels, training eligibility, boundary precision,
and reviewer/confidence metadata.

This directory contains the local, dataset-driven rebuild of cALorie. The
primary task is 14-class workout recognition from temporal pose landmarks, with
an additional `unknown` class. Exercise-specific state machines count complete
repetitions. Plank was retired from the active target after v5; future training
maps archived plank samples to `unknown` while historical reports remain intact.

See `EXPERIMENT_BACKBONE.md` for the fixed post-v5 implementation sequence,
`ACCURACY_RECOVERY_PLAN.md` for the interpretation of the v5 external results,
and `POST_V6C_ROADMAP.md` for the ordered plan after the G2 creator comparison.

## Active arc — lock the external creator benchmark

Recognition tuning on the reused 1,971-window internal test is frozen. V6-C
and V6-F remain fixed candidates; Notebook 34 is at most a final development
diagnostic and cannot start another sampler/threshold/loss loop.

The active work is the six-creator external benchmark. Existing evidence has
41 candidate regions across six reserved creator videos and all 14 proposed
classes, but zero locked labels. Follow
`data/youtube_creator_benchmark_v1/BENCHMARK_LOCK_PLAN.md`. CPU Notebook 29C
created the review queue. The old Notebook 29D interface is retired after its
page-selection bug produced three obvious wrong-context relabels; none of those
relabels is accepted as benchmark evidence. Manual visible-motion review itself
is not abandoned: it continues from the archived dense evidence through a
correct-page, auditable adjudication path.

That correct-page Codex pass is now recorded in
`data/youtube_creator_benchmark_v1/codex_dense_adjudication_v1.csv`. It retains
32 supported regions and four compound `unknown` regions, rejects five
no-target-motion locators, and restores visible candidate coverage for all 14
supported classes using the four supplemental Michelle regions. It is not a
blind or independent human pass. Its bounded independent confirmation has now
been completed, audited, and resolved without mutating either reviewer's source
file. The result is the locked 36-region classification contract described
below; the broken 41-row UI remains retired.

Notebook `35_colab_provisional_creator_diagnostic.ipynb` is the historical
bounded diagnostic. It scores frozen V6-C and V6-F on 35 conservative first-pass
regions (26 supported cores and nine explicit unknown regions), excludes six
unresolved split/supplemental regions, and exports region-, class-, creator-,
and creator-bootstrap diagnostics. It performs no training or threshold
selection. Its results are directional only and cannot lock the benchmark or
authorize model promotion.

The notebook was also executed locally against the exact archived inputs and
the verified output is preserved under
`artifacts/youtube_creator_benchmark_v1/provisional_diagnostic/`. V6-F improves
provisional region accuracy from 60.00% to 68.57%, present-label Macro F1 from
46.36% to 67.25%, and supported accuracy from 53.85% to 73.08%. The tradeoff is
material: unknown recall falls from 77.78% to 55.56%, and the paired creator-
bootstrap intervals include zero for the accuracy and Macro-F1 deltas. Treat
V6-F as the stronger recognition candidate but not as a promoted replacement.

Notebook `36_colab_locked_creator_region_benchmark.ipynb` is the active,
one-time frozen evaluation. It verifies the immutable 36-region contract and
all evidence/model hashes, creates deterministic 64-frame windows, compares
the fixed V6-C and V6-F systems, and exports one report ZIP. It performs no
training, calibration, threshold selection, or relabeling. The resulting
metrics apply only to locked-region classification, not continuous long-video
segmentation.

## Active source-balance intake

The rejected Notebook 29G run showed that adding 52 windows from three draft
clips did not fix source imbalance: end-to-end Macro F1 fell from 79.33% to
78.23%, with large regressions for dumbbell row and sit-up. Frozen V6-C remains
the reference.

`data/source_balance_v2/` is now the active intake queue. It contains 12
metadata-only candidates with three distinct creator/channel IDs per target
class (`dumbbell_row`, `sit_up`, `lat_pulldown`, `pull_up`) and a fail-closed
audit. Run:

```bash
python3 ml/scripts/audit_source_balance_v2.py
```

CPU Notebook `30a_colab_screen_source_balance_v2.ipynb` completed for all 12
sources. Its unchanged output and checksum are archived under
`artifacts/source_balance_v2/`. Visual screening advances three independent
dumbbell-row people, two pull-up people, one sit-up person, and no lat-pulldown
person. CHRIS HERIA and THENX show the same athlete and are grouped together.

Notebooks 30B and 30C completed the dense visual review. The unchanged evidence
archives and Codex decision tables are preserved under
`artifacts/source_balance_v2_*` and `data/source_balance_v2/`. Eighteen
canonical row, sit-up, and dynamic pull-up windows now advance to pose audit;
the new lat-pulldown candidates failed full-body pose/framing requirements.

CPU Notebook `30d_colab_source_balance_v2_pose_audit.ipynb` is complete. Its
first run was blocked by YouTube bot checks and the unchanged zero-pose report
is archived. The repaired run made no YouTube request, verified the archived
30B/30C inputs, and produced coarse 2-FPS pose for all 18 windows. All 117
output hashes pass. Codex overlay triage marks seven windows strong and eleven
usable with visibility cautions; none is independently reviewed or training-
enabled. The unchanged result is under `artifacts/source_balance_v2_pose_audit/`.
This screen cannot replace continuous 15-FPS extraction. Independent motion/
boundary and source/use review remain mandatory.

CPU Notebook `30e_colab_source_balance_v2_continuous_pose_from_upload.ipynb`
implements a source-controlled gate without a YouTube downloader. It mounts the user's
Drive folder `MyDrive/cALorie_source_balance_v2/videos/` and falls back to a
manual Colab upload widget. Filenames must contain the seven pinned video IDs.
The notebook hashes and probes the source files, extracts continuous 15-FPS
pose for the same 18 windows, and exports no raw video. Source identity remains
unattested and training remains disabled until independent review. This data
path is currently paused.

T4 Notebook `31_colab_v6f_seed_stability.ipynb` was the active model step. It
repeats Notebook 27's exact V6-F gate recipe with seeds 42, 137, and 2026 while
freezing every input, split, augmentation and sampler recipe, classifier,
fusion, and the `0.65` gate threshold. It reports mean, standard deviation, worst seed,
per-class and per-creator metrics, plus a predeclared mean-of-seeds ensemble.
The test cannot select a seed or threshold, and the notebook cannot promote a
production model.

Notebook 31 is complete and archived under `artifacts/v6f_seed_stability/`.
The three seeds are stable, but the held-out YouTube creator gate fails and the
ensemble rejects 220 supported windows as unknown. Notebook 32 is therefore
the active bounded experiment. `32_colab_v6f_validation_gate_calibration.ipynb`
chooses one ensemble threshold from validation only under the fixed `0.85`
unknown-recall floor, then evaluates that frozen choice once on the reused
internal development test. It compares only the selected threshold and the
`0.65` reference on test. Production promotion remains disabled.

Notebook 32 is complete and archived under
`artifacts/v6f_validation_calibration/`. Its validation-selected threshold
`0.57` raised test Macro F1 by only 0.30 points while reducing accuracy by 1.57
points and unknown recall by 8.42 points. It is rejected; `0.65` remains the
reference. Notebook 33 is complete and rejected. Equal creator mass plus a 50%
top-30% creator-group CVaR mixture reduced ensemble end-to-end Macro F1 from
82.09% to 73.53%, accuracy from 85.34% to 72.10%, unknown recall from 92.04%
to 80.55%, and supported accuracy from 82.02% to 67.91%. Hundreds of tiny
WorkoutFitness groups received about 84% of sampler mass; bicep-curl F1 fell
from 95.40% to 15.57%. The verified report is archived under
`artifacts/v6f_creator_robust_gate/`, and the checkpoint is not promoted.

Notebook 34 is the active development-only experiment. It keeps the frozen
data, split, classifier, architecture, augmentation, three seeds, fusion, and
threshold `0.65`. Creator mass is proportional to the square root of its
window count, each per-window sampler weight is capped at four times the
within-label median, and group-CVaR contributes 20% instead of 50%. A local
sampler dry run assigns about 36.5% mass to YouTube, 36.3% to MM-Fit, and
27.1% to WorkoutFitness while retaining 50/50 supported/unknown mass. Because
Notebook 33's reused internal-test diagnostic informed this recipe, Notebook
34 cannot establish production generalization or authorize promotion.

Colab: https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/34_colab_v6f_soft_creator_balance.ipynb

## Verified progress

The landmark pipelines now produce six compatible archives: Workout/Fitness,
MM-Fit exercise and `unknown`, and three reviewed long-form YouTube batches.
The newest YouTube batch adds 205 usable segments from four independent source
videos after seven low-detection `unknown` segments are filtered. All archives
retain source groups so related windows stay in one split.

The locked 917-second mixed workout exposed opposite failure modes. TCN v1
recognized 66.5% of supported exercise windows but rejected only 32.7% of
unsupported exercise and 26.2% of transitions. TCN v3 rejected 79.6% of
unsupported exercise and 88.9% of transitions, but recognized only 33.0% of
supported windows. Its higher overall accuracy was driven by the many
`unknown` windows. The two-stage v4 candidate recovered supported accuracy to
47.5%, but unsupported rejection fell to 32.7% and transition rejection to
54.0%. The gate is therefore the current bottleneck. See
[`artifacts/v4/README.md`](artifacts/v4/README.md).

## Current 14-class target

The evidence-driven class set is squat, push-up, jumping jack, pull-up, lunge,
sit-up, shoulder press, dumbbell row, tricep extension, bicep curl,
lateral raise, bench press, deadlift, and lat pulldown. Nine are
available in Workout/Fitness Video; MM-Fit supplies additional people and five
new movements. Burpee, mountain climber, and glute bridge remain external-data
candidates because the currently audited source contains too few canonical
examples to support a defensible trained class.

## First milestone

1. Audit dataset access, licenses, identities, and labels.
2. Populate `data/manifests/raw_v1.csv` without assigning the same person or
   source video to multiple splits.
3. Validate the manifest:

```bash
python ml/scripts/validate_manifest.py ml/data/manifests/raw_v1.csv
```

Training does not begin until the manifest contains reviewed samples and passes
validation.

## Model plan

- MediaPipe Pose provides frame-level landmarks.
- A Random Forest provides an explainable learned baseline.
- A gate TCN learns supported motion versus `unknown`/transition.
- A second TCN classifies accepted windows among the 14 supported exercises.
- A validation-only threshold sweep calibrates the gate without using locked-test labels.
- State machines count exercise phases and complete cycles.
- Evaluation reports Macro F1, per-class precision/recall/F1, confusion matrix,
  repetition MAE, exact-count accuracy, and off-by-one accuracy.

## Colab notebooks

The current rebuild uses twenty-nine sequential notebooks:

1. `01_colab_extract_workoutfitness.ipynb` converts selected Workout/Fitness videos to normalized 17-joint pose sequences.
2. `02_colab_prepare_mmfit.ipynb` converts the labeled MM-Fit exercise sets to the same representation.
3. `02b_colab_prepare_mmfit_unknown.ipynb` exports the unlabeled gaps between MM-Fit sets as `unknown` examples for rest and transitions.
4. `03_colab_train_tcn.ipynb` preserves the single-stage 16-class baseline.
5. `04_colab_analyze_mixed_video.ipynb` evaluates the archived single-stage candidate on locked GainsByBrains and scores it against frozen labels.
6. `05_colab_extract_youtube_mixed_landmarks.ipynb` downloads three reviewed long-form training videos and exports their labelled landmark segments.
7. `06_colab_extract_additional_youtube_landmarks.ipynb` processes the three earlier reviewed YouTube training videos that were missing from TCN v2, adding 111 segments without touching the locked tests.
8. `07_colab_extract_youtube_training_v4.ipynb` extracts 212 reviewed segments from four additional single-person long workouts while keeping the new creator-separated test locked.
9. `08_colab_train_two_stage_tcn.ipynb` trains the binary gate and 15-class exercise TCN from all six versioned archives in one T4 session.
10. `09_colab_evaluate_two_stage_tcn.ipynb` evaluates the two-stage checkpoint on locked GainsByBrains using CPU and exports a scored report.
11. `10_colab_extract_gate_hard_negatives.ipynb` uses CPU to extract independent movement-like `unknown` examples and supported exercise variants from previously unused Workout/Fitness classes.
12. `11_colab_train_hard_negative_tcn.ipynb` performs a controlled T4 retrain with the seventh hard-negative archive while keeping the v4 architecture and evaluation procedure fixed.
13. `12_colab_evaluate_hard_negative_tcn.ipynb` runs the v5 checkpoint on the unchanged locked GainsByBrains benchmark using CPU.
14. `13_colab_mine_hard_positives.ipynb` reuses the seven existing landmark archives and frozen v5 checkpoint to find reviewed training windows that the gate wrongly treats as `unknown`, then exports auditable sample-weight recommendations for the next retrain.
15. `14_colab_train_v6a_hierarchical_tcn.ipynb` retires plank, preserves the historical group split, samples class -> source group -> window, and applies Notebook 13 weights only to matching training windows.
16. `14b_colab_train_v6a1_tempered_tcn.ipynb` corrects V6-A's over-aggressive equal-group sampler by assigning each group square-root-tempered mass while preserving class balance and training-only hard-positive weights.
17. `15_colab_train_v6b_augmentation.ipynb` freezes V6-A.1's split and sampler, visualizes and applies train-only reflection, rotation, speed, frame-drop, and coordinate-noise augmentation.
18. `16_colab_train_v6c_kinematic_features.ipynb` retains V6-B augmentation and replaces the 34-coordinate input with 100 channels of coordinates, velocity, bone vectors, and joint angles.
19. `17_local_calibrate_gate.ipynb` runs on Mac CPU, calibrates V6-B and V6-C gates on three held-out creators, and compares the modular V6-C-gate/V6-B-classifier system without loading the locked test.
20. `18_colab_calibrate_dense_decoder.ipynb` runs on CPU, increases inference density to eight-frame strides, and calibrates hysteresis, minimum action duration, and short-gap merging on the same excluded creator timelines.
21. `19_colab_compare_stgcn.ipynb` trains a small two-stage ST-GCN on the exact V6 split, sampler, augmentation, and test windows, then exports a side-by-side comparison with V6-C.
22. `20_colab_train_pose_model_suite.ipynb` trains BiGRU, Pose Transformer, and Adaptive GCN classifiers on the frozen V6 split and compares them with V6-C.
23. `21_colab_compare_g2_creators.ipynb` compares the frozen G2 classifiers on the existing three-creator calibration set without tuning or promotion.
24. `22_colab_review_extract_youtube_long_v2.ipynb` loads 118 visually prepared first-pass intervals for two new long videos, audits them, downloads 720p sources, and exports continuous 15 FPS landmarks for independent second review.
25. `23_colab_review_build_youtube_long_v2.ipynb` runs on CPU, downloads and verifies Notebook 22's archived report, applies the recorded second contact-sheet label audit plus conservative trims to all 20 supported and 12 deterministic unknown intervals, and automatically exports source-group-safe clips and a compatible manifest; an optional widget can override any decision.
26. `24_colab_retrain_v6c_youtube_long_v2.ipynb` runs on a T4 GPU and retrains the exact V6-C system with only the two verified Notebook 23 groups added to training; all old assignments and the 1,971-window test remain frozen, and the notebook exports baseline deltas plus creator-level evidence.
27. `25_colab_visibility_missingness_ablation.ipynb` runs on a T4 GPU and compares two 134-channel variants on the exact Notebook 24 evidence: visibility plus explicit missing masks, then the same representation with separate train-only pose-failure augmentation. Original V6-C and Notebook 24 remain fixed controls.
28. `26_colab_complete_action_temporal_resampling.ipynb` runs on a T4 GPU, preserves the 100-channel V6-C model and all fixed windows, and adds train-only complete-cycle candidates resampled to 64 cumulative-motion phase positions; validation and the 1,971-window test remain unchanged.
29. `27_colab_multistream_open_set_gate.ipynb` runs on a T4 GPU, freezes Notebook 26's temporal exercise classifier, trains joint/bone/velocity binary gate streams, and selects a CrossMax-inspired probability/prototype fusion on validation under an explicit 85% unknown-rejection constraint before reading the unchanged test.

Notebook 08 downloads all six versioned landmark ZIPs from GitHub by default.
Run it on T4 and preserve `calorie_two_stage_tcn_report.zip`. Notebook 09 runs
on CPU and downloads the archived report automatically. Its locked external
evaluation shows that v4 recovers supported recognition to 47.5% but reduces
unsupported rejection to 32.7%; the gate still needs better hard negatives,
boundary handling, or a revised decision rule.

Notebook 10 is the first corrective data step after that diagnosis. It does not
use the locked GainsByBrains video. Its output
`calorie_workoutfitness_gate_hardneg_v1.zip` is intended for the next controlled
gate retraining experiment in Notebook 11. Notebook 11 downloads all seven
archives automatically and exports `calorie_two_stage_tcn_hardneg_report.zip`.
The v5 internal test reached **82.17% gate Macro F1**, **83.78% oracle exercise
Macro F1**, and **73.43% end-to-end Macro F1** with a validation-selected gate
threshold of **0.90**. Because adding groups changes the internal split,
Notebook 12 remains the required promotion test.

Notebook 13 begins the next controlled correction after Notebook 12 showed that
v5 rejects unsupported motion reliably but over-rejects supported exercises.
It downloads the same seven compact landmark archives used by Notebook 11,
reconstructs the deterministic v5 training split, and scores only reviewed,
supported training windows with the frozen gate. Validation, internal test,
locked GainsByBrains evaluation, and known draft YouTube groups remain excluded.
It exports `calorie_v5_hard_positive_mining.zip` with window scores, hard-positive
rows, clip summaries, pose previews, and recommended weights. A later retrain
must join those weights back to the original windows rather than append copies.

Notebook 14 implements V6-A from the fixed experiment backbone. It runs on T4,
downloads the existing landmark evidence, maps archived plank windows to
`unknown`, excludes unresolved draft groups, and exports
`calorie_v6a_hierarchical_tcn_report.zip`. Its report includes immutable split
assignments and sampler weights so V6-B, V6-C, and the ST-GCN comparison can use
the same evidence.

The completed V6-A run showed that fully equal source-group probability
over-amplified tiny groups. Its active-14 oracle exercise Macro F1 was 84.75%
and end-to-end Macro F1 was 71.63%, below the same-window v5 diagnostics of
88.11% and 76.70%. The failed run remains archived under `artifacts/v6a/`.
Notebook 14b is the controlled correction: group mass is proportional to the
square root of its window count, between equal-group and raw-window sampling.
V6-B augmentation begins only if this corrected base is acceptable.

V6-A.1 recovered the regression: its gate Macro F1 was 80.39%, end-to-end
Macro F1 was 76.76%, and unknown recall was 82.39%. On the exact same active-14
test windows, v5 reached 76.70% end-to-end Macro F1. V6-A.1 is therefore a
neutral, auditable sampling base rather than a claimed accuracy promotion.
Notebook 15 implements V6-B on the frozen V6-A.1 split and saves an augmentation
pose preview in its report before V6-C changes the feature representation.

V6-B improved oracle exercise Macro F1 from **84.81% to 86.17%** and
end-to-end Macro F1 from **76.76% to 78.97%** on the identical 1,971 internal
test windows. Its gate Macro F1 decreased from **80.39% to 79.18%**, so the
augmentation block is accepted while independent gate calibration remains
necessary. Notebook 16 freezes this accepted V6-B setup and changes only the
input representation: normalized x/y coordinates, frame velocity, directed
bone vectors, and joint angles.

V6-C improved gate Macro F1 from **79.18% to 82.03%**, internal end-to-end
Macro F1 from **78.97% to 79.33%**, and end-to-end balanced accuracy from
**80.43% to 82.38%**. Its oracle exercise Macro F1 decreased from **86.17% to
85.57%**. Because the two-stage checkpoints are modular, a diagnostic V6-C
gate plus V6-B exercise classifier reached **81.15%** end-to-end Macro F1 on
the same internal test. That hybrid is not promoted from test evidence.
Notebook 17 uses three excluded creator groups for provisional calibration and
system comparison. It runs on local CPU and never reads the locked long-video
test. The first local run used 90 segments and 1,198 windows. V6-C ranked first
at a provisional threshold of **0.95**, with **56.76%** accuracy, **30.65%**
Macro F1 across the eight labels present, and **67.53%** unknown recall. This
is evidence of strong domain shift rather than a final decision threshold: seven
supported classes are absent and four present exercises have zero recall. Its
historical timeline labels still require a final visual spot-check before the
threshold can be frozen.

Notebook 18 keeps the V6-C checkpoint and provisional 0.95 gate threshold
frozen while calibrating only temporal decoding. Its local validation run used
5,073 dense windows. The selected decoder improved present-class Macro F1 from
**29.89% to 30.69%** and unknown recall from **67.88% to 68.36%**. This small
gain confirms that temporal stabilization reduces flicker but cannot solve the
remaining data-domain and exercise-class errors.

Notebook 19 is the controlled graph-model comparison. Its 17 graph nodes use
normalized x/y coordinates and velocity while anatomical edges replace V6-C's
flattened bone-vector and angle representation. G1 improved oracle exercise
Macro F1 from **85.57% to 88.09%**, but its gate Macro F1 fell from **82.03% to
74.52%** and unknown recall collapsed from **74.58% to 16.85%** at the
validation-selected 0.10 threshold. End-to-end Macro F1 therefore fell to
**67.93%**, so the full ST-GCN is rejected. A diagnostic V6-C gate plus G1
classifier reached **79.25%** Macro F1, essentially tied with V6-C's **79.33%**;
this test-set combination is retained only as a hypothesis for independent
validation.

## External evaluation

The next long-workout candidate batch is documented in
`data/youtube_long_workouts_v2/`. It contains 61:59 from two new creators and
118 visually prepared first-pass intervals. Every row remains
`use_for_training=false`: the first pass is evidence for Notebook 22, not an
independent approval. Notebook 22 runs on CPU, downloads the 720p sources, and
extracts continuous landmarks. Its output remains excluded from training until
pose coverage is audited, an independent second review is adjudicated, and the
strict timeline audit passes. The subsequent controlled work is defined in
`POST_V6C_ROADMAP.md`.

Notebook 04 exports model predictions, but it cannot measure accuracy without
independent human labels. Score an exported mixed-video analysis with:

```bash
python ml/scripts/score_exported_mixed_video.py \
  --predictions path/to/window_predictions.csv \
  --annotations path/to/labels_v1.csv \
  --output path/to/evaluation
```

Keep each external-test video and its labels out of training. Compare future
models on the same frozen tests using supported-class accuracy, unknown and
transition rejection, balanced accuracy, macro F1, and per-movement errors.
