from analysis.aggregation import aggregate_exercises, total_calories
from analysis.models import SegmentResult


def segment(exercise, reps, calories):
    return SegmentResult(exercise, 0, 10, 10, reps, 12 if reps is not None else None, "moderate" if reps is not None else None, 5 if reps is not None else None, calories, calories * .8, calories * 1.2, "medium")


def test_totals_ignore_idle_and_do_not_double_count():
    segments = [segment("squat", 4, 2), segment("idle", None, 0), segment("squat", 5, 3)]
    totals = aggregate_exercises(segments)
    assert totals["squat"]["sets"] == 2
    assert totals["squat"]["repetitions"] == 9
    assert total_calories(segments) == (5, 4, 6)

