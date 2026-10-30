# YouTube long-workout candidate batch v2

This batch adds two previously unused YouTube videos from two previously unused
creators. Their combined duration is **3,719 seconds (61:59)**. The selection
intentionally complements the existing long-workout sources:

| Video | Duration | Candidate supported motion | Main value |
| --- | ---: | --- | --- |
| `zxqCV_eQHZY` — Legally Swole | 31:38 | squat, deadlift, push-up, triceps extension, biceps curl, lat pulldown, dumbbell row | rare weighted and machine movements |
| `Fk1wnNX4wQ8` — Daniel Nikolic | 30:21 | push-up, squat, lunge, sit-up, jumping jack | new person/background plus unsupported compound movement and transition negatives |

The source URLs and fetched metadata are in `candidates.csv`. On 2026-10-15,
both video IDs, channel IDs, and creator names were checked against the 14 rows
in `ml/data/youtube_mixed_workouts_v1/manifest.csv`; no earlier source or
creator was reused.

## Important status

This is a **candidate and first-pass annotation package**, not accepted
training data. The original channel descriptions and YouTube chapter
boundaries were used only to locate likely intervals. A later visual pass
expanded the 42 draft rows to 118 motion-oriented first-pass intervals, but
that pass cannot establish independently approved ground truth.

- `use_for_training=false` for every row;
- every first-pass label remains `use_for_training=false` and requires an
  independent second review;
- the raw-video license field remains `unspecified`; do not redistribute raw
  video and review intended use before acquisition;
- visually inspect the complete timeline, body visibility, person count,
  occlusion, camera cuts, and actual motion before changing a label;
- split assignment remains `candidate_unassigned` until person identity and
  the evaluation/training role are decided;
- unsupported machine exercises, planks, burpees, compound movements, rests,
  and transitions remain `unknown` unless a reviewer establishes one canonical
  supported motion for the full interval.

The original chapter-derived files live in `annotations/draft/`. The visual
first pass lives in `annotations/first_pass/` and covers the complete source
duration without overlap. A second reviewer must still check exercise, rest,
setup, transition, and boundary decisions.

`draft_annotation_audit.json` records the pre-review structural audit: 42 rows,
zero errors, and 42 expected warnings for the intentionally coarse five-second
chapter boundaries. The `metadata_prefill_only` reviewer value identifies the
automated draft source; it does not represent human review.

`first_pass_annotation_audit.json` records 118 rows and zero structural errors.
Its 118 coarse-boundary warnings are expected for this pass and are one reason
the labels cannot enter training yet.

## Review sequence

1. Confirm each source is still public and record the applicable usage/license
   decision. Download privately for project review; do not commit raw videos.
2. Use Notebook 22's continuous landmarks and pose previews to audit whether
   the first-pass intervals have usable pose coverage.
3. Keep ambiguous variants and compound movements as `unknown`; document why.
4. Produce an independent second review for all low-confidence rows and at
   least 10% of the remaining intervals.
5. Move accepted rows into a reviewed directory only after adjudication and
   update reviewer metadata truthfully.
6. Run the strict audit before landmark extraction:

   ```bash
   python3 ml/scripts/audit_timeline_annotations.py \
     ml/data/youtube_long_workouts_v2/annotations/reviewed \
     --strict \
     --report ml/data/youtube_long_workouts_v2/annotation_audit.json
   ```

No model should train on this batch until these steps pass.
