# RepCount-A intake v2 — plan (DRAFT, not approved)

Status: proposal written 2026-10-24. No notebook, download, or label exists
yet. Nothing here changes `ml/data/repcount_development_v1/`.

## Goal

Add source diversity for the six supported classes RepCount-A covers, plus
realistic `unknown` motion. The diagnosis behind this: V6-F learned too few
sources per class, so it fails on unseen footage. Single-knob experiments
(architecture, sampler, threshold) have not fixed that.

## What exists (pinned metadata, hashes verified 2026-10-24)

RepCount-A metadata `lmms-lab-eval/repcount@d4c2ad3`: 1,040 videos. The video
mirror `lmms-lab-eval/repcounta-lance@ae2e0b0` is about 9.7 GB.

| Our class | Published actions | Videos |
| --- | --- | ---: |
| squat | squat, squant | 135 |
| sit_up | situp | 131 |
| pull_up | pull_up, pullups | 127 |
| bench_press | bench_pressing, benchpressing | 125 |
| push_up | push_up, pushups | 122 |
| jumping_jack | jump_jack, jumpjacks | 117 |
| unknown candidate | front_raise, frontraise | 130 |
| unknown candidate | pommelhorse, battle_rope, others | 153 |

Not covered: bicep_curl, deadlift, dumbbell_row, lat_pulldown, lateral_raise,
lunge, shoulder_press, tricep_extension. They need other sources later.

Published actions are only locators. In v1, 6 of 10 `situp` clips were
crunch, V-up, GHD, or reverse-crunch variants, and 1 `front_raise` was a
lateral raise.

## 1. Selection

- Take all 1,010 videos not already in v1. The 30 v1 clips keep their
  adjudicated labels.
- Use only RepCount's annotated cycle bounds (first to last repetition), as
  Notebook 37 did. This excludes setup, rest, and walk-off.
- **Pilot first:** about 60 clips, 7 or 8 per published action, chosen by hash.
  The full run happens only after the pilot passes (section 3).
- **Compute:** Notebook 37 ran 30 clips on CPU. The full set runs as about 4
  CPU shards of about 250 clips, each returning one ZIP. Shard runtime is not
  measured yet; the pilot will measure it.
- **Output per clip:** 15-FPS pose, one contact sheet (12 frames), 3 scene
  thumbnails, an image embedding, and automatic check results. No raw video
  is returned.

## 2. Source groups and splits

`stuN` is not a person, and about 190 clips have no `stuN` code at all, so
groups must come from the footage.

1. **Scene and appearance clustering:** each clip gets an image embedding
   from 3 frames (pretrained, frozen). Clips whose embeddings are close are
   joined into one group (union-find). The threshold is predeclared from the
   30 v1 clips: it must merge both known pairs
   (`stu8_49`+`stu9_56`, `stu1_69`+`stu6_59`). Over-merging is safe; it only
   makes groups bigger. Under-merging leaks, so the threshold leans toward
   merging.
2. Identical video hashes always merge.
3. Groups are assigned to roles by hash, stratified by class:
   - **train** about 60%
   - **dev** about 20%: development decisions and early stopping
   - **sealed test** about 20%: opened once, at the end of this data arc
4. The 30 v1 clips, the pilot clips, and every group touching them go to
   train or dev only. They have already influenced decisions, so they can
   never be in the sealed test.
5. Audit: no group spans roles, and every class has at least 10 clips in the
   sealed test, or the split is redrawn with a new predeclared salt.

## 3. Labeling without you reviewing hundreds of clips

The model's own predictions are **never** a label source; they only order
the review queue. Each clip goes through three tiers.

**Tier 1 — automatic gates (all must pass):**
- pose detected in at least 80% of frames;
- repetition check: the motion period from autocorrelation implies a count
  within ±35% of RepCount's published count;
- a class-specific pose rule:

| Class | Rule (pose only) |
| --- | --- |
| pull_up | wrists above head throughout; vertical body; vertical hip travel |
| push_up | torso near horizontal and prone; elbow angle cycles |
| bench_press | torso near horizontal and supine; wrists cycle vertically over shoulders |
| jumping_jack | arms and legs abduct and adduct in phase |
| squat | torso upright; knee and hip angles cycle together; feet fixed |
| sit_up | supine start; torso angle cycles more than the leg angle (else `unknown`: V-up, leg raise) |
| front_raise / other | default `unknown`; any clip that looks like a lateral raise (sideways shoulder abduction) goes to review |

**Tier 2 — Claude visual review** of every clip that fails tier 1, plus a
random 10% audit of every class's tier-1 passes. It uses the contact sheets,
as in the v1 dense adjudication. If the audit finds more than 1 wrong label
in a class's sample, that class's tier-1 passes all go to review.

**Tier 3 — you:** a 20-clip random spot-check as the independent second
review the annotation guide requires (about 15 minutes, contact sheets only).
Everything still unclear stays `unknown` or is dropped. Nothing gets forced
into a supported class.

Expected review load: unknown until the pilot. If tier 1 passes most of
pull_up, push_up, bench_press, jumping_jack, and squat, review is roughly the
sit-up and front-raise pools, plus failures and audits.

**Provenance — needs your decision:** `ANNOTATION_GUIDE.md` allows only
`draft`, `reviewed`, `adjudicated`, and `rejected`, and forbids training on
`draft`. A rule-checked clip that nobody viewed is not honestly `reviewed`.
Proposal: add `review_status=auto_verified`, with `annotation_source`
recording the rules and the sampled-audit result. `auto_verified` rows may be
used in non-promotable experiments only. A promotable model would need them
upgraded by review. This changes the annotation contract, so it needs your
approval.

**Pilot pass criteria (predeclared):** Claude visually reviews all ~60 pilot
clips. Tier 1 is accepted for a class only if its auto-accepted pilot clips
have no wrong labels. Rules may be adjusted once using pilot clips only, and
those clips then go to train or dev.

## 4. What this cannot do

- It cannot help the 8 uncovered classes.
- The data is one dataset (RepCount-A). More sources are still needed, so
  this plan alone will not make the model production-ready.
- The license is `other`. Raw video is never committed. Any model trained on
  this stays research-only until the terms are checked.

## Order of work after approval

1. Build the pilot intake notebook (CPU), dry-run locally, push, link.
2. You run it; return the ZIP.
3. Claude reviews the pilot, finalizes the rules and threshold, commits them.
4. Shard notebooks for the remaining ~950 clips.
5. Labels, groups, and split audit committed.
6. Only then plan a training experiment.
