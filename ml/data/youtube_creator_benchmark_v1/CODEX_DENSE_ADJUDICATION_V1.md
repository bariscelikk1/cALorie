# Codex dense adjudication v1

`codex_dense_adjudication_v1.csv` is a complete visual pass over all 41
creator-benchmark candidates. It replaces neither the source candidate files
nor the required independent confirmation.

## Evidence and method

- The 37 original candidates were checked against the checksum-verified 2-FPS
  dense RGB contact sheets from `calorie_creator_benchmark_dense_review_evidence.zip`.
- The four supplemental Michelle Briehler candidates were checked against the
  checksum-verified 2-FPS pose sheets and the archived 10-second RGB context in
  `supplemental_pose_review.zip` (outer SHA-256
  `0d89ec3fd3fe7f56155c641464c1bc5f09b7071a1ab3e9ae938765a6bed5c588`).
- Decisions use visible motion only. Titles and on-screen text were not allowed
  to override motion.
- Frozen model predictions were not consulted when making any decision in this
  pass. However, model reports existed before this pass, so it is honestly
  marked `blind_review=false` and cannot count as an independent benchmark
  review.

## Result

- 32 supported exercise regions are retained.
- Four unsupported compound exercise regions are retained as `unknown`.
- Five locators contain no usable target motion and are rejected.
- All 14 supported classes now have at least one retained region.
- The three labels changed in the faulty Notebook 29D wrong-page UI are
  explicitly discarded.

Every retained row still has `needs_second_review=true` and
`benchmark_ready=false`. The next review is a small independent confirmation
set: all medium-confidence rows, all four unknown rows, and a stratified sample
of the remaining high-confidence rows. It is not another 41-row blind widget
pass.

That bounded set is materialized as `independent_confirmation_queue_v1.csv`:
17 rows total (eight medium-confidence regions, four compound unknowns, and
five high-confidence controls). Its decision fields are intentionally blank;
they must not be prefilled or inferred from the Codex pass.

Run the reproducible structural audit with:

```bash
python3 ml/scripts/audit_creator_benchmark_adjudication.py \
  --adjudication ml/data/youtube_creator_benchmark_v1/codex_dense_adjudication_v1.csv \
  --original-candidates ml/data/youtube_creator_benchmark_v1/candidate_intervals_v1.csv \
  --supplemental-candidates ml/data/youtube_creator_benchmark_v1/supplemental_candidates_v1.csv \
  --confirmation-queue ml/data/youtube_creator_benchmark_v1/independent_confirmation_queue_v1.csv \
  --report ml/data/youtube_creator_benchmark_v1/codex_dense_adjudication_audit_v1.json
```

The current audit passes with zero structural errors: 41/41 candidate IDs,
36 retained non-overlapping regions, 14/14 supported classes, and complete
coverage of the required confirmation subset. It deliberately reports
`benchmark_locked=false` while the 17 independent decisions and continuous
timeline audit remain incomplete.
