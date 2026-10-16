# Post-V6-C improvement roadmap

- Status date: 2026-10-15
- Active branch: `feat/tcn-rebuild`
- Reference system: V6-C two-stage TCN
Immediate work: finish Notebook 22, independently review its timelines, then
build the new creator-separated training package.

This is the execution plan after the G2 architecture comparison. It extends
`EXPERIMENT_BACKBONE.md`; it does not rewrite the evidence or promotion
decisions from the completed V6 experiments.

## Why the next step is data and evaluation

The three G2 replacement classifiers did not beat V6-C on the excluded-creator
comparison. All systems used the same frozen V6-C gate and the same 1,198
windows:

| System | Present-class Macro F1 |
| --- | ---: |
| V6-C | **30.39%** |
| Equal G2 ensemble | 29.79% |
| BiGRU | 28.48% |
| Adaptive GCN | 28.41% |
| Pose Transformer | 27.40% |

The approximately 49% accuracy and 56.45% shared unknown recall show a large
creator/domain gap. Seven supported classes are absent from this comparison.
The evidence therefore does not justify another blind classifier swap. The
next experiments address new people and views, pose failures, incomplete
action windows, and open-set rejection in that order.

V6-C already consumes 100 channels: normalized joint x/y, frame velocity,
directed bone vectors, and joint angles. A proposal to “add motion features”
must state what is new beyond those channels.

## Non-negotiable experiment contract

- Split by original person, creator, and source video before producing windows
  or augmentation. Related windows never cross train, calibration, and test.
- Never tune from a locked external test or from the final test partition.
- Use first-pass labels only for review and extraction. Training requires an
  independent second review, adjudication, and a passing strict audit.
- Change one experimental block at a time. Keep the V6 split, seed, sampler,
  report schema, and comparison checkpoint fixed unless the experiment
  explicitly tests one of them.
- Save configuration, source hashes, split assignments, sample counts,
  checkpoints, predictions, per-class metrics, confusion matrices, and audit
  results in every report ZIP.
- Report creator-level results as well as aggregate results. A gain from one
  small class or creator is a hypothesis, not a promotion.
- Archive failed runs with their reason. Do not silently stack a failed change
  into the next experiment.

Promotion uses present-class Macro F1 and per-class recall for supported
recognition, plus unknown precision/recall, AUROC or OSCR, and creator-level
breakdowns for rejection. Accuracy alone cannot promote a system. The first
practical target is a repeatable improvement above V6-C's 30.39% excluded-
creator Macro F1; **35% is a milestone, not a promised result**. A candidate
must also avoid a material unknown-recall or creator-level regression.

## Ordered execution plan

| Stage | Proposed notebook | Runtime | Controlled change | Required output |
| ---: | --- | --- | --- | --- |
| 0 | 22, then 23 | CPU | Complete new-video evidence, second review, pose audit, clip slicing | reviewed landmark/data ZIP |
| 1 | 24 | T4 GPU | Retrain exact V6-C with only the accepted new groups added | data-only comparison report |
| 2 | 25 | T4 GPU | Add visibility/missingness channels and realistic pose-failure augmentation | missingness ablation report |
| 3 | 26 | T4 GPU | Build complete-action and phase-aware temporal samples | temporal-window ablation report |
| 4 | 27 | T4 GPU | Add multi-stream open-set scoring to the retained TCN | gate/open-set report |
| 5 | 28 | T4 GPU | Pretrain on unlabeled continuous landmarks, then fine-tune | pretraining report |
| 6 | 29 | T4 GPU | Compare PoseC3D only if the earlier stages still leave a pose-noise gap | backbone comparison report |
| 7 | 30 | CPU first; T4 if trained | Add boundary-aware long-video decoding | dense timeline report |

Notebook numbers after 22 are reservations. Each notebook is implemented and
committed only when its preceding evidence and gate are complete.

### Stage 0 — finish the new evidence package

Notebook 22 currently uses the two new 720p YouTube sources, covering 61:59,
and 118 visually prepared first-pass intervals. It extracts continuous 15 FPS
landmarks and keeps every row out of training.

After it returns `calorie_youtube_long_workouts_v2_review_landmarks.zip`:

1. preserve and checksum the report;
2. inspect detection coverage and pose previews for both sources;
3. independently review every low-confidence interval and at least 10% of the
   remainder;
4. adjudicate label and boundary disagreements;
5. run the strict timeline audit with the independent review root;
6. reject or repair intervals with unusable pose coverage;
7. slice accepted continuous landmarks into class clips and retain source-group
   identity in the manifest.

Notebook 23 is CPU work. It must not train a model. Its proposed output is
`calorie_youtube_long_workouts_v2_reviewed_clips.zip` containing reviewed CSVs,
agreement and strict-audit reports, clip arrays, the manifest, pose coverage,
provenance, and checksums.

### Stage 1 — measure the data effect with the exact V6-C model

Retrain the existing V6-C architecture and training procedure with the accepted
new source groups. Do not add new channels, losses, or thresholds in this run.
Compare it with the frozen V6-C checkpoint on unchanged creator-separated
validation and test evidence.

The report must include a class-by-creator support matrix before training. New
hours are useful only when they add reliable motion, new people/views, hard
unknowns, or weak-class coverage. Continue targeted collection for sparse or
weak classes such as lat pulldown, dumbbell row, tricep extension, lateral
raise, shoulder press, pull-up, and varied deadlift views rather than collecting
another undirected hour.

### Stage 2 — expose pose failure instead of hiding it

Compare the retained 100-channel input with a controlled representation that
adds per-joint visibility and an explicit detection/missingness mask; test z
only as a separate ablation. Train-only corruption should resemble real pose
failures: joint or body-part occlusion, short frame occlusion, confidence-aware
noise, and anatomically correct left/right mirroring.

Every augmentation family needs a visual audit before training. Reject the
block if its creator-separated gain comes with a significant unknown-recall or
important-class regression.

### Stage 3 — train on complete actions and temporal phases

The fixed 64-frame window can contain a partial repetition, a boundary, or a
speed mismatch. Build samples from reviewed action intervals and complete
cycles where possible, then compare phase-aligned resampling and controlled
speed changes with the frozen V6-C window sampler. Include explicit boundary
windows so transitions do not become supported actions.

This stage should determine whether the model needs multi-scale 32/64/128-frame
branches. Do not add those branches before the data-only complete-action
comparison establishes a temporal-scale problem.

### Stage 4 — improve open-set rejection with separate motion streams

Keep the proven TCN family and compare a CrossMax-inspired gate with separate
joint, bone, and velocity streams. Fuse calibrated evidence and measure
distance to supported-class prototypes on a creator-separated calibration
set. Select thresholds under an explicit unknown-recall constraint; do not
choose them from the locked test.

This experiment addresses the shared 56.45% unknown recall in Notebook 21.
It must report supported-class damage at each operating point, not only unknown
AUROC.

### Stage 5 — use unlabeled continuous landmarks

Pretrain the temporal encoder on continuous landmarks with masked sequence
reconstruction, then compare a contrastive tuning stage before supervised
fine-tuning on the same reviewed labels. This can use unlabeled portions of
eligible training sources, but never locked evaluation sources.

Run a linear or nearest-neighbor probe before full fine-tuning. Stop if the
representation does not improve creator-separated clustering or probing; that
prevents an expensive pretraining idea from silently changing the production
model.

### Stage 6 — one final backbone comparison

If the earlier audits show that noisy or missing keypoints still dominate,
compare PoseC3D heatmap volumes with the best retained V6-C pipeline. Heatmap
representations can preserve spatial uncertainty that flattened coordinates
discard. Use the same groups and evaluation protocol. Do not reopen a broad
architecture search: BiGRU, Pose Transformer, Adaptive GCN, and the full G1
ST-GCN have already failed to replace V6-C under the project tests.

### Stage 7 — stabilize complete long-video output

Once the frame/window classifier improves, add a boundary head or temporal
segmentation refinement and calibrate minimum duration, hysteresis, short-gap
merging, and transition penalties. Score boundary F1, segment edit score,
supported Macro F1, and unknown rejection on complete held-out timelines.
Repetition counting and calorie estimation follow only after segment identity
and boundaries are stable.

## Active-learning loop

After every retained model, rank candidate review windows by:

1. low margin or high entropy;
2. gate/classifier disagreement;
3. high-confidence mistakes on reviewed creator evidence;
4. weak class-creator cells in the support matrix;
5. pose-coverage failures near action boundaries.

Review a small ranked batch, preserve reviewer provenance, audit it, and rerun
only the next controlled experiment. This turns labeling time into targeted
evidence rather than more correlated windows from the same source.

## Decision log to maintain after every stage

Append one row here or in the stage report:

| Date | Stage/run | Only changed block | Primary metrics | Creator regressions | Decision | Commit/report |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-10-15 | G2 creator comparison | classifier family | V6-C 30.39%; ensemble 29.79%; BiGRU 28.48%; AGCN 28.41%; transformer 27.40% present-class Macro F1 | all systems remain weak; seven classes absent | retain V6-C; improve evidence first | `ml/artifacts/g2/creator_comparison/` |
| 2026-10-16 | Notebook 22 pose audit | two new continuous landmark sources | 55,787 finite frames; 99.52% and 99.56% detection; supported-interval minimum 99.44% | labels still need full-motion boundary approval | accept pose extraction; proceed to CPU Notebook 23 | `ml/artifacts/youtube_long_v2/landmarks/` |
| 2026-10-16 | Notebook 23 reviewed clips | conservative reviewed clips from two new training groups | 32 clips; 15,195 frames; 715 s supported plus 326 s unknown; supported detection minimum 99.33% | contact-sheet audit does not claim frame-accurate full-motion review | accept as train-only evidence; run exact V6-C data-only retrain | `ml/artifacts/youtube_long_v2/reviewed_clips/` |
| 2026-10-16 | Notebook 24 data-only retrain | two verified groups added to exact V6-C training | oracle exercise F1 85.57%→87.09%; gate F1 82.03%→79.44%; end-to-end F1 79.33%→77.39% | held-out YouTube improves, but all four substantial MM-Fit creators regress; lunge/squat are over-rejected | reject checkpoint; retain V6-C and proceed to controlled missingness ablation | `ml/artifacts/v6c_longv2_data_retrain/` |
| 2026-10-16 | Notebook 25 visibility/missingness | add visibility+missing mask; separately add pose-failure corruption | mask variant gate F1 84.78%, end-to-end F1 80.88%; occlusion variant gate F1 71.66% | mask variant lowers oracle F1 and regresses several MM-Fit creators; MM-Fit visibility is synthetic and source-identifying | do not promote full model; retain mask as gate hypothesis, reject occlusion, proceed to temporal sampling on 100-channel base | `ml/artifacts/v6d_visibility_missingness/` |

## Research basis

- [Open-set skeleton action recognition and CrossMax](https://arxiv.org/abs/2312.06330): motivates separate joint, bone, and velocity evidence plus distance-aware unknown rejection.
- [Recovering Complete Actions for cross-dataset skeleton recognition](https://proceedings.neurips.cc/paper_files/paper/2024/hash/a78f142aec481e68c75276756e0a0d91-Abstract-Conference.html): motivates complete-action priors, boundary conditioning, and smooth temporal transformations.
- [Realistic skeleton data augmentation](https://openaccess.thecvf.com/content/WACV2024W/RWS/papers/Cormier_Enhancing_Skeleton-Based_Action_Recognition_in_Real-World_Scenarios_Through_Realistic_Data_WACVW_2024_paper.pdf): motivates body-part, keypoint, and frame occlusion plus correct mirroring.
- [STARS](https://arxiv.org/abs/2407.10935) and its [official implementation](https://github.com/TaatiTeam/STARS): motivate masked prediction followed by contrastive tuning for few-label transfer.
- [PoseC3D](https://openaccess.thecvf.com/content/CVPR2022/papers/Duan_Revisiting_Skeleton-Based_Action_Recognition_CVPR_2022_paper.pdf): motivates a heatmap-based robustness comparison after coordinate-pipeline fixes.
- [DuoCLR](https://openaccess.thecvf.com/content/ICCV2025/html/Tian_DuoCLR_Dual-Surrogate_Contrastive_Learning_for_Skeleton-based_Human_Action_Segmentation_ICCV_2025_paper.html): motivates multi-scale contrastive features for dense action segmentation.
- [SkeleTR](https://openaccess.thecvf.com/content/ICCV2023/papers/Duan_SkeleTR_Towards_Skeleton-based_Action_Recognition_in_the_Wild_ICCV_2023_paper.pdf): supports auxiliary-data regularization and evaluating skeleton recognition in unconstrained video.
- [PYSKL](https://github.com/kennymckormick/pyskl): official implementation reference for reproducible PoseC3D/ST-GCN-family comparisons.

These papers motivate hypotheses; they do not override this repository's
creator-separated tests or authorize combining several changes in one run.
