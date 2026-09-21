from dataclasses import asdict, dataclass, field
from enum import Enum


class Exercise(str, Enum):
    SQUAT = "squat"
    JUMPING_JACK = "jumping_jack"
    PUSH_UP = "push_up"
    PULL_UP = "pull_up"
    LUNGE = "lunge"
    SIT_UP = "sit_up"
    MOUNTAIN_CLIMBER = "mountain_climber"
    BURPEE = "burpee"
    PLANK = "plank"


class Activity(str, Enum):
    SQUAT = "squat"
    JUMPING_JACK = "jumping_jack"
    PUSH_UP = "push_up"
    PULL_UP = "pull_up"
    LUNGE = "lunge"
    SIT_UP = "sit_up"
    MOUNTAIN_CLIMBER = "mountain_climber"
    BURPEE = "burpee"
    PLANK = "plank"
    IDLE = "idle"
    UNKNOWN = "unknown"


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


@dataclass(frozen=True)
class FrameFeatures:
    timestamp: float
    valid: bool
    knee_angle: float | None = None
    elbow_angle: float | None = None
    body_angle: float | None = None
    torso_horizontal: bool = False
    wrists_up: bool = False
    ankle_to_shoulder_ratio: float = 0.0
    motion: float = 0.0
    knee_velocity: float = 0.0
    elbow_velocity: float = 0.0
    left_knee_angle: float | None = None
    right_knee_angle: float | None = None
    hip_angle: float | None = None
    knee_asymmetry: float = 0.0


@dataclass
class SegmentResult:
    exercise: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    repetitions: int | None
    repetitions_per_minute: float | None
    intensity: str | None
    met_value: float | None
    calories_estimated: float
    calories_low: float
    calories_high: float
    confidence: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class MultiAnalysisResult:
    duration_seconds: float
    total_calories_estimated: float
    total_calories_low: float
    total_calories_high: float
    overall_confidence: str
    valid_pose_frame_ratio: float
    frames_analyzed: int
    segments: list[SegmentResult]
    exercise_totals: dict[str, dict]
    unknown_duration_seconds: float
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
