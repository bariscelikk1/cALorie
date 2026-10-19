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
No V6-C, V6-F, or Notebook 34 score may be produced until the lock gates below
pass.

## Phase 1 — reproducible review queue

Run `ml/notebooks/29c_colab_creator_label_review_queue.ipynb` once on CPU. It
must return `calorie_creator_label_review_queue.zip` with 41 draft rows and an
`independent_review_template.csv`. Archive the returned ZIP unchanged and
verify its checksum manifest. This phase performs no video download, pose
extraction, training, model scoring, or label lock.

## Phase 2 — independent visible-motion review

Review every queued region against the archived dense RGB or supplemental pose
evidence. Do not use titles, chapters, transcripts, or model predictions to
decide a label.

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
