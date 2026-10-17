# cALorie — pose-based exercise recognition research

cALorie is currently a local-first machine-learning project for recognizing
exercise sequences from video. The active pipeline is:

```text
video -> MediaPipe pose landmarks -> supported/unknown gate
      -> 14-class exercise classifier -> stable timeline segments
      -> repetition counting -> MET-based calorie estimate -> local Python app
```

The project does **not** claim medical, wearable-grade, or final real-world
accuracy. MET values are population averages, and the current model scores are
research/development evidence rather than a final-system guarantee.

## Source of truth

- Active branch: [`feat/tcn-rebuild`](https://github.com/bariscelikk1/cALorie/tree/feat/tcn-rebuild)
- Current handoff: [`PROJECT_HANDOFF.md`](PROJECT_HANDOFF.md)
- ML guide and experiment history: [`ml/README.md`](ml/README.md)
- Fixed experiment contract: [`ml/EXPERIMENT_BACKBONE.md`](ml/EXPERIMENT_BACKBONE.md)
- Current roadmap: [`ml/POST_V6C_ROADMAP.md`](ml/POST_V6C_ROADMAP.md)
- Annotation rules: [`ml/data/ANNOTATION_GUIDE.md`](ml/data/ANNOTATION_GUIDE.md)

`main` is not the current project state. The historical `web/`, `worker/`,
`supabase/`, and deployment files are retained only as archive material while
the ML rebuild continues. They are not the active application, architecture,
or development target. There is currently no website workflow in scope.

## Active target

The model recognizes 14 dynamic exercises plus `unknown`:

- squat
- push-up
- jumping jack
- pull-up
- lunge
- sit-up
- shoulder press
- dumbbell row
- tricep extension
- bicep curl
- lateral raise
- bench press
- deadlift
- lat pulldown

Plank was retired from the active target after v5 and maps to `unknown` in
post-v5 work. Historical experiments and reports remain unchanged.

## Current model state

| Candidate | Role | Internal end-to-end Macro F1 | Internal accuracy | Decision |
| --- | --- | ---: | ---: | --- |
| V6-C | frozen reference | 79.33% | 82.90% | retain as baseline |
| V6-F | strongest aggregate candidate | 81.72% | 84.17% | do not promote yet |

These figures use the same 1,971-window internal development test. That test
has informed several experiment decisions, so the numbers must not be reported
as an untouched final evaluation. Creator-level regressions and strong domain
shift remain unresolved. The earlier three-creator diagnostic produced roughly
30% present-class Macro F1, showing that architecture changes alone did not
solve generalization.

## Current checkpoint

The active work is the Notebook 29 source-balance sequence. CPU notebooks
29D-29F screened new creators, produced dense visual evidence, and extracted
pose for candidate dumbbell-row, sit-up, lat-pulldown, and pull-up regions.
Only three stronger clips from two creator/video groups currently have exact
first-pass boundaries. They remain quarantined because no independent second
visual review has approved them.

[`ml/notebooks/29g_colab_exploratory_source_balance_retrain.ipynb`](ml/notebooks/29g_colab_exploratory_source_balance_retrain.ipynb)
is the next executable diagnostic:

- Runtime: **Colab T4 GPU**
- Action: **Runtime -> Run all**
- Model: exact V6-C recipe; no new architecture
- Only change: add the three quarantined source-balance clips to training
- Expected output: `calorie_v6c_source_balance_draft_retrain_report.zip`
- Promotion: explicitly forbidden; the result is diagnostic only

The first 29G run stopped before training because one Rowan clip contained two
missing pose frames. The current notebook repairs sparse missing poses by
per-joint temporal interpolation and exports `pose_imputation_audit.csv`.

## Evaluation rules

- Split by original person, creator, and source video before windowing.
- Never tune thresholds or models on locked tests.
- Never promote draft, rejected, or unresolved labels.
- Report Macro F1, per-class recall, unknown rejection, and creator-level
  results; accuracy alone is insufficient.
- Keep checkpoints, predictions, split assignments, hashes, and audit outputs.
- Treat overlapping windows as correlated samples, not independent people.
- Preserve failed experiments and document why they were rejected.

## Important limitations

- Several internal test classes have very little support.
- Exercise class and source dataset are partly confounded.
- External creator generalization is substantially weaker than internal
  development performance.
- The six-creator external benchmark is not final until its motion labels and
  boundaries receive independent review and pass the strict timeline audit.
- Repetition counting, long-video segmentation, calorie estimation, and the
  local Python application remain downstream work after recognition is stable.
- Downloaded creator videos require careful provenance and reuse review; raw
  videos are kept out of Git.

## Working in this repository

Read [`AGENTS.md`](AGENTS.md) and the applicable subdirectory instructions
before changing files. Colab notebooks must run end to end from a fresh runtime,
download checksum-pinned inputs automatically, and export one clearly named
ZIP. After a returned ZIP is verified, archive the evidence, update the
handoff, and checkpoint the work on `feat/tcn-rebuild`.
