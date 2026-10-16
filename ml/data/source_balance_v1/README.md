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
