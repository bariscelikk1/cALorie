# YouTube creator benchmark v1

This batch is a locked, external evaluation candidate set for the 14 supported
exercise classes. It is deliberately separate from every training,
augmentation, calibration, and threshold-selection source.

The first four sources are projected to cover all 14 classes across four new
creators and roughly 140 minutes of public video. Coverage in
`projected_coverage_matrix.csv` is a search-time locator, not ground truth.
Titles, descriptions, chapters, transcripts, and search snippets may locate a
motion, but the label is accepted only after visible-motion review.

## Sources and intended contribution

| Creator | Video | Approx. duration | Main candidate classes |
| --- | --- | ---: | --- |
| BullyJuice | `ojs-UW8ULhs` | 60 min | jumping jack, squat, push-up |
| TIFF x DAN | `fJQmoPKvjTg` | 30 min | shoulder press, dumbbell row, triceps extension, biceps curl, lateral raise |
| Buddy Fitness | `PY6DrbX4W4o` | 9 min | bench press, deadlift, lat pulldown, dumbbell row, arm/shoulder work, squat, lunge, sit-up |
| STRIQfit | `Kw89u6WtPC8` | 41 min | pull-up plus hard unknown calisthenics motions |

These creators and video IDs were checked against
`excluded_source_inventory.csv`. None of the four videos or creators occurs in
the existing YouTube training/evaluation source inventory. The inventory is a
durable guardrail and must be checked again against returned metadata before
any benchmark is finalized.

## Locked role

- `benchmark_role=locked_external_test`
- `training_allowed=false`
- `calibration_allowed=false`
- `threshold_selection_allowed=false`
- keep every source video wholly in the external-test partition;
- do not inspect model predictions while deciding labels or boundaries;
- do not redistribute raw video in the report archive;
- preserve unsupported, compound, setup, rest, transition, and occluded motion
  as `unknown`.

Notebook 28 downloads temporary 720p sources, records source metadata, creates
compact full-timeline visual evidence, and extracts continuous 15 FPS pose
landmarks. Its output remains unlabeled evaluation evidence. Codex then reviews
that evidence locally and prepares motion-based timelines before frozen-model
evaluation. No model is trained in Notebook 28.

The benchmark is not complete merely because every class has projected
coverage. The acceptance audit must report visible-motion support per class,
creator, and source, and must keep weak or missing cells explicit.

