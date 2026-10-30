# RepCount-A intake v2 — pilot results and locked parameters (2026-10-25)

Evidence: `ml/artifacts/repcount_intake_v2/pilot/` (Notebook 40, 94/94 clips).
These parameters are locked from pilot clips only. Pilot and v1 clips may go to
train or dev, never to the sealed test.

## Visual review (all 64 pilot clips)

`pilot_visual_review_v1.csv` holds Claude's contact-sheet review: target,
variant, usability, confidence, issue tags. Reviewer
`claude_visual_contact_sheet`.

- **51 of 64 clips are usable.** The 13 unusable clips are edited cutaways or
  close-ups (`stu1_5`, `stu1_49`, `stu5_28`), talking-head tutorials
  (`stu7_32`, `stu10_42`, `stu6_9`), crowded or partner scenes (`stu8_54`,
  `stu1_62`), an undecidable backlit clip (`stu2_33`), and compound moves:
  muscle-ups (`stu2_38`), push-up to pike (`train2737`), a push-up variant
  compilation (`stu3_49`), and a front/lateral/press shoulder complex
  (`stu1_14`).
- For usable clips in the six supported buckets, every published action
  matched the visible motion. The published action label is a good locator.
  Usability is the main problem.
- **Front-raise bucket confusers:** a bent-over raise that resembles a dumbbell
  row (`stu3_18`, needs second review) and a seated rear-delt fly (`stu2_23`).
- **Multi-person scenes mislead the single-pose tracker.** In `stu4_72` and
  `stu8_54` it followed the standing coach or judge. The class rules reject
  these because the expected motion is missing.

## Scene grouping (locked)

`ml/scripts/repcount_intake_v2_scene_groups.py`: frozen ImageNet ResNet-50,
mean of 3 thumbnails per clip, cosine similarity, union-find.

- **Merge threshold 0.85.** The known v1 duplicates score 0.929
  (`stu1_69`/`stu6_59`) and 0.987 (`stu8_49`/`stu9_56`). The closest distinct
  pair in the 94 clips scores 0.794. Twelve pairs between 0.74 and 0.79 were
  checked by eye; all are different people and places.
- **Result on 94 clips:** 92 groups. Exactly the two known pairs merge
  (`pilot_scene_groups_v1.csv`).
- **Gray zone 0.78-0.90:** pairs here get a visual check in the full intake
  (`pilot_scene_gray_zone_v1.csv`; the 3 pilot pairs were checked as distinct).
- **Limitation:** this detects shared scenes, not the same person in a
  different place.

## Tier-1 rules (locked as `tier1_v1`)

Code: `ml/scripts/repcount_intake_v2_tier1.py`. Scores:
`pilot_tier1_v1.csv`.

- **Common gates:** pose detection at least 0.90; at most 2 edit cuts (abrupt
  torso jump or rescale); repetition autocorrelation at least 0.30 at the
  period implied by RepCount's published count (supported buckets).
- **Class rules:** squat (upright torso, knee cycles), jumping jack (upright,
  arm and leg cycles), pull-up (vertical, hands over head in at least 55% of
  frames, body rises), push-up (horizontal, hands below shoulders, no pike or
  plyometric travel), bench press (horizontal, hands above shoulders), sit-up
  (torso cycles more than the thighs, hips stay down). Battle rope and pommel
  horse take the common gates only and become `unknown`.
- **Always reviewed:** the front-raise bucket and `others` (row and
  lateral-raise confusers and mixed content).

| Bucket | Clips | Usable | Auto-accepted |
| --- | ---: | ---: | ---: |
| squat | 8 | 8 | 6 |
| jumping_jack | 8 | 6 | 5 |
| sit_up | 8 | 6 | 5 |
| pull_up | 8 | 7 | 3 |
| push_up | 8 | 4 | 3 |
| bench_press | 8 | 7 | 2 |
| battle rope / pommel horse | 7 | 7 | 3 |
| front raise | 8 | 6 | 0 (always reviewed) |
| others | 1 | 0 | 0 (always reviewed) |

**Pilot criterion met:** 27 auto-accepted, 0 wrong or unusable. All 13 unusable
clips were sent to review. Because the thresholds were set on these same
clips, this proves only that the rules can separate the pilot, not their
error rate on new clips. The planned random 10% audit of auto-accepted clips
in the full intake measures that. If it finds more than 1 wrong label in a
class's sample, that whole class goes to visual review.

**Yield:** about 42% of pilot clips are auto-accepted, and bench press is
lowest (2/8) because of spotters, foreshortened views, and edits. Expect
roughly 55-60% of the remaining ~950 clips to need tier-2 visual review.

## Not done

- No clip is labeled `auto_verified` yet. Tier-1 labels apply only in the full
  intake, after its audit.
- The full-intake shard notebooks are not built.
- Role assignment (train/dev/sealed test) waits for full-set scene groups.
