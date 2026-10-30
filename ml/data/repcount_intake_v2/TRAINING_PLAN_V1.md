# RepCount-A training v1 — plan (approved 2026-10-27)

Status: approved by the user on 2026-10-27. Roles: `training_v1_roles.csv`;
stage A runs as Notebook 42.

## Question

Does adding 718 adjudicated, source-diverse RepCount-A clips, while
retraining **both** the exercise classifier and the open-set gate, fix the
failures seen on unseen footage (sit-ups 0/7, squats confused, unknowns let
through), without breaking the 8 classes RepCount does not cover?

Notebook 39 showed gate-only retraining cannot fix sit-ups: the frozen
classifier calls an accepted sit-up `bench_press`.

## 1. Split (by role group, fixed hash rule)

Input: `intake_v2_labels_v1.csv` usable rows (718) plus the 30 v1 clips.
Groups come from `full_role_groups_v1.csv`. A group is never split.

1. **Sealed test (about 20% per class):** walk groups in hash order (salt
   `repcount_intake_v2_roles`) and take a group only if all of these hold:
   it is sealed-test eligible (no borderline link to another group); it
   contains no pilot or v1 clip; every clip in it is `reviewed` (no
   `auto_verified`); and it does not push any class past its 20% target.
2. **Dev (about 15% per class):** the same walk over the remaining groups.
3. **Train:** everything else, including the tiny classes (lateral raise 8,
   deadlift 3, shoulder press 2). The 30 v1 clips follow their group's role
   (train or dev; never sealed test).

Preview of that rule:

| Label | Train | Dev | Sealed test |
| --- | ---: | ---: | ---: |
| unknown | 149 | 34 | 46 |
| squat | 66 | 15 | 18 |
| jumping_jack | 58 | 14 | 18 |
| bench_press | 53 | 12 | 16 |
| pull_up | 52 | 12 | 16 |
| sit_up | 44 | 10 | 14 |
| push_up | 37 | 9 | 12 |
| others (13 clips) | 13 | 0 | 0 |
| **Clips / groups** | 472 / 381 | 106 / 79 | 140 / 111 |

Plus the 30 v1 clips in train. The role file is written and committed
before any model is trained.

## 2. What changes

- **Training data:** the existing V6-A training pool plus RepCount train
  clips. They use the same 15-FPS pose, the same 64-frame / 32-stride windows,
  and the same train-only phase-resampled cycles for supported clips as the
  existing pool. That adds about 6,000 windows to about 10,000.
- **Retrained:** the 14-class exercise classifier (Notebook 26 recipe) and the
  joint, bone, and velocity gates (Notebook 31 recipe).
- **Unchanged:** architecture, features, augmentation, the class-balanced
  sampler with square-root group mass, mean-probability fusion, threshold
  0.65, and early stopping on the existing V6-A validation split only.
  RepCount is never used for early stopping.
- Each RepCount role group enters the sampler as its own source group with no
  extra weight. Because there are many small groups, RepCount will carry a
  large share of the covered classes (estimate: most of the sit-up mass). The
  sampler audit reports that share.

## 3. Arms

| Arm | Models | Seeds |
| --- | --- | --- |
| Control | Frozen V6-F: V6-E classifier plus Notebook 31's archived gates | 42, 137, 2026 (gates) |
| Treatment | Classifier plus 3 gates retrained with RepCount train | 42, 137, 2026 |

Runtime: 12 trainings on the Mac GPU (MPS), roughly overnight. The notebook
first checks that the control reproduces Notebook 31 and Notebook 37, as
Notebook 39 did.

## 4. Two-stage evaluation (recommended)

- **Stage A — decide on dev (106 clips).** All criteria in section 5 are
  computed on dev. The sealed test is not loaded.
- **Stage B — sealed test, once.** Only if stage A passes, the same frozen
  treatment models are scored once on the sealed test, using the same
  criteria. A failure is reported as a failure.

Why two stages: if the first attempt fails on dev, the sealed test is still
unseen and can judge a later, improved attempt honestly.

## 5. Predeclared pass rule

Clip-level scoring uses the Notebook 37 rule. Seed medians for the treatment.
All must hold:

1. **Big gain:** clip-level Macro F1 over the 7 test labels is at least 10
   percentage points above control, and the 95% role-group bootstrap interval
   of the difference stays above zero.
2. **The known failures are fixed:** sit-up recall is at least 50% and squat
   recall is at least 60%.
3. **No new leak:** unknown rejection is no more than 5 points below control.
4. **No damage elsewhere (internal 1,971-window test):** end-to-end Macro F1
   is no more than 2 points below control, and mean recall over the 8
   uncovered classes (bicep curl, deadlift, dumbbell row, lat pulldown,
   lateral raise, lunge, shoulder press, tricep extension) is no more than 5
   points below control.

Errors are reported in separate groups: gate false-unknown, gate false-accept,
wrong supported class, and end-to-end, plus per-class tables and per-group
breakdowns.

## 6. Limits

- Non-promotable: 166 training rows are `auto_verified`, the license is
  `other`, and all data comes from one dataset (RepCount-A).
- It cannot help the 8 uncovered classes; criterion 4 only checks they are
  not hurt.
- The locked 36-region creator benchmark is not read. If stages A and B
  pass, a one-time locked-benchmark evaluation would be proposed separately
  and needs the user's approval.
- One run per stage. A rerun is allowed only for a crash or a code bug.

## Order of work after approval

1. Write and commit the role file, with its audit (no split groups, pilot and
   v1 outside the sealed test, per-class minimums).
2. Build Notebook 42, dry-run it on the Mac, and commit.
3. Run stage A on the Mac GPU; archive the result and analyze it.
4. Stage B only if stage A passes.
