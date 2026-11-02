# Short-clip check of final model v2 (informational, 2026-11-02)

A quick, small check requested before the class presentation: how does the final model (v2, Notebook 47) do on
**brand-new short single-exercise videos** from creators never used in training? Nothing was tuned or selected from
the result; the model, threshold (0.65), and decoder are exactly the shipped ones.

- 15 short (20-75 s) tutorial clips from 12 creators not in any exclusion or training list, one or two per exercise
  (no real pull-up demo qualified, so pull-up is not covered). The exercise label is the video's own title plus a visual
  check of six frames per clip. One clip was an animated cartoon and was excluded by the rule "real people only", leaving 14.
- Raw video was deleted right after pose extraction; only `results.csv` and the scripts are kept.
- A clip counts as correct when the longest supported label the model gives it equals the exercise.

**Result: 11 of 14 clips correct (79%).** The three misses: a squat demo and a sit-up demo with two people and mostly
talking (the model said `unknown` the whole time), and a single-arm dumbbell row with a bench (`unknown` the whole
time). Without the three flagged talking/two-person demos: 10 of 11 (91%). Averaged over time, the model labeled 50% of
each clip with the right exercise and 46% `unknown`; tutorials include talking and standing time, so this share is a
lower bound on how well exercise moments are recognized.

Limits: 14 clips, chosen by one person from YouTube search results, tutorial-style rather than workout-style, one clip
per class at most two; this is a sanity check, not a benchmark, and the interval is wide.
