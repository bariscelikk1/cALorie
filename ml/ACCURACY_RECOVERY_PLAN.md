# Accuracy recovery plan

## What the 28.51% result actually measures

The locked GainsByBrains evaluation is a deliberately difficult domain-shift
test, but its supported subset is not a balanced test of all 15 classes. Its
221 stable supported windows cover only:

| Fine label | Broad target | Windows | Accuracy |
| --- | --- | ---: | ---: |
| jumping jack | jumping jack | 37 | 75.68% |
| plank variation left | plank | 37 | 0.00% |
| plank variation right | plank | 37 | 0.00% |
| pop squat | squat | 37 | 21.62% |
| squat kick | squat | 37 | 2.70% |
| sumo squat pulse | squat | 36 | 72.22% |

Therefore, 28.51% must not be described as accuracy across all supported
exercises. It measures whether unfamiliar variants are absorbed into broad base
classes. The original broad-taxonomy evaluation remains frozen and valid; this
interpretation does not relabel it after seeing predictions.

For diagnosis only, treating every variation as `unknown` gives 88.84% stable
window accuracy, 89.59% rejection on the resulting strict-unknown set, and
75.68% jumping-jack accuracy. This post-hoc number is not a promotion metric.
It demonstrates why the class ontology must be fixed before collecting the next
benchmark.

## Main problems in priority order

1. **The deployment ontology is ambiguous.** Decide whether `squat` means only
   a standard squat or also pop squat, squat kick, sumo pulse, and future
   variants. Labels, training data, and evaluation must use the same rule.
2. **The external benchmark is incomplete.** It contains only three broad
   supported classes and cannot estimate 15-class recognition accuracy.
3. **Windows are not independent examples.** The v5 training split has 4,433
   reviewed supported windows but only 284 source groups. Long videos can
   dominate through many correlated windows.
4. **The gate is over-conservative out of domain.** Its internal validation
   selected 0.90. On the locked diagnostic sweep, 0.60-0.65 recovers about 47%
   broad supported accuracy while retaining 97.65-99.15% unknown rejection.
   The locked test must not be used to choose the production threshold.
5. **The current TCN discards useful pose information.** It consumes only
   normalized x/y coordinates. MediaPipe z, visibility, joint velocities, bone
   vectors, and joint angles are not available to the classifier.
6. **A 64-frame window is a single temporal scale.** At 15 FPS it covers about
   4.27 seconds and can mix partial repetitions, transitions, and different
   movement speeds.

## Controlled experiment sequence

### A. Fix evaluation before changing architecture

- Freeze a written class dictionary with positive and negative examples.
- Create a creator/person-separated calibration set that is never used for
  gradient updates.
- Create a new locked test containing every supported class, standard forms,
  chosen variants, transitions, and unsupported exercises.
- Report class-balanced Macro F1, per-class recall, unknown precision/recall,
  boundary F1, and segment-level edit score in addition to window accuracy.
- Keep the existing GainsByBrains broad-taxonomy result as a hard variant test.

### B. Correct the training sampler and data representation

- Sample hierarchically: class, then source group, then window. Do not let one
  long source contribute hundreds of near-duplicate examples per epoch.
- Apply the Notebook 13 weights only to their original training `window_key`.
  Do not duplicate those windows and do not touch validation/test groups.
- Add train-only augmentation: left/right flip with joint swapping, small
  in-plane rotation, scale jitter, temporal speed jitter, frame drop, coordinate
  noise, and visibility masking.
- Compare four feature sets with the same split: xy baseline; xyz+visibility;
  xy+velocity; xy+velocity+bone vectors+joint angles.
- Run a 25/50/75/100% group learning curve. If validation continues improving
  with more groups, new people/views remain the best investment.

### C. Repair gate calibration

- Retrain v6 with group-balanced sampling and hard-positive weights.
- Select the gate threshold only on the independent calibration set, under an
  explicit target such as at least 95% unknown recall.
- Calibrate probabilities with temperature scaling on calibration data.
- Compare the two-stage gate against a single 16-class TCN with outlier
  exposure. A separate gate creates cascading errors and must earn its place.

### D. Improve temporal decoding

- Predict more densely at inference (8-16 frame stride).
- Add hysteresis, minimum-duration rules, and short-gap merging.
- Train with windows deliberately placed across action boundaries.
- Compare multi-scale 32/64/128-frame branches.
- If predictions remain fragmented, test an MS-TCN-style refinement stage and
  temporal smoothing loss.

### E. Compare one skeleton-aware architecture

The flattened TCN learns time patterns but does not explicitly encode the body
graph. Compare it against a small ST-GCN on the identical group split. ST-GCN
connects anatomical neighbors within each frame and the same joint through
time. Promote it only if it improves creator-separated validation and the new
locked test, not merely internal window accuracy.

## Minimal experiment matrix

| ID | Change | Purpose |
| --- | --- | --- |
| V5 | Frozen current model | Reference |
| V6-A | Hierarchical sampler + Notebook 13 weights | Test sampling correction |
| V6-B | V6-A + pose/temporal augmentation | Test robustness |
| V6-C | V6-B + velocity/bone/angle features | Test representation |
| G1 | Small ST-GCN with V6-B data | Test skeleton-aware model |
| D1 | Best model + dense smoothed decoder | Test long-video stability |

Change one block at a time. Every run keeps the same group split, seed, report
schema, and locked tests. The next training notebook should implement V6-A;
V6-B and V6-C are ablations rather than silent additions.

## References behind the plan

- Reddit model-improvement discussion: learning curves, error analysis, simple
  baselines, and controlled experiments:
  https://www.reddit.com/r/learnmachinelearning/comments/1ed380j/
- Practitioner discussion of skeleton overfitting, ST-GCN, light rotations,
  scale shifts, weight decay, and early stopping:
  https://www.reddit.com/r/computervision/comments/1e103if/
- Practitioner action-recognition overview and the importance of defining the
  action ontology and duration:
  https://www.reddit.com/r/computervision/comments/11we6sa/
- ST-GCN paper:
  https://aaai.org/papers/12328-spatial-temporal-graph-convolutional-networks-for-skeleton-based-action-recognition/
- MS-TCN paper:
  https://openaccess.thecvf.com/content_CVPR_2019/papers/Abu_Farha_MS-TCN_Multi-Stage_Temporal_Convolutional_Network_for_Action_Segmentation_CVPR_2019_paper.pdf

