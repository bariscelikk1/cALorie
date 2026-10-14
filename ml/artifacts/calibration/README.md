# cALorie independent gate calibration

Notebook 17 ran locally on the Mac CPU and evaluated the frozen V6-B and V6-C
checkpoints on three creator groups excluded from every V6 train, validation,
and internal-test split. It used 90 labelled timeline segments and 1,198
64-frame windows. The locked GainsByBrains long-video test was not loaded.

The provisional comparison selected V6-C at a gate threshold of **0.95**. On
the eight labels present in this small calibration set it reached **56.76%**
accuracy, **30.65%** Macro F1, and **67.53%** unknown recall. V6-B reached
50.92% accuracy and 29.10% Macro F1 at threshold 0.105. The diagnostic V6-C
gate plus V6-B classifier did not improve the independent result.

These numbers expose a substantial domain shift and weak exercise coverage:
only seven supported classes occur, and dumbbell row, lunge, sit-up, and
tricep extension have zero recall. Historical annotation notes also retain a
draft warning even though the manifest says reviewed. The 0.95 threshold must
therefore remain provisional until the timelines are visually spot-checked and
the missing classes receive creator-separated calibration examples.

`calorie_v6_gate_calibration_report.zip` contains the threshold sweep,
per-window predictions, system comparison, classification reports, confusion
matrix, calibration curve, and machine-readable summary.
