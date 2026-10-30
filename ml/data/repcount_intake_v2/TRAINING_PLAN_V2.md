# RepCount-A training v2 — plan (DRAFT, not approved)

Status: proposal written 2026-10-27. Nothing is built. It follows training v1
stage A (`ml/artifacts/repcount_training_v1_stage_a/`), which failed only
the internal-test guard (−2.24 pp against a −2.00 pp limit).

## What v1 showed

- New footage (RepCount dev) improved a lot: Macro F1 61% to 86%, sit-ups 0%
  to 80%.
- The internal test lost sit-up recall (−15.4 pp; 147 windows from 4 source
  groups), pull-up recall (−16.7 pp), and unknown recall (−4.6 pp).
- The classes that lost the most were the ones RepCount dominated in the
  sampler: pull-up (83% of that class's sampler mass came from RepCount),
  sit-up (66%), and both gate targets (60%).
- **Caveat about the guard:** pull-up has only **4** internal-test windows,
  so −16.7 pp is less than one window per seed. Because Macro F1 weights
  every class equally, that tiny class may account for roughly half of the
  2.24 pp drop. The guard is therefore noisy. v2 keeps it **unchanged**
  anyway, because loosening a limit after failing it would be moving the
  goalposts.

## The one change

**Cap RepCount at 50% of each class's sampler mass**, for every exercise
class in the classifier and for both gate targets (supported / unknown).
Where RepCount's share is above 50%, its windows are scaled down so that new
and original sources carry equal mass in that class. Classes at or below 50%
are untouched (push-up 48%, deadlift 22%, lateral raise 17%, shoulder press
6%, and the 6 classes with no RepCount data).

Why 50%: it gives the original sources and the new sources an equal voice.
It is a round, predeclared value, not tuned on any result. No other value
will be tried.

| Class mass from RepCount | v1 | v2 |
| --- | ---: | ---: |
| pull_up | 83% | 50% |
| jumping_jack | 73% | 50% |
| bench_press | 71% | 50% |
| sit_up | 66% | 50% |
| squat | 58% | 50% |
| gate supported / unknown | 60% / 60% | 50% / 50% |

Inside each source's share, the existing square-root group tempering and the
hard-positive weights are unchanged.

## Everything else is identical to v1

Same roles file (`training_v1_roles.csv`), same data, recipes, seeds (42, 137,
2026), threshold 0.65, fusion, early stopping on V6-A validation only, the
same control (frozen V6-F), and the **same seven pass criteria with the same
limits** (TRAINING_PLAN_V1.md, section 5). Same two-stage evaluation: stage A
on dev; stage B (sealed test, once) only if stage A passes.

## Honest limits

- The dev clips were already scored once in v1. Judging v2 on the same dev
  set is slightly optimistic. That is why the sealed test, still unseen, is
  the final judge.
- If v2 fails, the RepCount arc stops here as a documented result, with no
  v3 sweep of cap values. A further attempt would need a new idea and a new
  plan.
- Non-promotable, for the same reasons as v1.

## Order of work after approval

1. Add the cap to the Notebook 42 builder as Notebook 43, dry-run it on the
   Mac, and commit.
2. Run stage A once; archive and analyze.
3. Stage B only if stage A passes, after your go-ahead.
