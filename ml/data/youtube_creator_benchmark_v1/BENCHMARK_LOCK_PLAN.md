# Six-creator benchmark lock plan

Status: **not locked**. This file starts the evaluation-first arc after the
recognition-tuning loop was frozen on 2026-10-19.

## Current evidence

- Six unused real-person creator videos are reserved for external evaluation.
- Continuous 15 FPS landmarks and full-timeline visual evidence already exist.
- There are 37 original draft locators plus four supplemental Michelle
  Briehler locators: 41 regions total across all 14 proposed classes.
- The RGB first pass inspected only two overview tiles per dense contact-sheet
  page, not every 2 FPS frame.
- First-pass decisions are 26 trim candidates, five rejects, two relabel-to-
  unknown candidates, two unresolved variants, and two regions requiring a
  split. The four supplemental regions remain low-confidence drafts.
- Accepted clips: 0. Locked labels: 0. Model predictions inspected: no.

Projected or provisional class coverage is not accepted benchmark coverage.
No V6-C, V6-F, or Notebook 34 result may be called a final benchmark score
until the lock gates below pass. Notebook 35 is an explicitly provisional,
fail-closed diagnostic exception: it may compare frozen systems on conservative
first-pass regions, but it cannot tune, select, promote, or relabel anything.

Manual review is paused. The partial Reviewer A confirmation file is not a
lock artifact: only 27 of 41 rows were touched, all confidence values remained
the default `medium`, and three changed labels came from the old interface
opening the wrong evidence page. Those three changes are discarded.

## Phase 1 — reproducible review queue

Run `ml/notebooks/29c_colab_creator_label_review_queue.ipynb` once on CPU. It
must return `calorie_creator_label_review_queue.zip` with 41 draft rows and an
`independent_review_template.csv`. Archive the returned ZIP unchanged and
verify its checksum manifest. This phase performs no video download, pose
extraction, training, model scoring, or label lock.

## Phase 2 — independent visible-motion review

Use `ml/notebooks/29d_colab_creator_benchmark_review.ipynb` to review every
queued region against the archived dense RGB or supplemental pose evidence.
Its `confirmation` mode preserves the existing first-pass work as Reviewer A
evidence; it does not count as an independent blind review. A distinct reviewer
must use `blind` mode for the independent pass. Do not use titles, chapters,
transcripts, or model predictions to decide a label.

For each row record:

- stable `reviewer_id`;
- visible `reviewed_motion_label`, using `unknown` for unsupported, compound,
  ambiguous, rest, transition, or badly occluded motion;
- `reviewed_start_s` and `reviewed_end_s` around only the visible semantic
  state;
- `segment_type`, `confidence`, `decision`, and notes;
- `needs_second_review=true` for every uncertain label or boundary.

Reject rows with no useful visible action. Split broad regions when a single
interval would contain multiple semantic states. The two TIFF twist-press
regions and both broad Michelle RDL regions require explicit adjudication; do
not silently convert them into supported clips.

## Phase 3 — agreement and timeline audit

- Independently repeat at least 10% of intervals, including every low-
  confidence row and every new edge-case pattern.
- Resolve every disagreement explicitly.
- Convert accepted decisions into sorted, non-overlapping continuous timelines
  that preserve setup, rest, transitions, and unsupported motion as `unknown`.
- Run `audit_timeline_annotations.py` with the independent-review root, then
  run the final batch with `--strict`.
- Keep every source video wholly in the external-test partition.

## Lock gates

The benchmark becomes locked only when all of the following are true:

- all six source identities and hashes match the archived evidence;
- every evaluated interval has visible-motion support and final boundaries;
- no evaluated row is `draft`, `rejected`, or unresolved low-confidence;
- required second reviews and adjudications are complete;
- structural and strict timeline audits pass;
- accepted class-by-creator coverage is recomputed from final labels;
- training, augmentation, calibration, and threshold selection remain disabled;
- V6-C/V6-F predictions have never been used to edit labels or boundaries.

## First frozen evaluation

After the lock, evaluate original V6-C and Notebook 27/31 V6-F exactly once
with their already fixed checkpoints and thresholds. Report gate and exercise
classifier metrics separately, then combined Macro F1, per-class recall,
unknown precision/recall, per-creator results, and bootstrap confidence
intervals over creators or videos—not overlapping windows. The benchmark may
reject a candidate but must never tune one.

## Provisional diagnostic while manual review is paused

`ml/notebooks/35_colab_provisional_creator_diagnostic.ipynb` uses only the 26
first-pass `trim_candidate` cores and nine explicit unknown/reject/variant
regions. It excludes both `requires_split` rows and all four
`supplemental_pose_candidate` rows. It reports both region-level and retained
window-level predictions, but creator-bootstrap uncertainty is computed from
region results with creators as sampling units. Every exported row remains
`provisional_first_pass_not_locked`; training, calibration, threshold
selection, and promotion flags stay false.

The verified provisional run contains 561 windows aggregated to the 35 fixed
regions. V6-C reaches 60.00% region accuracy, 46.36% present-label Macro F1,
53.85% supported accuracy, and 77.78% unknown recall. V6-F reaches 68.57%,
67.25%, 73.08%, and 55.56% respectively. This is evidence of V6-F's stronger
supported-motion recognition and weaker unknown rejection, not a benchmark
lock or promotion decision.
