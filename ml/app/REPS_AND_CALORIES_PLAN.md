# Rep counting and calories for the web page — plan (approved by the user 2026-10-28)

Status: written 2026-10-28. Nothing is built. Deadline for the whole project:
2026-11-02.

## Goal

For every exercise segment the page already finds, also show **reps** and
**estimated calories**, with honest ranges. Keep it small: one new module
(`ml/app/reps_and_calories.py`) and a few lines in the page.

## 1. Rep counting

**Method (one generic counter, no new training).** For each exercise segment:
1. Take the segment's hip-centered 17-keypoint pose (15 FPS), fill gaps.
2. Reduce it to one motion signal: the first principal component of the
   keypoint positions over the segment, smoothed (Savitzky-Golay, about 0.4 s).
3. Count peaks with a minimum spacing of 0.6 s and a minimum prominence of
   35% of the signal's robust range. One peak = one rep.
4. Count only inside windows where the gate said "exercise", so rests between
   sets add nothing.

The constants above are the starting values. They may be tuned on the **dev**
clips only (item 3 below), then frozen before anything else is scored.

**Data for checking it.** RepCount-A clips carry a published human rep count
and our extracted pose. Each clip is one exercise, so the model's label is not
needed: we test the counter on the true class. Available non-unknown clips with
counts: dev 66 (bench press 11, jumping jack 12, pull-up 10, push-up 9,
sit-up 9, squat 15), sealed test 94, train 241. Classes with no RepCount clips
(curl, row, lunge, press, triceps, lateral raise, deadlift, lat pulldown) **cannot
be checked**.

**Steps and rules (set now):**
1. Build the counter and a scorer; both are committed before scoring.
2. Tune the constants on the **dev** clips only (66 clips), allowed.
3. Freeze. Score the **train** clips once as a sanity check (not for tuning).
4. Score the **sealed test** clips once (94 clips) for the report. The sealed
   test was spent for exercise recognition, but it has never been used for
   counting.
5. The locked long-video test is not used (it has no rep labels).

**Metrics:** exact-count rate, within-one-rep rate, mean absolute error, and
median relative error, overall and per class.

**Rule for what the page shows (decided on dev):** a class gets a rep count in
the page only if at least 50% of its dev clips are within one rep. Otherwise
the page shows time only for that class and says "reps not validated". Classes
without RepCount clips show "reps not validated" too.

## 2. Calories

Formula (standard): `kcal = MET x 3.5 x weight_kg / 200 x minutes`.
- **Minutes** = total time the page assigns to that exercise.
- **Weight** = typed by the user in the page (default 70 kg, never stored).
- **MET** = one fixed value per exercise, in a table in the module. Values start
  from the earlier project's configuration (moderate effort), based on 2011/2024
  Compendium of Physical Activities categories, and are rounded: squat 5.0,
  jumping jack 7.0, push-up 6.0, pull-up 6.0, lunge 5.0, sit-up 4.0; weights
  (bench press, curl, deadlift, row, lat pulldown, lateral raise, shoulder press,
  tricep extension) 3.5 to 5.0. The table is printed in the README, and I check each
  value against the Compendium page before building.
- **Range:** the page shows the estimate plus or minus 35%, because the exercise
  label can be wrong and MET is a population average, not a measurement.
- Calories **cannot be validated** with our data (no calorie ground truth). The
  report says so. They count only recognized exercise time, not rest.

## 3. Page changes

- A weight box (kg).
- Per-exercise table gains **reps** and **calories (range)** columns.
- A total calories line with the range.
- The existing disclaimer gets one more sentence about reps and calories.

## 4. Done when

- `reps_and_calories.py` and its scorer are committed.
- Dev and sealed-test rep results and the per-class enable list are archived in
  `ml/artifacts/rep_counting_v1/` with checksums.
- The page runs end to end (Streamlit's headless tester) with the new columns.
- README, FINAL_REPORT, and the handoff are updated and pushed.

## 5. Limits (stated up front)

- Only 6 of 14 exercises can be checked for reps; the rest are labeled unvalidated.
- RepCount clips are short single-exercise clips, not full sessions. In a full
  workout, a wrong exercise label or a missed segment makes the reps wrong.
- Calories rest on one fixed MET per exercise and are not personalized beyond
  weight.
- No model is retrained; the final model stays frozen.

## Effort

About 1 day: counter and scorer (half a day), page and docs (half a day).
