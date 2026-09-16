from .config import MIN_VISIBILITY
from .geometry import distance, joint_angle, mean
from .models import FrameFeatures, Point
from .pose import Landmarks


def _visible(points: list[Point]) -> bool:
    return all(point.visibility >= MIN_VISIBILITY for point in points)


def _best_angle(landmarks: Landmarks, triplets: list[tuple[str, str, str]]) -> float | None:
    candidates: list[tuple[float, float]] = []
    for names in triplets:
        points = [landmarks[name] for name in names]
        if _visible(points):
            candidates.append((mean([p.visibility for p in points]), joint_angle(*points)))
    return max(candidates, default=(0.0, None), key=lambda item: item[0])[1]


def extract_features(
    landmarks: Landmarks | None,
    timestamp: float,
    previous_landmarks: Landmarks | None = None,
    previous_features: FrameFeatures | None = None,
    delta_seconds: float = 0.0,
) -> FrameFeatures:
    if landmarks is None:
        return FrameFeatures(timestamp=timestamp, valid=False)
    required = [
        landmarks[name]
        for name in ("left_shoulder", "right_shoulder", "left_hip", "right_hip")
    ]
    if not _visible(required):
        return FrameFeatures(timestamp=timestamp, valid=False)
    knee = _best_angle(landmarks, [
        ("left_hip", "left_knee", "left_ankle"),
        ("right_hip", "right_knee", "right_ankle"),
    ])
    elbow = _best_angle(landmarks, [
        ("left_shoulder", "left_elbow", "left_wrist"),
        ("right_shoulder", "right_elbow", "right_wrist"),
    ])
    body = _best_angle(landmarks, [
        ("left_shoulder", "left_hip", "left_ankle"),
        ("right_shoulder", "right_hip", "right_ankle"),
    ])
    shoulder_mid = Point(
        mean([landmarks["left_shoulder"].x, landmarks["right_shoulder"].x]),
        mean([landmarks["left_shoulder"].y, landmarks["right_shoulder"].y]),
    )
    hip_mid = Point(
        mean([landmarks["left_hip"].x, landmarks["right_hip"].x]),
        mean([landmarks["left_hip"].y, landmarks["right_hip"].y]),
    )
    torso_horizontal = abs(shoulder_mid.x - hip_mid.x) > abs(shoulder_mid.y - hip_mid.y)
    shoulder_width = distance(landmarks["left_shoulder"], landmarks["right_shoulder"])
    ankle_ratio = 0.0 if shoulder_width < 0.02 else distance(
        landmarks["left_ankle"], landmarks["right_ankle"]
    ) / shoulder_width
    wrists_up = (
        landmarks["left_wrist"].y < landmarks["left_shoulder"].y
        and landmarks["right_wrist"].y < landmarks["right_shoulder"].y
    )
    motion = 0.0
    if previous_landmarks:
        names = ("left_wrist", "right_wrist", "left_ankle", "right_ankle", "left_hip", "right_hip")
        motion = mean([distance(landmarks[name], previous_landmarks[name]) for name in names])
    knee_velocity = 0.0
    elbow_velocity = 0.0
    if previous_features and delta_seconds > 0:
        if knee is not None and previous_features.knee_angle is not None:
            knee_velocity = abs(knee - previous_features.knee_angle) / delta_seconds
        if elbow is not None and previous_features.elbow_angle is not None:
            elbow_velocity = abs(elbow - previous_features.elbow_angle) / delta_seconds
    return FrameFeatures(
        timestamp=timestamp,
        valid=True,
        knee_angle=knee,
        elbow_angle=elbow,
        body_angle=body,
        torso_horizontal=torso_horizontal,
        wrists_up=wrists_up,
        ankle_to_shoulder_ratio=ankle_ratio,
        motion=motion,
        knee_velocity=knee_velocity,
        elbow_velocity=elbow_velocity,
    )
