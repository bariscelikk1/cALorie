# RepCount-A intake v2 — results (2026-10-27)

Final table: `intake_v2_labels_v1.csv` (one row per clip, built by
`ml/scripts/build_repcount_intake_v2_labels.py`). Every row is still
`training_allowed=false`; a training experiment must list its rows in a new
versioned manifest.

## Coverage

- 1,010 non-v1 clips were selected (64 pilot + 946 full). 1,009 have pose;
  `stu1_10` cannot be decoded at its annotated end.
- **718 usable clips.** 291 are unusable: tutorials with talking heads,
  edited cutaways, crowds or several people in frame, tiny or blurry or
  rotated footage, and compound moves.
- **Label provenance:** 843 `reviewed` (Claude contact-sheet review) and 166
  `auto_verified` (tier-1 rules plus a passed class audit; non-promotable use
  only, per `ANNOTATION_GUIDE.md`).

| Label (usable) | Clips | Role groups |
| --- | ---: | ---: |
| unknown | 229 | 140 |
| squat | 99 | 71 |
| jumping_jack | 90 | 84 |
| bench_press | 81 | 77 |
| pull_up | 80 | 74 |
| sit_up | 68 | 63 |
| push_up | 58 | 54 |
| lateral_raise | 8 | 8 |
| deadlift | 3 | 3 |
| shoulder_press | 2 | 2 |

The v1 set had 7 sit-ups and 10 squats from about 8 sources. This adds 68
sit-ups and 99 squats from 63 and 71 role groups.

## What the review found

- **Published labels are often wrong among usable clips (41 of 718).** Eleven
  `situp` clips are V-ups, leg raises, bicycle crunches, or twists, which stay
  `unknown`. Eight "front raise" clips are lateral raises. "Bench pressing"
  includes 3 deadlifts, a squat, a shoulder press, and seated machine presses.
  Visible motion decided every label.
- **Unknown-bucket content:** pommel horse, battle ropes, rowing machines and
  boats, hammer throw, football juggling, and many front-raise variants.
  This is varied, realistic "not one of the 14" motion.
- **Tier-1 rules were strict on new clips:** they auto-accepted 21% (pilot:
  42%), so most clips were reviewed by eye. The audit found 1 wrong label in
  28 auto-accepts, so `auto_verified` rows are not error-free.

## Splits

`full_role_groups_v1.csv`: 857 role groups (largest 15). 430 usable clips
sit in groups eligible for a sealed test (no borderline link to another
group). Roles are not assigned yet. The plan's rule stands: pilot and v1
clips go only to train or dev.

## Not done

- No user spot-check yet (the plan's tier 3: 20 random clips).
- No train/dev/sealed-test assignment and no training run.
