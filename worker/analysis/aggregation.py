from collections import defaultdict

from .models import SegmentResult


def aggregate_exercises(segments: list[SegmentResult]) -> dict[str, dict]:
    totals = defaultdict(lambda: {"sets": 0, "repetitions": 0, "duration_seconds": 0.0, "calories_estimated": 0.0})
    for segment in segments:
        if segment.repetitions is None:
            continue
        item = totals[segment.exercise]
        item["sets"] += 1
        item["repetitions"] += segment.repetitions
        item["duration_seconds"] += segment.duration_seconds
        item["calories_estimated"] += segment.calories_estimated
    return {
        exercise: {
            "sets": values["sets"],
            "repetitions": values["repetitions"],
            "duration_seconds": round(values["duration_seconds"], 2),
            "calories_estimated": round(values["calories_estimated"], 2),
        }
        for exercise, values in totals.items()
    }


def total_calories(segments: list[SegmentResult]) -> tuple[float, float, float]:
    return tuple(round(sum(getattr(segment, field) for segment in segments), 2) for field in (
        "calories_estimated", "calories_low", "calories_high"
    ))
