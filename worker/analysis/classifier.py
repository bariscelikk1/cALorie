from .config import JOINT_VELOCITY_ACTIVE_THRESHOLD, MIN_LABEL_SCORE, MOTION_IDLE_THRESHOLD
from .models import Activity, FrameFeatures


def activity_scores(features: FrameFeatures) -> dict[Activity, float]:
    if not features.valid:
        return {Activity.UNKNOWN: 1.0}
    scores = {activity: 0.0 for activity in Activity}
    if features.motion < MOTION_IDLE_THRESHOLD and max(
        features.knee_velocity, features.elbow_velocity
    ) < JOINT_VELOCITY_ACTIVE_THRESHOLD:
        scores[Activity.IDLE] = 0.72
    if features.torso_horizontal and (features.body_angle or 0) >= 150 and features.motion < MOTION_IDLE_THRESHOLD:
        scores[Activity.PLANK] = 0.88
    if features.torso_horizontal and (features.body_angle or 0) >= 145:
        scores[Activity.PUSH_UP] = 0.62
        if features.elbow_velocity >= JOINT_VELOCITY_ACTIVE_THRESHOLD:
            scores[Activity.PUSH_UP] += 0.28
    if features.torso_horizontal and features.knee_asymmetry >= 30 and features.motion >= MOTION_IDLE_THRESHOLD:
        scores[Activity.MOUNTAIN_CLIMBER] = 0.91
    if features.torso_horizontal and features.hip_angle is not None and features.hip_angle < 135:
        scores[Activity.SIT_UP] = 0.84
    if not features.torso_horizontal and features.knee_angle is not None:
        if features.knee_asymmetry >= 30 and features.knee_angle <= 145:
            scores[Activity.LUNGE] = 0.88
        elif features.knee_angle <= 150:
            scores[Activity.SQUAT] = 0.72
        elif features.knee_velocity >= JOINT_VELOCITY_ACTIVE_THRESHOLD:
            scores[Activity.SQUAT] = 0.62
    if features.wrists_up and features.ankle_to_shoulder_ratio >= 1.25:
        scores[Activity.JUMPING_JACK] = 0.92
    elif features.ankle_to_shoulder_ratio >= 1.05 and features.motion >= MOTION_IDLE_THRESHOLD:
        scores[Activity.JUMPING_JACK] = 0.60
    if features.wrists_up and features.ankle_to_shoulder_ratio < 1.15 and features.elbow_angle is not None:
        scores[Activity.PULL_UP] = 0.90 if features.elbow_velocity >= JOINT_VELOCITY_ACTIVE_THRESHOLD else 0.66
    if (features.knee_angle or 180) < 120 and features.elbow_velocity > 10 and features.motion > 0.04:
        scores[Activity.BURPEE] = 0.80
    scores[Activity.UNKNOWN] = 0.25
    return scores


def classify_frame(features: FrameFeatures) -> tuple[Activity, float]:
    scores = activity_scores(features)
    activity, score = max(scores.items(), key=lambda item: item[1])
    if score < MIN_LABEL_SCORE:
        return Activity.UNKNOWN, score
    return activity, min(score, 1.0)
