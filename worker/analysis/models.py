from dataclasses import asdict, dataclass, field
from enum import Enum


class Exercise(str, Enum):
    SQUAT = "squat"
    JUMPING_JACK = "jumping_jack"
    PUSH_UP = "push_up"


class Intensity(str, Enum):
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    visibility: float = 1.0


@dataclass(frozen=True)
class VideoMetadata:
    fps: float
    frame_count: int
    duration_seconds: float
    width: int
    height: int


@dataclass
class AnalysisResult:
    exercise: str
    duration_seconds: float
    repetitions: int
    repetitions_per_minute: float
    intensity: str
    met_value: float
    calories_estimated: float
    calories_low: float
    calories_high: float
    confidence: str
    frames_analyzed: int
    valid_pose_frame_ratio: float
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

