# Gainsbybrains external mixed-video evaluation

This evaluation compares the TCN's 4.27-second sliding-window predictions with
human timeline labels for a 917.4-second workout video that was not used for
training. A three-second guard is removed from each segment boundary for the
stable-interior metrics.

## Main result at the notebook's 0.55 confidence threshold

- Pose detection rate: 99.9% (13,761 sampled frames)
- All-window accuracy: 40.3%
- Stable-interior accuracy: 42.3%
- Stable-interior balanced accuracy: 49.3%
- Stable-interior macro F1: 19.5%
- Supported-exercise accuracy: 66.5%
- Unsupported-exercise rejection: 32.7%
- Transition/intro/outro rejection: 26.2%

## Movement-level finding

The model correctly recognized both plank variations and two of the three squat
families (sumo squat pulse and squat kick). It missed jumping jack entirely,
mostly calling it pull-up, and missed pop squat, mostly calling it deadlift.
Unsupported movements and transitions were often assigned a known exercise.

## Threshold finding

Raising the threshold to 0.80 keeps supported-exercise accuracy at 65.6% while
improving unsupported-movement rejection to 76.7% and transition rejection to
59.5%. The resulting 70.0% stable accuracy is helped by this video's large
amount of `unknown` content, so it must not be presented alone as model quality.
Use supported accuracy, rejection rates, balanced accuracy, macro F1, and the
per-movement table together.

## Reading the probability timeline

`raw/probability_timeline.png` plots video time on the horizontal axis and the
TCN's smoothed class probabilities on the vertical axis. Each colored line is
one exercise class. The dashed horizontal line is the 0.55 rejection threshold:
the highest class above it becomes the prediction, while a window whose best
class stays below it is emitted as `unknown`.

A useful prediction appears as one stable, isolated plateau for the correct
class during the corresponding movement, followed by a drop at the transition.
Rapid crossings near the threshold indicate ambiguity. A tall plateau only
means confidence; it does not prove correctness. This run contains several
near-1.0 plateaus for wrong classes, which is evidence of confident domain-shift
errors. Read the plot together with `labels_v1.csv` and
`window_predictions_scored.csv`, then use the confusion matrix and per-movement
results to identify which confident regions were actually correct.

## What this proves

The end-to-end pipeline works on a long mixed workout: video -> MediaPipe pose
landmarks -> overlapping TCN windows -> smoothed/rejected predictions -> merged
timeline -> external evaluation. The current bottleneck is recognition and
rejection quality, not pose detection.

## Highest-value next changes

1. Add labeled long-video windows for jumping jacks, pop squats, transitions,
   burpees, running in place, and other unsupported movements.
2. Retrain with a stronger and more varied `unknown` class sampled from actual
   transitions and unsupported exercises.
3. Select the rejection threshold on a validation set; 0.80 is the first value
   to test, not a final value chosen from this external test video.
4. Keep this exact video as a locked external test and never add its windows to
   training.

The source video is intentionally excluded from this repository. `labels_v1.csv`
contains the frozen human timeline annotation, and `mixed_video_analysis.zip`
preserves the original notebook export. The expanded `raw/` directory contains
the same raw outputs for direct inspection. `window_predictions_scored.csv`
adds the human truth to each window. `threshold_sweep.csv`,
`per_movement_results.csv`, and `confusion_matrix.csv` provide the detailed
diagnostics.

Reproduce the 0.55-threshold score from the repository root with:

```bash
python ml/scripts/score_exported_mixed_video.py \
  --predictions ml/artifacts/v1/evaluation/gainsbybrains_external_v1/raw/window_predictions.csv \
  --annotations ml/artifacts/v1/evaluation/gainsbybrains_external_v1/labels_v1.csv \
  --output /tmp/gainsbybrains-score
```
