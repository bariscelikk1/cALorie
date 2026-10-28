import pytest

from analysis.features import extract_features
from analysis.models import Point


def landmarks():
    return {
        "left_shoulder": Point(0.4, 0.2), "right_shoulder": Point(0.6, 0.2),
        "left_elbow": Point(0.35, 0.4), "right_elbow": Point(0.65, 0.4),
        "left_wrist": Point(0.3, 0.6), "right_wrist": Point(0.7, 0.6),
        "left_hip": Point(0.45, 0.5), "right_hip": Point(0.55, 0.5),
        "left_knee": Point(0.45, 0.7), "right_knee": Point(0.55, 0.7),
        "left_ankle": Point(0.4, 0.9), "right_ankle": Point(0.6, 0.9),
    }


def test_feature_distances_are_normalized_by_shoulder_width():
    feature = extract_features(landmarks(), 0)
    assert feature.valid
    assert feature.ankle_to_shoulder_ratio == pytest.approx(1.0)
    assert feature.torso_horizontal is False


def test_missing_pose_produces_invalid_feature():
    assert extract_features(None, 0).valid is False

