from analysis.quality import confidence_from_pose_ratio, quality_warnings


def test_confidence_uses_pose_ratio_and_repetitions():
    assert confidence_from_pose_ratio(0.9, 3) == "high"
    assert confidence_from_pose_ratio(0.7, 1) == "medium"
    assert confidence_from_pose_ratio(0.95, 0) == "low"


def test_low_visibility_produces_warning():
    warnings = quality_warnings(0.5, 2)
    assert any("visibility" in warning for warning in warnings)
