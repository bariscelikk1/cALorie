import pytest

from analysis.calories import calorie_summary, estimate_calories
from analysis.models import Exercise, Intensity


def test_met_formula():
    assert estimate_calories(5, 70, 60) == pytest.approx(6.125)


@pytest.mark.parametrize("weight", [0, 29.9, 250.1])
def test_invalid_weight(weight):
    with pytest.raises(ValueError):
        estimate_calories(5, weight, 60)


def test_summary_range_surrounds_estimate():
    met, estimate, low, high = calorie_summary(
        Exercise.SQUAT, Intensity.MODERATE, 70, 60, "high"
    )
    assert met == 5.0
    assert low < estimate < high
