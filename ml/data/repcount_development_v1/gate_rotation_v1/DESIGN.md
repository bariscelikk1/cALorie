# RepCount gate rotation v1 — predeclared design (Notebook 39)

Status: design approved by the user on 2026-10-24. Notebook 39 is not built
yet. Nothing here is a result. Every row in
`../final_visible_adjudication_v1.csv` stays `training_allowed=false`; this
directory is the separate versioned experiment manifest.

## Research question

Can adjudicated, source-diverse RepCount development data reduce
false-`unknown` gate errors on real sit-ups and squats without damaging
`unknown` rejection on source groups the gate never saw?

## Why rotation instead of one fixed holdout

A fixed one-third holdout (hash-selected per class, duplicate groups intact)
was tested first. It held only one supported clip that frozen V6-F rejects as
`unknown` (`stu3_54`), so the research question would rest on a single clip.
The user chose a 3-fold source-group rotation instead: every clip is scored
exactly once by gates that never trained on its source group. This replaces
contract item 5's "one permanent untouched subset" with "every clip is
untouched by the model that scores it". No clip is ever used for early
stopping.

## Roles

`folds.csv` assigns each of the 28 source groups (30 clips) to one
`eval_fold`. It is produced by `ml/scripts/build_repcount_gate_rotation_v1.py`:
within each visible target, groups are sorted by
`SHA-256("repcount_gate_rotation_v1|" + source_group_id)` and dealt round-robin
across folds with one counter shared across classes. The rule was fixed
before any retrained model existed, and it does not look at predictions.

| Fold | Clips | sit_up | squat | lateral_raise | unknown | V6-F false-unknown | V6-F false-accept | V6-F wrong class |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 10 | 2 | 3 | 1 | 4 | 1 | 2 | 3 |
| 1 | 9 | 2 | 3 | 0 | 4 | 3 | 4 | 1 |
| 2 | 11 | 3 | 4 | 0 | 4 | 4 | 1 | 0 |
| All | 30 | 7 | 10 | 1 | 12 | 8 | 7 | 4 |

Both duplicate groups stay intact: `outdoor_crunch_shared_01`
(`stu8_49`, `stu9_56`) and `orange_rig_squat_shared_01` (`stu1_69`, `stu6_59`).
`stuN` is a source code, not a person; no split is called person-disjoint.

For fold `k`, the gate trains on the existing V6-F gate training pool plus
the RepCount clips in the other two folds. Fold `k` clips are scored only by
that fold's gates.

## What changes (one block only)

- **Changes:** the joint, bone, and velocity binary gate TCNs are retrained,
  following Notebook 31's `train_gate` recipe exactly (AdamW 1e-3, weight
  decay 1e-4, 40 max epochs, patience 8, existing V6-A validation split for
  early stopping, the same train-only augmentation and square-root-tempered
  source-group sampler).
- **Added data:** RepCount training-fold clips at 15 FPS, 64-frame windows,
  32-frame stride (the Notebook 37 pose archive, SHA-256
  `fddd4e63f1162c1b48d1d81165c6e204127226824e5af500f452161f8a7219ef`). Gate
  label: `sit_up`, `squat`, `lateral_raise` -> supported; `unknown` ->
  unsupported. Each RepCount source group enters the sampler as its own
  source group; no extra weight.
- **Frozen:** V6-E temporal exercise classifier, mean-probability stream
  fusion, threshold `0.65`, architecture, features, and every hyperparameter.
- **Never read:** the locked 36-region creator benchmark.

## Arms

| Arm | Gate training data | Runs |
| --- | --- | --- |
| Control | Existing V6-F pool only | Notebook 31's archived gates, seeds 42, 137, 2026 |
| Treatment | Existing pool + RepCount clips outside the scored fold | 3 folds x 3 seeds, same training seeds as Notebook 31 |

The control separates the data effect from retraining noise. Control gates
score all 30 clips (none were trained on RepCount). Runtime: Colab T4.

Implementation note (2026-10-24, before any run): the control reuses Notebook
31's checksummed gate checkpoints instead of retraining them. They are
exactly this arm: same pool, recipe, and seeds, with no RepCount data. Notebook
39 first checks that they reproduce Notebook 31's internal-test Macro F1
(within 0.3 pp), and that frozen V6-F reproduces Notebook 37's 30 clip
predictions. If either check fails, the notebook stops.

## Reported errors (kept separate)

Clip-level aggregation is the Notebook 37 rule: mean window gate probability
against 0.65, mean window class probability for the exercise.

1. **Gate false-unknown:** supported clip whose gate falls below 0.65.
2. **Gate false-accept:** `unknown` clip whose gate is at or above 0.65.
3. **Oracle classifier:** on the 18 supported clips, the frozen classifier's
   label with the gate ignored. It cannot change between arms; it is reported
   so wrong-class errors (`stu5_69`, `stu6_50`, `stu7_62`, `stu9_12`) are not
   blamed on the gate.
4. **End-to-end:** final label against the visible target.

Also reported: per-class counts, per-fold and per-seed tables, every
clip's gate probability, and the reused internal 1,971-window test for each
model as a regression guard only.

## Baseline (frozen V6-F, already measured)

Supported false-unknown 8/18; unknown rejection 5/12; sit-up 0/7; squat 6/10;
end-to-end 11/30.

## Predeclared stopping rule

Notebook 39 runs once. A rerun is allowed only for a crash or a code bug,
never because of a result, and any rerun is logged.

The data effect counts as **supported** only if all three hold, using the
median across the three seeds of out-of-fold counts:

1. Supported false-unknown is at most 5/18 (three or more fewer than V6-F's
   8/18) and lower than the control median.
2. Unknown rejection is at least the control median and at least 5/12.
3. Mean internal-test end-to-end Macro F1 of the treatment models is no more
   than 1.0 percentage point below the control mean.

Otherwise the result is archived as a negative or inconclusive finding. In
either case, no epoch, weight, threshold, fold, or sampler change follows from
these numbers, and the internal test is not used to choose anything.

## What this cannot prove

- The run is **non-promotable**: identities are unverified, support is tiny
  (one count is about 5.6 points of supported recall), and the source license
  is `other`.
- It cannot fix the four wrong-class errors; only the gate changes.
- Success means "more source-diverse data is worth collecting", not that
  V6-F is fixed. It says nothing about continuous segmentation, repetition
  counting, or the locked benchmark.
- RepCount scenes may differ from home or gym video; folds come from one
  dataset, so this is in-source transfer across groups.
