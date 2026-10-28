from analysis.intensity import classify_intensity
from analysis.models import Exercise, Intensity


def test_squat_intensity_boundaries():
    assert classify_intensity(Exercise.SQUAT, 10) is Intensity.LIGHT
    assert classify_intensity(Exercise.SQUAT, 20) is Intensity.MODERATE
    assert classify_intensity(Exercise.SQUAT, 30) is Intensity.VIGOROUS
