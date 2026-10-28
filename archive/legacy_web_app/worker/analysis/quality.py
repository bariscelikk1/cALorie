def confidence_from_pose_ratio(valid_pose_ratio: float, repetitions: int) -> str:
    if valid_pose_ratio >= 0.85 and repetitions >= 2:
        return "high"
    if valid_pose_ratio >= 0.60 and repetitions >= 1:
        return "medium"
    return "low"


def quality_warnings(valid_pose_ratio: float, repetitions: int) -> list[str]:
    warnings: list[str] = []
    if valid_pose_ratio < 0.75:
        warnings.append(
            "Pose visibility was low. Keep the whole body in frame with steady lighting."
        )
    if repetitions == 0:
        warnings.append(
            "No complete repetitions were counted; check the camera angle and movement range."
        )
    return warnings

