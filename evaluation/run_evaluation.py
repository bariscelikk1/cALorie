import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "worker"))

from analysis.models import Exercise  # noqa: E402
from analysis.pipeline import analyze_video  # noqa: E402


def run(manifest_path: Path, output_path: Path) -> None:
    fields = [
        "video_path", "exercise", "manual_repetitions", "predicted_repetitions",
        "repetition_error", "actual_duration_seconds", "detected_duration_seconds",
        "duration_error_seconds", "valid_pose_frame_ratio", "calories_estimated",
        "runtime_seconds", "status", "error",
    ]
    rows = []
    with manifest_path.open(newline="", encoding="utf-8") as source:
        for sample in csv.DictReader(source):
            started = time.perf_counter()
            row = {field: "" for field in fields}
            row.update({key: sample[key] for key in ("video_path", "exercise", "manual_repetitions", "actual_duration_seconds")})
            try:
                selected = None if sample["exercise"] == "auto" else Exercise(sample["exercise"])
                result = analyze_video(ROOT / sample["video_path"], selected, float(sample["weight_kg"]))
                manual = int(sample["manual_repetitions"])
                actual_duration = float(sample["actual_duration_seconds"])
                row.update({
                    "predicted_repetitions": sum(segment.repetitions for segment in result.segments),
                    "repetition_error": sum(segment.repetitions for segment in result.segments) - manual,
                    "detected_duration_seconds": result.duration_seconds,
                    "duration_error_seconds": round(result.duration_seconds - actual_duration, 3),
                    "valid_pose_frame_ratio": result.valid_pose_frame_ratio,
                    "calories_estimated": result.total_calories_estimated,
                    "status": "ok",
                })
            except Exception as exc:
                row.update({"status": "error", "error": str(exc)})
            row["runtime_seconds"] = round(time.perf_counter() - started, 3)
            rows.append(row)
    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    run(ROOT / "evaluation" / "manifest.csv", ROOT / "evaluation" / "results.csv")
