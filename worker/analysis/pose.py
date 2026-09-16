from collections.abc import Iterator

import cv2
import mediapipe as mp

from .models import Point

Landmarks = dict[str, Point]

_NAMES = {
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
    "left_knee": 25,
    "right_knee": 26,
    "left_ankle": 27,
    "right_ankle": 28,
}


def extract_pose_landmarks(video_frames: Iterator) -> Iterator[Landmarks | None]:
    pose_module = mp.solutions.pose
    with pose_module.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        for frame in video_frames:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = pose.process(rgb)
            if not result.pose_landmarks:
                yield None
                continue
            source = result.pose_landmarks.landmark
            yield {
                name: Point(source[index].x, source[index].y, source[index].visibility)
                for name, index in _NAMES.items()
            }

