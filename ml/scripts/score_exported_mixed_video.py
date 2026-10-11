#!/usr/bin/env python3
"""Score notebook 04 window predictions against human timeline labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


BOUNDARY_GUARD_SECONDS = 3.0


def add_truth(predictions: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    ends = labels["end_s"].astype(float).to_numpy()
    truth_rows: list[dict] = []
    for center in predictions["center_s"].astype(float):
        index = int(ends.searchsorted(center, side="right"))
        index = min(index, len(labels) - 1)
        label = labels.iloc[index]
        boundary_distance = min(center - float(label.start_s), float(label.end_s) - center)
        truth_rows.append(
            {
                "true_class": label.current_tcn_label,
                "fine_label": label.fine_label,
                "segment_type": label.segment_type,
                "stable_interior": boundary_distance >= BOUNDARY_GUARD_SECONDS,
            }
        )
    return pd.concat([predictions.reset_index(drop=True), pd.DataFrame(truth_rows)], axis=1)


def metric_block(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"windows": 0, "accuracy": None, "balanced_accuracy": None, "macro_f1": None}

    truth = frame.true_class.astype(str)
    pred = frame.predicted_class.astype(str)
    labels = sorted(set(truth) | set(pred))
    accuracy = float((truth == pred).mean())
    recalls: list[float] = []
    f1s: list[float] = []
    for label in labels:
        tp = int(((truth == label) & (pred == label)).sum())
        fn = int(((truth == label) & (pred != label)).sum())
        fp = int(((truth != label) & (pred == label)).sum())
        recall = tp / (tp + fn) if tp + fn else 0.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        if tp + fn:
            recalls.append(recall)
        f1s.append(f1)
    return {
        "windows": int(len(frame)),
        "accuracy": accuracy,
        "balanced_accuracy": float(sum(recalls) / len(recalls)),
        "macro_f1": float(sum(f1s) / len(f1s)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    predictions = pd.read_csv(args.predictions)
    labels = pd.read_csv(args.annotations).sort_values("start_s").reset_index(drop=True)
    scored = add_truth(predictions, labels)
    scored.to_csv(args.output / "window_predictions_scored.csv", index=False)

    stable = scored[scored.stable_interior].copy()
    supported = stable[(stable.segment_type == "exercise") & (stable.true_class != "unknown")]
    unsupported = stable[(stable.segment_type == "exercise") & (stable.true_class == "unknown")]
    transitions = stable[stable.segment_type.isin(["transition", "intro", "outro"])]

    metrics = {
        "boundary_guard_seconds": BOUNDARY_GUARD_SECONDS,
        "all_windows": metric_block(scored),
        "stable_interior_windows": metric_block(stable),
        "supported_exercise_windows": metric_block(supported),
        "unsupported_exercise_rejection_rate": float((unsupported.predicted_class == "unknown").mean()),
        "unsupported_exercise_windows": int(len(unsupported)),
        "transition_rejection_rate": float((transitions.predicted_class == "unknown").mean()),
        "transition_windows": int(len(transitions)),
    }
    (args.output / "external_test_metrics.json").write_text(json.dumps(metrics, indent=2))

    class_names = sorted(set(stable.true_class.astype(str)) | set(stable.predicted_class.astype(str)))
    confusion = pd.crosstab(stable.true_class, stable.predicted_class).reindex(
        index=class_names, columns=class_names, fill_value=0
    )
    confusion.to_csv(args.output / "confusion_matrix.csv")

    rows = []
    for (fine_label, true_class), group in stable.groupby(["fine_label", "true_class"]):
        rows.append(
            {
                "fine_label": fine_label,
                "true_class": true_class,
                "windows": int(len(group)),
                "correct": int((group.predicted_class == group.true_class).sum()),
                "dominant_prediction": group.predicted_class.value_counts().index[0],
                "mean_confidence": float(group.confidence.mean()),
                "accuracy": float((group.predicted_class == group.true_class).mean()),
            }
        )
    per_movement = pd.DataFrame(rows).sort_values(["true_class", "fine_label"])
    per_movement.to_csv(args.output / "per_movement_results.csv", index=False)

    print(json.dumps(metrics, indent=2))
    print(per_movement.to_string(index=False))


if __name__ == "__main__":
    main()
