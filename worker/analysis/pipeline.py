from pathlib import Path

from .aggregation import aggregate_exercises, total_calories
from .calories import calorie_summary
from .classifier import classify_frame
from .errors import PoseNotDetectedError
from .exercises import JumpingJackCounter, PushUpCounter, SquatCounter
from .features import extract_features
from .intensity import classify_intensity
from .models import Activity, Exercise, FrameFeatures, MultiAnalysisResult, SegmentResult
from .pose import extract_pose_landmarks
from .quality import confidence_from_pose_ratio, quality_warnings
from .segmentation import FrameLabel, TimelineSegment, build_segments, smooth_labels
from .video import frames, read_metadata


def _counter(exercise: Exercise):
    return {
        Exercise.SQUAT: SquatCounter,
        Exercise.JUMPING_JACK: JumpingJackCounter,
        Exercise.PUSH_UP: PushUpCounter,
    }[exercise]()


def _counter_metrics(exercise: Exercise, feature: FrameFeatures) -> dict[str, float] | None:
    if not feature.valid:
        return None
    if exercise is Exercise.SQUAT and feature.knee_angle is not None:
        return {"knee_angle": feature.knee_angle}
    if exercise is Exercise.PUSH_UP and feature.elbow_angle is not None:
        return {"elbow_angle": feature.elbow_angle, "body_angle": feature.body_angle or 180.0}
    if exercise is Exercise.JUMPING_JACK:
        return {
            "wrist_above_shoulder": 1.0 if feature.wrists_up else 0.0,
            "ankle_to_shoulder_ratio": feature.ankle_to_shoulder_ratio,
        }
    return None


def _exercise_segment(
    segment: TimelineSegment,
    features: list[FrameFeatures],
    weight_kg: float,
    valid_pose_ratio: float,
) -> SegmentResult:
    if segment.activity in {Activity.IDLE, Activity.UNKNOWN}:
        return SegmentResult(
            exercise=segment.activity.value,
            start_seconds=round(segment.start_seconds, 2),
            end_seconds=round(segment.end_seconds, 2),
            duration_seconds=round(segment.duration_seconds, 2),
            repetitions=None,
            repetitions_per_minute=None,
            intensity=None,
            met_value=None,
            calories_estimated=0.0,
            calories_low=0.0,
            calories_high=0.0,
            confidence="high" if segment.confidence >= 0.8 else "medium" if segment.confidence >= 0.6 else "low",
            warnings=[],
        )
    exercise = Exercise(segment.activity.value)
    counter = _counter(exercise)
    valid = 0
    for feature in features[segment.start_index:segment.end_index]:
        metrics = _counter_metrics(exercise, feature)
        if metrics is not None:
            valid += 1
            counter.update(metrics)
    duration = segment.duration_seconds
    rpm = counter.repetitions / (duration / 60) if duration > 0 else 0.0
    intensity = classify_intensity(exercise, rpm)
    segment_pose_ratio = valid / max(1, segment.end_index - segment.start_index)
    confidence = confidence_from_pose_ratio(min(valid_pose_ratio, segment_pose_ratio), counter.repetitions)
    met, estimated, low, high = calorie_summary(exercise, intensity, weight_kg, duration, confidence)
    return SegmentResult(
        exercise=exercise.value,
        start_seconds=round(segment.start_seconds, 2),
        end_seconds=round(segment.end_seconds, 2),
        duration_seconds=round(duration, 2),
        repetitions=counter.repetitions,
        repetitions_per_minute=round(rpm, 1),
        intensity=intensity.value,
        met_value=met,
        calories_estimated=estimated,
        calories_low=low,
        calories_high=high,
        confidence=confidence,
        warnings=quality_warnings(segment_pose_ratio, counter.repetitions),
    )


def analyze_feature_sequence(
    features: list[FrameFeatures],
    fps: float,
    duration_seconds: float,
    weight_kg: float,
    selected_exercise: Exercise | None = None,
) -> MultiAnalysisResult:
    valid_count = sum(feature.valid for feature in features)
    ratio = valid_count / len(features) if features else 0.0
    if not features or ratio < 0.15:
        raise PoseNotDetectedError("A person could not be detected reliably. Keep the full body visible.")
    if selected_exercise:
        labels = [FrameLabel(
            feature.timestamp,
            Activity(selected_exercise.value) if feature.valid else Activity.UNKNOWN,
            1.0 if feature.valid else 0.0,
        ) for feature in features]
    else:
        labels = [FrameLabel(feature.timestamp, *classify_frame(feature)) for feature in features]
        labels = smooth_labels(labels, fps)
    timeline = build_segments(labels, fps, duration_seconds)
    results = [_exercise_segment(segment, features, weight_kg, ratio) for segment in timeline]
    estimated, low, high = total_calories(results)
    unknown_duration = sum(
        segment.duration_seconds for segment in results if segment.exercise == Activity.UNKNOWN.value
    )
    completed_reps = sum(segment.repetitions or 0 for segment in results)
    overall_confidence = confidence_from_pose_ratio(ratio, completed_reps)
    warnings = quality_warnings(ratio, completed_reps)
    if unknown_duration / duration_seconds > 0.2:
        warnings.append("A substantial part of the video could not be classified reliably.")
    return MultiAnalysisResult(
        duration_seconds=round(duration_seconds, 2),
        total_calories_estimated=estimated,
        total_calories_low=low,
        total_calories_high=high,
        overall_confidence=overall_confidence,
        valid_pose_frame_ratio=round(ratio, 3),
        frames_analyzed=len(features),
        segments=results,
        exercise_totals=aggregate_exercises(results),
        unknown_duration_seconds=round(unknown_duration, 2),
        warnings=warnings,
    )


def analyze_video(
    path: str | Path,
    selected_exercise: Exercise | None,
    weight_kg: float,
) -> MultiAnalysisResult:
    metadata = read_metadata(path)
    extracted: list[FrameFeatures] = []
    previous_landmarks = None
    previous_features = None
    delta = 1 / metadata.fps
    for frame_index, landmarks in enumerate(extract_pose_landmarks(frames(path))):
        feature = extract_features(
            landmarks,
            frame_index / metadata.fps,
            previous_landmarks,
            previous_features,
            delta,
        )
        extracted.append(feature)
        if landmarks is not None:
            previous_landmarks = landmarks
        if feature.valid:
            previous_features = feature
    return analyze_feature_sequence(
        extracted, metadata.fps, metadata.duration_seconds, weight_kg, selected_exercise
    )
