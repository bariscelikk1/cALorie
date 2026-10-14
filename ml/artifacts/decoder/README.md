# cALorie provisional dense decoder calibration

Notebook 18 keeps the V6-C checkpoint frozen and changes only long-video
decoding. It predicts every eight frames, applies gate hysteresis, removes
short supported runs, and can merge short `unknown` gaps between equal labels.

The local validation run used 90 segments and 5,073 dense windows from three
creator groups excluded from all V6 training, validation, and internal-test
splits. The locked GainsByBrains test was not loaded. The provisional decoder
selected gate entry/exit thresholds of **0.95/0.90**, exercise entry/hold
confidences of **0.40/0.15**, a minimum supported duration of **2 seconds**,
and no gap merge.

Dense decoding improved accuracy from **56.97% to 57.30%**, Macro F1 across
present classes from **29.89% to 30.69%**, creator-mean Macro F1 from **50.22%
to 50.52%**, and unknown recall from **67.88% to 68.36%**. The small gain shows
that temporal stabilization helps, but cannot repair unsupported domain shift
or exercise-class confusion.

These settings remain provisional because historical timeline notes still
require visual spot-checking and seven supported classes are absent from this
calibration set.
