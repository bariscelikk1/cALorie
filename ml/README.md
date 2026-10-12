# cALorie ML

This directory contains the local, dataset-driven rebuild of cALorie. The
primary task is 15-class workout recognition from temporal pose landmarks, with
an additional `unknown` class. Exercise-specific state machines count complete
repetitions; plank is measured by duration.

## Verified progress

The landmark pipelines now produce six compatible archives: Workout/Fitness,
MM-Fit exercise and `unknown`, and three reviewed long-form YouTube batches.
The newest YouTube batch adds 205 usable segments from four independent source
videos after seven low-detection `unknown` segments are filtered. All archives
retain source groups so related windows stay in one split.

The locked 917-second mixed workout exposed opposite failure modes. TCN v1
recognized 66.5% of supported exercise windows but rejected only 32.7% of
unsupported exercise and 26.2% of transitions. TCN v3 rejected 79.6% of
unsupported exercise and 88.9% of transitions, but recognized only 33.0% of
supported windows. Its higher overall accuracy was driven by the many
`unknown` windows. The two-stage v4 candidate recovered supported accuracy to
47.5%, but unsupported rejection fell to 32.7% and transition rejection to
54.0%. The gate is therefore the current bottleneck. See
[`artifacts/v4/README.md`](artifacts/v4/README.md).

## Current 15-class target

The evidence-driven class set is squat, push-up, jumping jack, pull-up, lunge,
sit-up, plank, shoulder press, dumbbell row, tricep extension, bicep curl,
lateral raise, bench press, deadlift, and lat pulldown. The first ten are
available in Workout/Fitness Video; MM-Fit supplies additional people and five
new movements. Burpee, mountain climber, and glute bridge remain external-data
candidates because the currently audited source contains too few canonical
examples to support a defensible trained class.

## First milestone

1. Audit dataset access, licenses, identities, and labels.
2. Populate `data/manifests/raw_v1.csv` without assigning the same person or
   source video to multiple splits.
3. Validate the manifest:

```bash
python ml/scripts/validate_manifest.py ml/data/manifests/raw_v1.csv
```

Training does not begin until the manifest contains reviewed samples and passes
validation.

## Model plan

- MediaPipe Pose provides frame-level landmarks.
- A Random Forest provides an explainable learned baseline.
- A gate TCN learns supported motion versus `unknown`/transition.
- A second TCN classifies accepted windows among the 15 supported exercises.
- A validation-only threshold sweep calibrates the gate without using locked-test labels.
- State machines count exercise phases and complete cycles.
- Evaluation reports Macro F1, per-class precision/recall/F1, confusion matrix,
  repetition MAE, exact-count accuracy, and off-by-one accuracy.

## Colab notebooks

The current rebuild uses ten sequential notebooks:

1. `01_colab_extract_workoutfitness.ipynb` converts selected Workout/Fitness videos to normalized 17-joint pose sequences.
2. `02_colab_prepare_mmfit.ipynb` converts the labeled MM-Fit exercise sets to the same representation.
3. `02b_colab_prepare_mmfit_unknown.ipynb` exports the unlabeled gaps between MM-Fit sets as `unknown` examples for rest and transitions.
4. `03_colab_train_tcn.ipynb` preserves the single-stage 16-class baseline.
5. `04_colab_analyze_mixed_video.ipynb` evaluates the archived single-stage candidate on locked GainsByBrains and scores it against frozen labels.
6. `05_colab_extract_youtube_mixed_landmarks.ipynb` downloads three reviewed long-form training videos and exports their labelled landmark segments.
7. `06_colab_extract_additional_youtube_landmarks.ipynb` processes the three earlier reviewed YouTube training videos that were missing from TCN v2, adding 111 segments without touching the locked tests.
8. `07_colab_extract_youtube_training_v4.ipynb` extracts 212 reviewed segments from four additional single-person long workouts while keeping the new creator-separated test locked.
9. `08_colab_train_two_stage_tcn.ipynb` trains the binary gate and 15-class exercise TCN from all six versioned archives in one T4 session.
10. `09_colab_evaluate_two_stage_tcn.ipynb` evaluates the two-stage checkpoint on locked GainsByBrains using CPU and exports a scored report.

Notebook 08 downloads all six versioned landmark ZIPs from GitHub by default.
Run it on T4 and preserve `calorie_two_stage_tcn_report.zip`. Notebook 09 runs
on CPU and downloads the archived report automatically. Its locked external
evaluation shows that v4 recovers supported recognition to 47.5% but reduces
unsupported rejection to 32.7%; the gate still needs better hard negatives,
boundary handling, or a revised decision rule.

## External evaluation

Notebook 04 exports model predictions, but it cannot measure accuracy without
independent human labels. Score an exported mixed-video analysis with:

```bash
python ml/scripts/score_exported_mixed_video.py \
  --predictions path/to/window_predictions.csv \
  --annotations path/to/labels_v1.csv \
  --output path/to/evaluation
```

Keep each external-test video and its labels out of training. Compare future
models on the same frozen tests using supported-class accuracy, unknown and
transition rejection, balanced accuracy, macro F1, and per-movement errors.
