# Source balance intervention — candidate stage

The V6-C training split has four supported classes represented by only one
source dataset: dumbbell row and sit-up (MM-Fit), lat pulldown and pull-up
(WorkoutFitness-video). The earlier long-video retrain added one YouTube creator
for dumbbell row and lat pulldown, but degraded end-to-end F1; it did not
resolve multi-creator support. Window counts must not be confused with creator
counts.

`candidates.csv` is a search-time intake list, not reviewed evidence or training
data. Each row is a different creator absent from the existing training and
six-creator external-test inventories. Its `training_allowed` field is false.
Descriptions and titles only suggest where to look; they cannot establish a
motion label. All eight candidate videos need source access, license/use review,
full-person visual and pose-quality checks, independent interval annotation,
and a strict audit before any row can be promoted.

If YouTube access fails, the official [UCF101](https://www.crcv.ucf.edu/research/data-sets/ucf101/)
release includes a Pull Ups category, and the official
[HMDB51](https://serre.lab.brown.edu/hmdb51.html) release includes pull up and
sit up categories. Those are alternative *candidates*, not interchangeable
canonical labels: inspect source licensing, actor/group identity, clip length,
pose quality, and the project's motion definition before importing anything.

Run `python3 ml/scripts/audit_source_balance.py` from the repo root to inspect
class-by-source and group support and to check candidate video/creator IDs
against the reserved inventories. This audit does not promote candidates.

CPU `Run all` notebook `ml/notebooks/29d_colab_screen_source_balance_candidates.ipynb`
fetches this pinned manifest automatically, attempts only 360p video, records
unavailable sources without aborting the batch, and returns contact sheets and
metadata in one ZIP. It excludes raw video and performs no landmark extraction
or training. It follows the 29C review notebook as a separate data-intake
screen; reserved 30–33 model experiments keep their numbering.

After the 29E dense RGB output, `dense_visual_first_pass.csv` records a human
contact-sheet triage. Its times are approximate locators, not motion labels or
annotation boundaries. Every row is still draft, requires second review, and
has `training_allowed=false`. CPU `Run all` notebook
`ml/notebooks/29f_colab_audit_source_balance_pose_candidates.ipynb` fetches
that exact CSV from pinned GitHub commit `5315822130c3bbd0933f82508b14a1f75fc683ea`,
reuses the 360p Colab video cache when present, and extracts 15 FPS pose only
for the 17 candidate windows across five sources. Its pose ZIP is evidence for
quality and actor review, not a training set. It records source failures and
does not export raw video or require manual uploads.

The successful 29F rerun is archived at
`ml/artifacts/source_balance_v1/calorie_source_balance_v1_pose_audit.zip`.
All 17 candidate windows have pose evidence, but the labels and motion
boundaries remain draft and excluded from training. In particular, the
Goku pull-up candidates need careful exclusion of hanging knee raises,
camera cuts, and actor switches. Do not equate `pose_ready` with a reviewed
canonical label.

`pose_visual_triage.csv` records a provisional visual pass over representative
29F one-frame-per-second pose contact-sheet pages, combined with the earlier
2-FPS source triage. It is a review queue, not an
annotation timeline: only two Rowan row windows and one Nick sit-up window
are prioritized for exact motion/boundary inspection; several nominal
pull-up windows visibly include hanging knee raises. The Ryan lat-pulldown
windows are substantially cropped. The current batch therefore does not yet
provide clean new-creator coverage for all four source-confounded classes.
Every row remains draft with second review required and training disallowed.

The first exact-window pass is in `annotations/first_pass/` with its provenance
and per-window pose counts in `annotations/README.md`. It narrows three
candidate windows to proposed row/sit-up motion intervals and separates
visible setup/end transitions. The annotation audit passes structurally, but
an independent second motion review and group split decision are still needed
before any training clip is exported. This pass covers two original videos,
not three independent creators.

Acquisition target: at least two independently filmed new creators for each
of the four classes, with several clear complete repetitions per creator,
different camera angles or settings, and an unknown/rest timeline around the
action. This is a *collection target*, not a quality guarantee. Keep all
videos from one person wholly in one split. Keep the six locked benchmark
creators and all historical held-out creators out of training. Once reviewed,
retrain the identical V6-C recipe with only accepted groups added, compare
creator-level and per-class metrics against the frozen checkpoint, and reject
the candidate if unknown rejection or existing movements regress. The same
internal test has already informed many decisions; use fresh creator-disjoint
development data for model selection and leave the locked benchmark for one
frozen final evaluation.
