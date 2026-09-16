from pathlib import Path

from .calories import calorie_summary
from .errors import PoseNotDetectedError
from .exercises import JumpingJackCounter, PushUpCounter, SquatCounter
from .geometry import distance, joint_angle, mean
from .intensity import classify_intensity
from .models import AnalysisResult, Exercise, Point
from .pose import Landmarks, extract_pose_landmarks
from .quality import confidence_from_pose_ratio, quality_warnings
from .video import frames, read_metadata

MIN_VISIBILITY = 0.55


def _visible(points: list[Point]) -> bool:
    return all(point.visibility >= MIN_VISIBILITY for point in points)


def _side_angle(landmarks: Landmarks, joint: str) -> float | None:
    if joint == "knee":
        triplets = [
            ("left_hip", "left_knee", "left_ankle"),
            ("right_hip", "right_knee", "right_ankle"),
        ]
    elif joint == "elbow":
        triplets = [
            ("left_shoulder", "left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow", "right_wrist"),
        ]
    else:
        raise ValueError(f"Unsupported joint: {joint}")
    candidates = []
    for names in triplets:
        points = [landmarks[name] for name in names]
        if _visible(points):
            candidates.append((mean([p.visibility for p in points]), joint_angle(*points)))
    return max(candidates, default=(0.0, None), key=lambda item: item[0])[1]


def _metrics(exercise: Exercise, landmarks: Landmarks) -> dict[str, float] | None:
    if exercise is Exercise.SQUAT:
        angle = _side_angle(landmarks, "knee")
        return {"knee_angle": angle} if angle is not None else None

    if exercise is Exercise.PUSH_UP:
        elbow = _side_angle(landmarks, "elbow")
        body_candidates = []
        for side in ("left", "right"):
            points = [
                landmarks[f"{side}_shoulder"],
                landmarks[f"{side}_hip"],
                landmarks[f"{side}_ankle"],
            ]
            if _visible(points):
                body_candidates.append(joint_angle(*points))
        if elbow is None or not body_candidates:
            return None
        return {"elbow_angle": elbow, "body_angle": max(body_candidates)}

    required = [
        landmarks[name]
        for name in (
            "left_wrist",
            "right_wrist",
            "left_shoulder",
            "right_shoulder",
            "left_ankle",
            "right_ankle",
        )
    ]
    if not _visible(required):
        return None
    shoulder_width = distance(landmarks["left_shoulder"], landmarks["right_shoulder"])
    if shoulder_width < 0.02:
        return None
    wrists_up = (
        landmarks["left_wrist"].y < landmarks["left_shoulder"].y
        and landmarks["right_wrist"].y < landmarks["right_shoulder"].y
    )
    ankle_width = distance(landmarks["left_ankle"], landmarks["right_ankle"])
    return {
        "wrist_above_shoulder": 1.0 if wrists_up else 0.0,
        "ankle_to_shoulder_ratio": ankle_width / shoulder_width,
    }


def analyze_video(path: str | Path, exercise: Exercise, weight_kg: float) -> AnalysisResult:
    metadata = read_metadata(path)
    counter = {
        Exercise.SQUAT: SquatCounter,
        Exercise.JUMPING_JACK: JumpingJackCounter,
        Exercise.PUSH_UP: PushUpCounter,
    }[exercise]()
    analyzed = 0
    valid = 0
    for landmarks in extract_pose_landmarks(frames(path)):
        analyzed += 1
        if landmarks is None:
            continue
        metrics = _metrics(exercise, landmarks)
        if metrics is None:
            continue
        valid += 1
        counter.update(metrics)

    ratio = valid / analyzed if analyzed else 0.0
    if analyzed == 0:
        raise PoseNotDetectedError("No readable frames were found in the video.")
    if ratio < 0.15:
        raise PoseNotDetectedError(
            "A person could not be detected reliably. Keep the full body visible."
        )

    rpm = counter.repetitions / (metadata.duration_seconds / 60.0)
    intensity = classify_intensity(exercise, rpm)
    confidence = confidence_from_pose_ratio(ratio, counter.repetitions)
    met, estimated, low, high = calorie_summary(
        exercise, intensity, weight_kg, metadata.duration_seconds, confidence
    )
    return AnalysisResult(
        exercise=exercise.value,
        duration_seconds=round(metadata.duration_seconds, 2),
        repetitions=counter.repetitions,
        repetitions_per_minute=round(rpm, 1),
        intensity=intensity.value,
        met_value=met,
        calories_estimated=estimated,
        calories_low=low,
        calories_high=high,
        confidence=confidence,
        frames_analyzed=analyzed,
        valid_pose_frame_ratio=round(ratio, 3),
        warnings=quality_warnings(ratio, counter.repetitions),
    )

