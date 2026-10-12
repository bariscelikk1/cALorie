# cALorie ML

This directory contains the local, dataset-driven rebuild of cALorie. The
primary task is 15-class workout recognition from temporal pose landmarks, with
an additional `unknown` class. Exercise-specific state machines count complete
repetitions; plank is measured by duration.

## Verified progress

The landmark pipelines have produced four compatible archives: 368 usable
Workout/Fitness clips, 616 MM-Fit exercise clips, 252 MM-Fit `unknown` clips,
and 91 reviewed segments from three long-form YouTube workouts. The YouTube
archive contributes 39,652 landmark frames, including unsupported movements,
rests, previews, and transitions labelled `unknown`. The first 16-class TCN
reached 87.6% held-out window accuracy, but that number does not describe
performance on long, unseen workouts.

Two frozen external tests now expose the generalization gap. A 45-second
jumping-jack/burpee video produced no correct jumping-jack windows. A separately
annotated 917-second mixed workout achieved 42.3% stable-interior accuracy,
66.5% supported-exercise accuracy, 32.7% unsupported-exercise rejection, and
26.2% transition rejection at the notebook's 0.55 threshold. MediaPipe detected
a pose in 99.9% of sampled frames, so the main bottleneck is exercise
recognition and rejection rather than landmark extraction. See
[`artifacts/v1/README.md`](artifacts/v1/README.md) for the frozen evidence.

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
- A PyTorch TCN learns exercise identity from normalized landmark sequences.
- State machines count exercise phases and complete cycles.
- Evaluation reports Macro F1, per-class precision/recall/F1, confusion matrix,
  repetition MAE, exact-count accuracy, and off-by-one accuracy.

## Colab notebooks

The current rebuild uses seven small, sequential notebooks:

1. `01_colab_extract_workoutfitness.ipynb` converts selected Workout/Fitness videos to normalized 17-joint pose sequences.
2. `02_colab_prepare_mmfit.ipynb` converts the labeled MM-Fit exercise sets to the same representation.
3. `02b_colab_prepare_mmfit_unknown.ipynb` exports the unlabeled gaps between MM-Fit sets as `unknown` examples for rest and transitions.
4. `03_colab_train_tcn.ipynb` trains and evaluates the exercise TCN from all uploaded landmark ZIPs.
5. `04_colab_analyze_mixed_video.ipynb` downloads the versioned TCN v2 checkpoint, reruns the locked GainsByBrains test, and produces a smoothed timeline.
6. `05_colab_extract_youtube_mixed_landmarks.ipynb` downloads three reviewed long-form training videos and exports their labelled landmark segments.
7. `06_colab_extract_additional_youtube_landmarks.ipynb` processes the three earlier reviewed YouTube training videos that were missing from TCN v2, adding 111 segments without touching the locked tests.

Notebook 03 downloads all four versioned landmark ZIPs from GitHub by default.
Notebook 04 expects the report ZIP produced by notebook 03; its `tcn_model.pt`
contains the class list and model weights.

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
