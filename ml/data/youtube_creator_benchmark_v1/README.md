# YouTube creator benchmark v1

This batch is a reserved external evaluation candidate set for the 14 supported
exercise classes. It is deliberately separate from every training,
augmentation, calibration, and threshold-selection source.

The first Notebook 28 run extracted four sources. Full-timeline visual review
rejected Buddy Fitness because the source is an exercise illustration/slide
deck rather than filmed human motion. The other three sources passed the
source-level visual check and provide about 139 minutes of usable real-person
evidence before interval selection.

Three replacement sources were selected after checking official chapters and
downloading their full-video YouTube storyboards. They restore projected
coverage of all 14 classes across six usable new creators. Coverage in
`projected_coverage_matrix.csv` is a search-time locator, not ground truth.
Titles, descriptions, chapters, transcripts, and search snippets may locate a
motion, but the label is accepted only after visible-motion review.

## Sources and intended contribution

| Creator | Video | Approx. duration | Main candidate classes |
| --- | --- | ---: | --- |
| BullyJuice | `ojs-UW8ULhs` | 60 min | jumping jack, squat, push-up |
| TIFF x DAN | `fJQmoPKvjTg` | 30 min | shoulder press, dumbbell row, triceps extension, biceps curl, lateral raise |
| Buddy Fitness | `PY6DrbX4W4o` | 8 min | **rejected:** drawings/slides, not filmed human exercise |
| STRIQfit | `Kw89u6WtPC8` | 41 min | pull-up plus hard unknown calisthenics motions |
| Michelle Briehler | `phFvFuLUFEw` | 38 min | bench press, RDL/deadlift, lat pulldown, lunge, lateral raise |
| Criticalbench | `lKHGBuanBsY` | 34 min | deadlift, bench press, row, shoulder press, curl, triceps extension, squat, lunge |
| TRAIN WITH GAINSBYBRAINS | `7-mVPCVJMtI` | 30 min | sit-up plus hard unknown abdominal motions |

All retained creators and video IDs were checked against
`excluded_source_inventory.csv`. None occurs in the existing YouTube
training/evaluation source inventory. The inventory is a durable guardrail and
must be checked again against returned metadata before any benchmark is
finalized.

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

Notebook 28 downloads temporary 360p sources, records source metadata, creates
compact full-timeline visual evidence, and extracts continuous 15 FPS pose
landmarks. Its output remains unlabeled evaluation evidence. Codex then reviews
that evidence locally and prepares motion-based timelines before frozen-model
evaluation. No model is trained in Notebook 28.

Notebook 28B performs the same evidence-only extraction for the three gap-fill
sources. It does not rerun the already valid BullyJuice, TIFF x DAN, or STRIQfit
videos and never includes the rejected Buddy Fitness source.

Notebook 28B returned successfully. ZIP integrity, all 64 internal checksums,
and all three landmark arrays passed. The 52 gap-fill contact sheets establish
that the sources show real people and help locate candidate motions. They do
not establish exact action boundaries. `candidate_intervals_v1.csv` has 37
draft locators across 14 proposed classes, spanning 1,664 seconds. Its
99.88% minimum pose detection is a diagnostic on those *candidate windows*,
not evidence that every frame belongs to the proposed action. Dense pose
review found that the Criticalbench deadlift candidate includes substantial
standing/talking. All 37 rows require dense RGB motion review and an
independent second review before any benchmark score is valid. No model
prediction was inspected while proposing these labels.

The benchmark is not complete merely because every class has projected
coverage. Do not score models on these draft rows. The acceptance audit must
report visible-motion support per class, creator, and source, and must keep
weak or missing cells explicit.

`ml/notebooks/29_colab_dense_creator_rgb_review.ipynb` is the next CPU
`Run all` step. It fetches pinned draft locators, downloads temporary 360p
videos with Notebook 28B's yt-dlp fallbacks, and packages 2 FPS RGB contact
sheets with five seconds of context around each candidate. Its ZIP is evidence
for motion-based relabeling and second review, not a benchmark or training set.

Notebook 29 returned one ZIP on 2026-10-17. Its first-pass audit lives in
`ml/artifacts/youtube_creator_benchmark_v1/dense_review_evidence/`. Five
proposed regions contain no supported target action, and the two proposed
`lateral_raise` regions show a compound upright-row-to-90-degree-raise
movement. Two `bench_press` twist-press regions require variant adjudication.
The current draft therefore has plausible core movement for only 12 of 14
classes without resolving the bench-press variant, or 13 if that variant is
accepted. These are not final scores or accepted benchmark labels.

The accepted Michelle Briehler source also shows unselected standard dumbbell
bench press and seated lateral raise work in its full-timeline storyboards.
`supplemental_candidates_v1.csv` records four new **draft** locators for those
motions. The archived 15-FPS landmarks were reused to produce 2-FPS pose
sheets in `ml/artifacts/youtube_creator_benchmark_v1/supplemental_pose_review/`;
Notebook 29B RGB extraction is optional when pose plus the existing 10-second
RGB storyboard leaves a real visual ambiguity. The four draft rows do not
restore 14-class coverage until their motion and boundaries are independently
reviewed. CPU Notebook 29C assembles all 41 draft regions into a review queue
and audit bundle without video downloads or model scoring.

