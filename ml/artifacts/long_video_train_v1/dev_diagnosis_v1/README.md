# Long-video training v1 — dev diagnosis (2026-10-27)

PLAN.md section 2. Frozen V6-F and v2 (3 seeds) scored once on the 5 dev
videos (77 min of supported exercise) by `ml/scripts/diagnose_long_video_dev_v1.py`
(commit `e875a90`, predeclared reading in its docstring) on the Mac GPU.
Pose hashes were verified against the evidence ZIPs. No training, no tuning,
no locked-test access.

**Reading: data problem, for all four models.** The gate barely separates
exercise from downtime (AUROC 0.61-0.65), so lowering the threshold frees
exercise time only by letting downtime through at about the same rate. At the
lowest threshold that keeps downtime-called-unknown within 10 points, exercise
time called unknown drops only 6-14 points (bar: 15). Pose quality (missing
frames, visibility, figure size, side view) shows no consistent pattern.

| Dev control (smoothed) | V6-F | v2 seed 42 / 137 / 2026 |
| --- | ---: | ---: |
| Macro F1 (15 labels) | 29.7% | 24.1 / 26.0 / 25.7% |
| Exercise time called unknown | 37.7% | 49.9 / 62.0 / 54.7% |
| Downtime called unknown | 58.5% | 69.8 / 78.9 / 72.4% |

The classifier is also weak on these sources (gate ignored, V6-F / v2 s42):
lunge 9 / 45%, shoulder press 29 / 8%, sit-up 0 / 65%, tricep extension
0 / 0%, dumbbell row 58 / 0%. v2's classifier still knows curls (91%) and
lateral raises (98%), but its gate rejects 81% and 94% of that time.
Push-ups, bench press, squats, and deadlifts are the healthy classes.

Files: `diagnosis.json` (summary per model), `dev_metrics_by_model_video.csv`
(section 3 control numbers), `threshold_sweep.csv`, `oracle_by_class.csv`,
`oracle_confusion_*.csv`, `rejection_breakdown.csv`, `dev_windows.csv.gz`
(every window), `run.log`.
