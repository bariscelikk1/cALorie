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

Notebook 29G is complete and rejected as a promotion candidate. It retained
the exact V6-C recipe and added only three quarantined clips (52 windows) from
two new creator/video groups. All hashes pass and the expected two missing pose
frames were repaired and audited.

The gate improved by 1.52 Macro-F1 points, but the exercise classifier lost
1.73 points and end-to-end Macro F1 fell from **79.33% to 78.23%**. The two
target classes also regressed: `dumbbell_row` F1 fell by 12.75 points and
`sit_up` F1 by 7.25 points. Frozen V6-C remains the reference; the 29G
checkpoint must not be deployed or promoted.

The verified report is archived under
[`ml/artifacts/v6c_source_balance_draft_retrain/`](ml/artifacts/v6c_source_balance_draft_retrain/).
The next work is independent motion/boundary review and broader creator data
for the weak/source-confounded classes. Notebook 30A screened all 12 initial
source-balance-v2 candidates, Notebook 30B completed the first dense motion and
replacement screen, and Notebook 30C completed all four follow-up targets. The
review now queues 18 row/sit-up/pull-up windows for pose audit. Both new
lat-pulldown replacements were rejected for full-body pose inconsistency, while
Alex Crockford and two Max Euceda row passages advanced. The first CPU Notebook
30D run was blocked by YouTube bot checks and produced zero pose-ready windows;
its unchanged failure report is archived. The repaired 30D completed without a
YouTube request: all 18 windows produced coarse 2-FPS pose and all 117 output
hashes pass. Seven windows have strong coarse coverage and eleven remain usable
with visibility cautions. The unchanged result and Codex triage are archived,
but these landmarks are not training data and do not replace source-backed
continuous 15-FPS extraction or independent review. Do not start another
architecture experiment or tune against the already-used 1,971-window test.
Notebook 30E remains available as a YouTube-free, user-controlled source ingest
path, but that data branch is paused. The active model step is T4 Notebook 31:
an exact three-seed V6-F stability audit. It freezes the data, split, temporal
classifier, mean-probability fusion, and threshold `0.65`; only gate seeds 42,
137, and 2026 change. No best test seed is selected and production promotion
remains disabled. Notebook 31 is now complete: the seeds are stable (81.64%
mean end-to-end Macro F1, 0.23-point standard deviation), but the research gate
fails because the held-out YouTube creator's present-class F1 remains 12.06
points below V6-C. The next bounded model step is validation-only ensemble gate
calibration in T4 Notebook 32. Its threshold grid and unknown-recall floor are
predeclared; the reused internal test cannot select the threshold. Notebook 32
selected `0.57`, but that threshold is rejected: accuracy fell 1.57 points,
unknown recall fell 8.42 points, and creator-domain gates still failed. The
`0.65` reference remains active. Notebook 33's equal-creator/group-CVaR
training is also rejected: end-to-end Macro F1 fell from 82.09% to 73.53%,
accuracy from 85.34% to 72.10%, and unknown recall from 92.04% to 80.55%.
Its sampler gave roughly 84% of total mass to hundreds of tiny WorkoutFitness
groups. T4 Notebook 34 is the active development-only correction: square-root
creator mass, a four-times-median per-window cap, 20% group-CVaR, the same
three seeds, and fixed threshold `0.65`. Because the reused internal-test
diagnostic motivated this recipe, Notebook 34 cannot establish production
generalization or authorize promotion. The tuning loop is now frozen: its
result may be archived, but it must not motivate another internal-test
iteration. The active milestone is to lock the six-creator external benchmark
under `ml/data/youtube_creator_benchmark_v1/BENCHMARK_LOCK_PLAN.md`, then score
the fixed V6-C and V6-F candidates once.

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
