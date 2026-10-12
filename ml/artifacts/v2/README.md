# cALorie experiment artifacts — v2 inputs

This directory begins the second TCN experiment with reviewed, long-form
YouTube workout data. The source MP4 files are excluded from GitHub. The
landmark archive is the compact, reproducible training input produced by
`05_colab_extract_youtube_mixed_landmarks.ipynb`.

## YouTube mixed-workout landmarks

`landmarks/calorie_youtube_mixed_landmarks_v3.zip` contains 91 reviewed
segments from three source videos. Each NPZ stores a 15 FPS sequence with 17
normalized pose landmarks and four values per landmark (`x`, `y`, `z`, and
visibility). All segments from one source video share a `group_id`, so the
training notebook cannot split neighboring segments from the same video across
train, validation, and test sets.

Validation results:

- 91 readable NPZ files and 39,652 sampled frames
- 90 `ok` segments and one three-second `unknown` intro with low detection
- 98.97% mean pose-detection rate
- no invalid shapes, NaNs, infinities, or manifest/frame-count mismatches
- 69 `unknown` segments and 22 supported-exercise segments

The high `unknown` count is intentional: unsupported exercises, rests,
previews, and transitions teach the classifier to reject movements outside its
supported classes. Notebook 03 uses weighted sampling so this majority class
does not dominate training batches.

The extracted manifest is included beside the ZIP for review. `validation.json`
records the machine-readable audit, and `SHA256SUMS.txt` identifies the exact
files committed here.
