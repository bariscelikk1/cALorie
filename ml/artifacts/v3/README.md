# cALorie experiment artifacts — v3 inputs

This directory preserves the reviewed long-form YouTube landmark archives that
will be added to the next TCN training run. The source MP4 files are excluded;
the compact NPZ sequences and their manifests are sufficient for Notebook 03.

## Additional YouTube landmarks

`landmarks/calorie_youtube_additional_landmarks_v1.zip` contains the reviewed
segments produced by Notebook 06.

## YouTube training batch v4

`landmarks/calorie_youtube_training_landmarks_v4.zip` contains 212 reviewed
segments from four source videos. The archive audit found:

- 212 readable NPZ files and 81,863 sampled frames
- 205 `ok` segments and seven low-detection `unknown` segments
- four independent source-video groups
- 96.79% mean pose-detection rate
- consistent `(frames, 17, 4)` landmark arrays
- no missing files, invalid shapes, NaNs, infinities, or duplicate clip IDs

Notebook 03 filters the seven low-detection segments before window generation.
This generated archive retains the older `youtube_additional_workouts_v1`
source-dataset string because extraction began before the notebook metadata fix;
its YouTube-based `group_id` values are correct, so group-separated splitting is
unaffected.

`SHA256SUMS.txt` identifies the exact archives preserved here.
