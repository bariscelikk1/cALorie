# cALorie — Claude master handoff

Last updated: 2026-10-24 (Europe/Istanbul)

This is the fastest safe entry point for continuing cALorie with Claude. The
linked repository evidence remains the source of truth. Read the documents in
the required order before changing data, labels, models, or notebooks.

## Repository and exact working state

- Repository: https://github.com/bariscelikk1/cALorie
- Active branch: https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild
- Open draft PR #2: https://github.com/bariscelikk1/cALorie/pull/2
- PR base/head: `main` <- `feat/tcn-rebuild`
- Last scientific checkpoint before this handoff:
  https://github.com/bariscelikk1/cALorie/commit/16109002bb4b2e3c8f002e964cecc495799fab13

`feat/tcn-rebuild` is the current project. `main` is not current. The old
website, worker, Supabase, and deployment code is historical archive material.
There is no active website workflow. Do not restart or redesign it unless the
user explicitly changes scope.

```bash
git clone --branch feat/tcn-rebuild --single-branch \
  https://github.com/bariscelikk1/cALorie.git
cd cALorie
git status --short --branch
```

## Required reading order

1. [Collaboration rules](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/AGENTS.md)
2. [Chronological handoff and experiment log](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/PROJECT_HANDOFF.md)
3. [Root project overview](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/README.md)
4. [ML-specific rules](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/AGENTS.md)
5. [ML overview and notebook history](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/README.md)
6. [Fixed experiment contract](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/EXPERIMENT_BACKBONE.md)
7. [Post-V6-C roadmap](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/POST_V6C_ROADMAP.md)
8. [Mandatory annotation contract](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/ANNOTATION_GUIDE.md)

When documents conflict, prefer immutable artifacts and row-level CSVs, then
the latest dated section of `PROJECT_HANDOFF.md`, then this current summary,
then older roadmap/proposal text. Never turn a provisional figure into a final
result.

## Product goal and current scope

```text
video -> MediaPipe pose landmarks -> supported/unknown gate
      -> 14-class exercise classifier -> stable timeline segments
      -> repetition counting -> MET-based calorie estimate -> local Python app
```

Pose extraction, open-set gating, exercise classification, controlled
experiments, and region-level evaluation are developed. Continuous full-video
segmentation, repetition counting, calorie estimation, and the local app are
not production-complete.

Supported labels are `bench_press`, `bicep_curl`, `deadlift`, `dumbbell_row`,
`jumping_jack`, `lat_pulldown`, `lateral_raise`, `lunge`, `pull_up`, `push_up`,
`shoulder_press`, `sit_up`, `squat`, and `tricep_extension`, plus `unknown`.
Plank was intentionally retired to `unknown`.

## Current recognition models

### V6-C frozen reference

V6-C is a two-stage TCN using 64-frame windows and 32-frame training stride.
Each frame has 100 pose-derived features: 34 normalized x/y coordinates, 34
x/y velocities, 24 bone-vector values, and 8 joint angles. It uses class
balancing, square-root-tempered source-group mass, and train-only
geometric/temporal augmentation.

On the reused 1,971-window internal development test it records 79.33%
end-to-end Macro F1 and 82.90% accuracy. This is development evidence, not
untouched final performance.

- [V6-C artifact index](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild/ml/artifacts/v6c)
- [V6-C metrics](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/artifacts/v6c/model/metrics.json)

### V6-F preferred candidate

V6-F freezes the V6-E complete-action temporal classifier and uses separate
joint, bone, and velocity TCN streams for the open-set gate. Gate probabilities
use mean-probability fusion. The active fixed threshold is `0.65`; Notebook
32's validation-selected `0.57` was explicitly rejected.

On the same reused internal test, original V6-F records 81.72% end-to-end
Macro F1 and 84.17% accuracy. The three-seed ensemble diagnostic recorded
82.09% Macro F1 and 85.34% accuracy with about 0.23 percentage-point seed
standard deviation. These are not production claims.

- [V6-F artifact index](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild/ml/artifacts/v6f_multistream_gate)
- [V6-F metrics](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/artifacts/v6f_multistream_gate/model/metrics.json)
- [V6-F seed-stability evidence](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild/ml/artifacts/v6f_seed_stability)

Correct decision: **V6-F is preferred over V6-C for recognition, but it is
not production-ready.**

## Locked external creator benchmark

The six-creator region benchmark is locked: 36 reviewed non-overlapping
regions, 32 supported regions, four compound `unknown` regions, all 15 output
labels, and 616 deterministic windows. It evaluates region classification,
not continuous full-video segmentation.

- [Locked benchmark CSV](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/youtube_creator_benchmark_v1/locked_region_benchmark_v1.csv)
- [Lock audit](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/youtube_creator_benchmark_v1/locked_region_benchmark_audit_v1.json)
- [Final analysis](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/artifacts/youtube_creator_benchmark_v1/locked_region_benchmark_v1/ANALYSIS.md)
- [Machine-readable metrics](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/artifacts/youtube_creator_benchmark_v1/locked_region_benchmark_v1/metrics.json)

| Metric | V6-C | V6-F | Delta |
| --- | ---: | ---: | ---: |
| Region accuracy | 52.78% | 69.44% | +16.67 pp |
| 15-label Macro F1 | 44.59% | 67.11% | +22.52 pp |
| Supported accuracy | 53.13% | 71.88% | +18.75 pp |
| Unknown recall | 50.00% | 50.00% | 0.00 pp |

Paired creator-bootstrap intervals for accuracy, Macro F1, and supported
accuracy remain above zero, so V6-F wins the frozen comparison. It nevertheless
has zero recall on lateral raise (0/2), sit-up (0/1), squat (0/3), and tricep
extension (0/2), recovers only two of four true unknown regions, and sends nine
supported regions to `unknown`.

Freeze these observations. Never train on the 36 rows or alter labels,
thresholds, fusion, or weights in response to their predictions.

## Latest arc: RepCount external development

Thirty RepCount-A clips were selected: ten published `front_raise`, ten
`situp`, and ten `squat`. The source is a public Hugging Face Lance mirror, not
YouTube.

- [Intake contract](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/README.md)
- [Candidate manifest](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/candidates.csv)
- [Pinned video mirror](https://huggingface.co/datasets/lmms-lab-eval/repcounta-lance/tree/ae2e0b0496124d900d4e54a8e92f7ec15a292afd)
- [Pinned metadata](https://huggingface.co/datasets/lmms-lab-eval/repcount/tree/d4c2ad3df38dfef3d1fca6f7b3fdfad6a38128e5)

The source is marked `license: other`. Never commit or redistribute raw
RepCount video. Derived pose, compact review evidence, and aggregate
diagnostics are the allowed evidence boundary used here.

### Critical identity correction

`stu1` through `stu10` are source codes, not verified people. The provisional
plan treated them as ten people and proposed `stu1`-`stu7` versus
`stu8`-`stu10` person-disjoint roles. Visual review invalidated this: the three
`stu10` clips show different people, while `stu8_49` and `stu9_56` share an
actor and scene. Never call that split person-disjoint.

Known source collisions that must stay together:

- `stu8_49` + `stu9_56`: `outdoor_crunch_shared_01`
- `stu1_69` + `stu6_59`: `orange_rig_squat_shared_01`

### Notebook 37

Notebook 37 fetched only the 30 pinned Lance blobs, extracted RGB sheets and
15-FPS MediaPipe pose, scored frozen V6-F at 0.65, deleted raw video, and
returned a checksummed ZIP. It performed no training, calibration, or locked
benchmark access.

- [Notebook 37 artifact](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild/ml/artifacts/repcount_external_development_v1)
- [Post-run visual audit](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/POSTRUN_VISUAL_AUDIT_V1.md)

### Notebook 38 and final labels

Notebook 38 fetched eight medium-confidence clips and returned dense 4-FPS
JPEG evidence plus silent 240p previews. All hashes passed. It contained no
raw videos, training, threshold selection, or locked-benchmark access.

- [Dense evidence artifact](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild/ml/artifacts/repcount_external_development_v1/visual_adjudication_v1)
- [Final row-level labels](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/final_visible_adjudication_v1.csv)

Final visible targets: 12 `unknown`, 10 `squat`, 7 `sit_up`, and 1
`lateral_raise`. The eight resolved second-review decisions are:

- `stu1_53`, `stu3_54`, `stu5_52`, `stu6_50`, `stu8_49`, `stu9_56` -> `sit_up`
- `stu2_67` -> `squat`
- `stu9_12` -> `lateral_raise`

Conventional crunches, anchored sit-ups, and incline-bench sit-ups map to
`sit_up` when torso flexion is dominant. V-ups/jackknives, reverse
crunches/leg raises, and GHD-style hyperextensions remain `unknown`.

Frozen V6-F against final labels:

| Diagnostic | Result |
| --- | ---: |
| Overall | 11/30 = 36.7% |
| Supported visible clips | 6/18 = 33.3% |
| Unknown rejection | 5/12 = 41.7% |
| Squat | 6/10 |
| Sit-up | 0/7 |
| Lateral raise | 0/1 |

The earlier 16/30 was provisional. It fell because dense review correctly
moved six apparent unknowns into supported `sit_up`; the model did not change.
This is a more honest source-shift diagnostic, not person-disjoint accuracy.
Every row remains `training_allowed=false`.

## Experiments and decisions not to forget

| Work | Outcome |
| --- | --- |
| G1 full ST-GCN | Rejected. |
| G2 BiGRU / Transformer / Adaptive GCN | Small BiGRU internal gain came mostly from seven lat-pulldown windows; no promotion. |
| Notebook 24, +464 windows | End-to-end Macro F1 fell from 79.33% to 77.39%; rejected. |
| Notebook 29G, +52 windows | Macro F1 fell to 78.23%; rejected. |
| Notebook 31, three seeds | Stable seeds, but held-out creator weakness remained. |
| Notebook 32, threshold 0.57 | Rejected; keep 0.65. |
| Notebook 33, equal-creator/group-CVaR | Collapsed to 73.53%; tiny groups received ~84% sampler mass; rejected. |
| Notebook 34, softer balance | Proposal exists; no verified returned result is archived. Do not assume success. |
| Notebook 35 | Provisional diagnostic superseded by Notebook 36. |
| Notebook 36 | One-time locked benchmark; V6-F won; result frozen. |
| Notebooks 37-38 | RepCount diagnosis and adjudication; no training yet. |
| Notebook 39 | Ran once on Mac GPU: data effect not supported (false-unknown 6/18 vs required 5/18); sit-ups 0/7 because the frozen classifier calls them bench press. |
| Notebook 40 | RepCount-A intake v2 pilot evidence (64 clips); ran locally on the Mac. |
| Notebooks 41 | Full RepCount-A intake (946 clips) ran locally; 718 usable labeled clips in `ml/data/repcount_intake_v2/intake_v2_labels_v1.csv`. |
| Notebook 42 | Training v1 stage A failed one guard: dev Macro F1 61%→86%, sit-ups 0%→80%, but internal Macro F1 −2.24 pp (limit −2.00). Sealed test unseen. |
| Notebook 43 | Training v2 (50% RepCount cap) stage A passed on dev (Macro F1 61%→85%, sit-ups 0%→90%, internal −1.61 pp). |
| Notebook 44 | v2 stage B on the sealed test FAILED one criterion: sit-ups 42.9% (needed 50%). Macro F1 57%→75%, squats 44%→72%, unknown rejection 80%→94%. Arc closed; v2 not promoted; sealed test spent. |
| Long-video test v1 | Locked 8-video 3.9 h full-session set; evaluation 1: V6-F 32.6% vs v2 32.3% smoothed Macro F1 (no difference); both reject >50% of real exercise time as unknown. |

The full history is in [PROJECT_HANDOFF.md](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/PROJECT_HANDOFF.md).
Failed experiments are evidence; do not delete or rewrite them as successes.

## Immediate next step

The RepCount experiment design is predeclared and approved:
[gate rotation v1 design](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/gate_rotation_v1/DESIGN.md)
and its [fold manifest](https://github.com/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/data/repcount_development_v1/gate_rotation_v1/folds.csv).
Notebook 39 implements it and passed a local CPU dry run; it has not run on
Colab yet. Run it on a T4 and archive the returned ZIP before anything else.

Minimum contract:

1. Do not touch the locked benchmark for training, calibration, threshold
   selection, relabeling, or repeated consultation.
2. Treat `stuN` as source codes, not people.
3. Predeclare source-group-disjoint roles and keep both duplicate groups intact.
4. Create a new versioned experiment manifest for any rows changing from
   `training_allowed=false`; never mutate the evidence CSV.
5. Score every RepCount clip only with gates that never trained on its
   source group (3-fold source-group rotation, chosen over a fixed holdout
   that held one false-unknown); never use RepCount for early stopping.
6. Keep threshold 0.65 fixed so the first run measures a data effect.
7. Separate gate, oracle-classifier, and end-to-end errors.
8. Keep the run non-promotable because identity is uncertain, support is tiny,
   and the source license is `other`.
9. Predeclare a stopping rule and do not reopen tuning on the reused
   1,971-window internal test.

Research question: can adjudicated source-diverse development data reduce
false-unknown errors on real sit-ups and squats without damaging unknown
rejection on a source-disjoint development holdout?

## Colab contract and direct links

The user wants direct Colab links. A notebook must run with `Runtime -> Run
all` from a fresh stated CPU/T4 runtime, download immutable GitHub inputs,
verify SHA-256, and automatically return one named ZIP. Normal execution must
not require uploads, file pickers, pasted fixes, widgets, or per-row clicks.

- [31 — seed stability](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/31_colab_v6f_seed_stability.ipynb)
- [32 — validation calibration](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/32_colab_v6f_validation_gate_calibration.ipynb)
- [33 — creator-robust gate](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/33_colab_v6f_creator_robust_gate.ipynb)
- [34 — soft creator balance; result unverified](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/34_colab_v6f_soft_creator_balance.ipynb)
- [35 — provisional creator diagnostic](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/35_colab_provisional_creator_diagnostic.ipynb)
- [36 — locked creator benchmark](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/36_colab_locked_creator_region_benchmark.ipynb)
- [37 — RepCount intake](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/37_colab_repcount_external_development_intake.ipynb)
- [38 — dense adjudication packet](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/feat/tcn-rebuild/ml/notebooks/38_colab_repcount_visual_adjudication_packet.ipynb)
- [39 — RepCount gate rotation; T4; awaiting run](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/94c7cb9d7252eb58b2ee889f589109fa42720370/ml/notebooks/39_colab_repcount_gate_rotation.ipynb)
  (commit-pinned: Colab can misread the `/` in the branch name, so use commit links)
- [40 — RepCount-A intake v2 pilot; CPU; awaiting run](https://colab.research.google.com/github/bariscelikk1/cALorie/blob/b1e3f527c61942cf774c266d3936ffe7c95db824/ml/notebooks/40_colab_repcount_intake_v2_pilot.ipynb)

Notebook 37 originally failed because its Lance build did not support `hf://`.
Notebook 38 originally failed because Pillow conflicted with Colab Python 3.13
(`17 given`, `16 accepted`). Both were repaired; Notebook 38 now uses OpenCV.
Do not reintroduce those failed paths.

## Non-negotiable data and evaluation rules

- Split by person, creator, source video, and known source group before
  creating overlapping windows.
- Keep every source video/group in exactly one role.
- Visible motion controls labels; titles and metadata are only locators.
- Unsupported, compound, ambiguous, rest, setup, and transition motion remains
  `unknown` rather than being forced into a supported class.
- Do not train on draft, rejected, unresolved, or disabled rows.
- Report Macro F1, per-class metrics, unknown precision/recall, source/creator
  breakdowns, and uncertainty over creators/videos—not just window accuracy.
- The 1,971-window internal test is reused development evidence.
- The locked 36-region benchmark is frozen.
- Region classification does not prove continuous segmentation.
- Pose quality, camera/cropping, and source-class confounding remain major
  bottlenecks; architecture changes alone have not solved them.

## Git and user workflow

- Preserve unrelated changes; never force-push or reset away user work.
- After each meaningful unit, update `PROJECT_HANDOFF.md`, commit intended
  files, and push `feat/tcn-rebuild`.
- Archive returned ZIPs unchanged with outer and internal checksums.
- Record what was and was not tested. A pushed notebook is not a completed
  experiment until its output is returned and verified.
- Never commit credentials, private raw data, or raw licensed videos.
- If push fails, keep the local commit and report it honestly.
- Work autonomously on safe scoped tasks; do not ask the user to repeat
  uploads or manual labeling already completed.
- Explain what each experiment changes, what success means, and what it cannot
  prove. Give direct Colab links after push.
- Minimize manual review. Do not hide regressions; grounded lower metrics are
  better than inflated provisional ones.
- The user wants progress on the model, not the historical website.

## Paste this as Claude's first task

> Continue cALorie from https://github.com/bariscelikk1/cALorie on branch
> `feat/tcn-rebuild`; `main` and the historical website are not active. Read
> `CLAUDE.md`, `AGENTS.md`, the latest `PROJECT_HANDOFF.md`, `ml/AGENTS.md`,
> `ml/EXPERIMENT_BACKBONE.md`, and `ml/data/ANNOTATION_GUIDE.md` before acting.
> The frozen creator benchmark says V6-F beats V6-C at 67.11% vs 44.59% region
> Macro F1 but is not production-ready. The latest RepCount adjudication
> finalized 30 clips and exposes V6-F at 11/30, including 0/7 sit-ups. Do not
> tune on the locked benchmark or reused 1,971-window internal test. First
> propose and audit a source-group-disjoint, non-promotable RepCount
> development experiment with threshold 0.65 fixed; do not create Notebook 39
> until its roles and stopping rule are explicit. After each meaningful unit,
> update the handoff, commit, and push. Give direct Colab links for notebooks.
