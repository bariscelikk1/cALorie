# RepCount external development v1 post-run visual audit

This audit corrects two assumptions discovered after Notebook 37 returned. It is
a contact-sheet first pass, not a final video-level adjudication, and every row
remains excluded from training.

## Blocking findings

1. The `stuN` token is not a verified person identity. For example, the three
   `stu10` clips visibly contain different people, while `stu8_49` and
   `stu9_56` appear to contain the same actor and scene. Therefore the prior
   `stu1`–`stu7` versus `stu8`–`stu10` partition is not person-disjoint and must
   not be reported as validation.
2. Published action names are video-level metadata, not cALorie labels. The ten
   `situp` clips include crunches, a V-up/jackknife, a GHD/hyperextension
   variant, and a leg raise/reverse crunch. One nominal squat clip
   (`stu2_67`) does not visibly establish repeated squats in the selected
   cycle bounds.
3. Pose extraction is healthy: all 30 clips produced usable pose. The immediate
   blocker is semantic validity, not landmark detection.

## Provisional visible-motion score

Using `contact_sheet_visual_review_v1.csv`, the frozen V6-F prediction matches
the first-pass visible target on 16/30 clips (53.3%). This replaces the report's
8/30 metadata alignment only as a **review diagnostic**, not as accuracy.

- Unknown rejection: 10/18 first-pass unknown clips (55.6%).
- Supported visible clips: 6/12 correct (50.0%).
- Visible squats: 6/9 correct (66.7%).
- Three plausible sit-up variants: 0/3 correct.

These values include medium-confidence contact-sheet calls. They are not valid
for promotion, threshold selection, or comparison with the locked creator
benchmark.

## Decision

- Do not train Notebook 38 from the original `train_pool` split.
- Retain this package as a source-shift/error-analysis set.
- Before any RepCount training experiment, inspect the rows marked
  `needs_second_review=true` from video, replace `person_id` with an explicitly
  unverified source code, and use clip/source-disjoint development roles rather
  than claiming person-disjoint validation.
- The frozen threshold remains 0.65; this audit does not tune it.
