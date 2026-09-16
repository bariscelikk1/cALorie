from abc import ABC, abstractmethod


class RepetitionCounter(ABC):
    """Small state machine shared by all exercise counters."""

    def __init__(self) -> None:
        self.repetitions = 0
        self.stage = "unknown"
        self.valid_updates = 0

    @abstractmethod
    def update(self, metrics: dict[str, float]) -> None:
        """Consume one frame's exercise-specific measurements."""

