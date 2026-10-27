# cALorie temporal annotation guide

This guide defines how long workout videos become trustworthy temporal labels.
The model only sees pose landmarks and time, so a label must be decidable from
visible body motion. Titles, transcripts, and creator chapters may help locate
a segment, but they cannot override what is visible in the video.

## Unit of annotation

One row represents one contiguous interval with a single semantic state. The
timeline must be sorted, non-overlapping, and cover the reviewed part of the
video without silent gaps.

Required fields retain the existing v1 schema. New annotation batches should
also fill the four QA fields in `templates/timeline_labels_v2.csv`:

- `annotation_confidence`: `high`, `medium`, or `low`;
- `review_status`: `draft`, `reviewed`, `adjudicated`, `auto_verified`, or
  `rejected`;
- `reviewer`: stable reviewer name or ID;
- `needs_second_review`: `true` for ambiguous boundaries or labels.

Low confidence is useful evidence. Never force an uncertain supported label.

### `auto_verified` (approved by the user 2026-10-24)

`auto_verified` means a row passed predeclared automatic pose and
repetition checks, and its class passed a sampled visual audit, but no person
or assistant viewed that specific row. Rules:

- `annotation_source` must name the rule set version and the audit result.
- `auto_verified` rows may be used only in non-promotable experiments.
- A promotable model needs every training row it uses to be `reviewed` or
  `adjudicated`.
- Never relabel an `auto_verified` row as `reviewed` unless it was viewed.

## Label decision order

1. Mark intros, outros, rests, previews, and movement changes with the matching
   `segment_type` and `current_tcn_label=unknown`.
2. For an exercise interval, identify the visible movement as precisely as
   possible in `fine_label`.
3. Map it to one of the 14 supported classes only when the visible motion
   matches that class definition.
4. Use `unknown` for unsupported, compound, ambiguous, or badly occluded
   movements. Record the reason in `notes`.
5. Mark a supported-looking edge case with `needs_second_review=true`. Do not
   solve ambiguity by guessing.

## Supported-class rules

The canonical names live in `ml/config/classes.json`. A variation may map to a
supported class when its main joint sequence remains the same and the product
is expected to accept it. Examples:

- bodyweight, sumo, pulse, and kick squat variants may map to `squat` after
  review;
- conventional crunches, anchored sit-ups, and incline-bench sit-ups may map
  to `sit_up` when repeated torso flexion is the dominant visible motion;
- V-ups/jackknives, reverse crunches or leg raises, and GHD-style
  hyperextension movements remain `unknown` rather than being forced into
  `sit_up`;
- plank and plank variants map to `unknown` in the post-v5 target;
- close-grip push-ups may map to `push_up`;
- a compound sequence containing multiple unsupported phases remains
  `unknown`, even if one phase resembles a supported class.

When a new edge case changes one of these decisions, update this guide and
recheck every earlier row with the same pattern.

### Edge-case rulings (user-approved 2026-10-27, long-video test v1)

1. Barbell bent-over row -> `unknown` (the supported class is `dumbbell_row`).
2. Supine dumbbell floor press and glute-bridge dumbbell press -> `bench_press`.
3. Chest-supported and two-dumbbell bent-over rows -> `dumbbell_row`.
4. Split squats and forward/reverse lunges with a knee drive or reach -> `lunge`
   (lateral lunges stay `unknown`).
5. Staggered, sumo, in-and-out, and step-out squats -> `squat`.
6. Dumbbell tricep kickback -> `tricep_extension`.
7. Crunch variants with arms overhead or reaching to the knees -> `sit_up`.
8. Single-arm kneeling dumbbell press -> `shoulder_press`.
9. Push-ups with feet on a ball, on dumbbell handles, or side-to-side -> `push_up`.
10. Pull-ups with the head cropped or in dark footage -> `pull_up` when the
    motion is visible.

### Edge-case rulings (user-approved 2026-10-27, long-video training v1)

11. Stiff-leg, single-leg, kickstand, staggered, and Smith-machine Romanian
    deadlifts -> `deadlift`.
12. Single-kettlebell bent-over row -> `dumbbell_row`.
13. Arnold, push, single-arm, seated, and in-and-out presses -> `shoulder_press`.
14. Zottman and partial-range (top-half) curls -> `bicep_curl`.
15. Knee push-ups and push-up pulses -> `push_up`.
16. Smith-machine front squats and sumo-squat pulses -> `squat`.
17. A set that mixes variations of one move (lateral-raise variations,
    skull crushers alternating with presses) keeps the main class.
18. A forward or reverse lunge with an arm move (curl, weight pass, overhead
    transfer) -> `lunge`. Side lunges, squat-to-press, and other compounds
    stay `unknown`.

## Temporal boundaries

- `start_s` is the first frame where the labeled state is visibly established.
- `end_s` is the first frame belonging to the next state.
- Countdown text alone does not define the boundary; visible motion does.
- Use a transition segment when the athlete changes position, previews the
  next move, adjusts equipment, or pauses between exercises.
- Record realistic precision in `boundary_precision_s`; do not claim frame
  precision from ten-second contact sheets.
- If a boundary remains ambiguous by more than two seconds, use medium/low
  confidence and request a second review.

## Quality-control loop

1. **Pilot:** label 10-20 segments before scaling a source.
2. **Early review:** inspect the pilot and refine unclear definitions.
3. **Independent repeat:** label at least 10% of intervals twice. Include every
   low-confidence row and every new hard-positive/hard-negative pattern.
4. **Agreement:** compare the two timelines with
   `audit_timeline_annotations.py --second-root ...`. Resolve disagreements;
   do not silently use majority voting as ground truth.
5. **Automated audit:** run the same script without `--second-root` before
   landmark extraction.
6. **Model feedback:** review high-confidence model mistakes and low-margin
   predictions first. Correct confirmed label errors; preserve difficult but
   correctly labeled examples.
7. **Versioning:** keep source video ID, annotation source, reviewer, split,
   and notes with every row. Never move intervals from one source video across
   train, validation, and test.

An annotation batch is accepted only when it has no structural audit errors,
no training row marked as draft/rejected, all low-confidence rows have a second
review, and disagreements have been adjudicated.

## Data and augmentation checks

- Split by original video and person before creating temporal windows.
- Keep all windows from one original video in one split.
- Inspect class, source, person, and camera-view counts rather than only the
  total number of windows.
- Visualize landmark augmentations after transformation. A horizontal mirror
  must swap left/right joints consistently; time warping must preserve the
  action label; missing-landmark simulation must not erase the movement.
- Add one augmentation family at a time and compare it against the fixed
  baseline and locked evaluation.

These rules implement the recurring advice in practitioner discussions:
iterate on guidelines, explicitly retain edge cases, measure repeated-label
agreement, review early batches, prevent sequence leakage, and inspect what
augmentation actually feeds to the model.

Sources:

- [r/MachineLearning: effective labeling guidelines](https://www.reddit.com/r/MachineLearning/comments/o5ggz9/)
- [r/MachineLearning: handling badly labeled data](https://www.reddit.com/r/MachineLearning/comments/vtu6f9/)
- [r/computervision: neighboring frames across splits are leakage](https://www.reddit.com/r/computervision/comments/1is2i4r/)
- [r/computervision: augmentation practice and visual checks](https://www.reddit.com/r/computervision/comments/1rld1bl/)
- [r/MachineLearning: MIT data-centric AI course discussion](https://www.reddit.com/r/MachineLearning/comments/1194wm0/)

