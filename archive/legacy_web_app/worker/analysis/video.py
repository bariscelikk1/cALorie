from pathlib import Path

import cv2

from .errors import InvalidVideoError
from .models import VideoMetadata

MAX_DURATION_SECONDS = 180


def read_metadata(path: str | Path) -> VideoMetadata:
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise InvalidVideoError("The uploaded file could not be opened as a video.")
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
            raise InvalidVideoError("The video metadata is missing or invalid.")
        duration = frame_count / fps
        if duration > MAX_DURATION_SECONDS:
            raise InvalidVideoError(
                f"The video is too long. The limit is {MAX_DURATION_SECONDS} seconds."
            )
        return VideoMetadata(fps, frame_count, duration, width, height)
    finally:
        capture.release()


def frames(path: str | Path):
    capture = cv2.VideoCapture(str(path))
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            yield frame
    finally:
        capture.release()

