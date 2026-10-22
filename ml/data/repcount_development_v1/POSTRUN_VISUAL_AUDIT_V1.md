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

## Dense visual adjudication update

Notebook 38 returned dense 4 FPS evidence and silent previews for all eight
medium-confidence rows. Frame-by-frame review resolves every one of them:

- `stu1_53`, `stu3_54`, `stu5_52`, `stu6_50`, `stu8_49`, and `stu9_56` map to
  `sit_up` under the clarified torso-flexion rule;
- `stu2_67` contains clear repeated bodyweight squats and maps to `squat`;
- `stu9_12` is a bent-elbow dumbbell lateral raise and maps to
  `lateral_raise`.

The final row-level calls are recorded in
`final_visible_adjudication_v1.csv`. Against those calls, frozen V6-F matches
11/30 clips (36.7%): 6/18 supported clips (33.3%) and 5/12 unknown clips
(41.7%). By class it is 6/10 for `squat`, 0/7 for `sit_up`, and 0/1 for
`lateral_raise`. The lower result is expected: six clips previously credited
as correct unknown rejections are now correctly recognized as supported
`sit_up` examples.

Two source collisions remain explicit: `stu8_49` and `stu9_56` share one
outdoor crunch source, while `stu1_69` and `stu6_59` appear to share one
orange-rig squat source. Any future split must keep each source group intact.
This is still a source-shift diagnostic, not person-disjoint accuracy.

## Decision

- Do not train Notebook 38 from the original `train_pool` split.
- Retain this package as a source-shift/error-analysis set.
- The eight second-review rows are resolved, but every RepCount row remains
  `training_allowed=false` until a predeclared source-group-disjoint exploratory
  split is created. Never treat `stuN` as a person ID.
- A future RepCount retrain is non-promotable and must preserve untouched
  diagnostic source groups; it must not use these rows for threshold tuning.
- The frozen threshold remains 0.65; this audit does not tune it.
