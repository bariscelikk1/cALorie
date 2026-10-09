# cALorie ML

This directory contains the local, dataset-driven rebuild of cALorie. The
primary task is 15-class workout recognition from temporal pose landmarks, with
an additional `unknown` class. Exercise-specific state machines count complete
repetitions; plank is measured by duration.

## Verified progress

The Colab landmark pipeline in
[`notebooks/01_colab_tasks_extract_landmarks.ipynb`](notebooks/01_colab_tasks_extract_landmarks.ipynb)
has completed a 14-video smoke test across bicep curl, lateral raise, plank,
pull-up, push-up, shoulder press, and squat. All 14 clips produced normalized
17-joint pose sequences; the minimum detected-frame ratio was 95.8%. This test
validates the extraction and transfer format only. It is not a training result
or an accuracy claim.

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

The current rebuild uses five small, sequential notebooks:

1. `01_colab_extract_workoutfitness.ipynb` converts selected Workout/Fitness videos to normalized 17-joint pose sequences.
2. `02_colab_prepare_mmfit.ipynb` converts the labeled MM-Fit exercise sets to the same representation.
3. `02b_colab_prepare_mmfit_unknown.ipynb` exports the unlabeled gaps between MM-Fit sets as `unknown` examples for rest and transitions.
4. `03_colab_train_tcn.ipynb` trains and evaluates the exercise TCN from all uploaded landmark ZIPs.
5. `04_colab_analyze_mixed_video.ipynb` runs the trained model over a long mixed-workout video and produces a smoothed timeline.

For the final mixed-video model, upload all three landmark ZIPs to notebook 03. Notebook 04 expects the report ZIP produced by notebook 03; its `tcn_model.pt` contains the class list and model weights.
