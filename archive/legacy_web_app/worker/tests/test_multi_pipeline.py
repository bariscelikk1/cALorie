from analysis.models import Exercise, FrameFeatures
from analysis.pipeline import analyze_feature_sequence


def squat_feature(timestamp, angle):
    return FrameFeatures(timestamp, True, knee_angle=angle, body_angle=175, motion=.02, knee_velocity=20)


def push_feature(timestamp, angle):
    return FrameFeatures(timestamp, True, elbow_angle=angle, body_angle=175, torso_horizontal=True, motion=.02, elbow_velocity=20)


def test_manual_mode_remains_supported():
    angles = [170, 95, 170] * 10
    features = [squat_feature(index / 10, angle) for index, angle in enumerate(angles)]
    result = analyze_feature_sequence(features, 10, 3, 70, Exercise.SQUAT)
    assert result.exercise_totals["squat"]["repetitions"] == 10


def test_automatic_squat_rest_push_up_integration():
    features = []
    for index, angle in enumerate(([170, 95, 170] * 7)):
        features.append(squat_feature(index / 10, angle))
    offset = len(features)
    for index in range(12):
        features.append(FrameFeatures((offset + index) / 10, True, knee_angle=175, motion=0))
    offset = len(features)
    for index, angle in enumerate(([170, 90, 170] * 7)):
        features.append(push_feature((offset + index) / 10, angle))
    result = analyze_feature_sequence(features, 10, len(features) / 10, 70)
    exercises = [segment.exercise for segment in result.segments]
    assert "squat" in exercises
    assert "idle" in exercises
    assert "push_up" in exercises
    assert result.total_calories_estimated > 0
