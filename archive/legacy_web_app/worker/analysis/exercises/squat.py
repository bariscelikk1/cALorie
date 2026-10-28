from .base import RepetitionCounter


class SquatCounter(RepetitionCounter):
    STANDING_ANGLE = 155.0
    LOWERED_ANGLE = 105.0

    def update(self, metrics: dict[str, float]) -> None:
        angle = metrics["knee_angle"]
        self.valid_updates += 1
        if angle >= self.STANDING_ANGLE:
            if self.stage == "lowered":
                self.repetitions += 1
            self.stage = "standing"
        elif angle <= self.LOWERED_ANGLE and self.stage in {"standing", "unknown"}:
            self.stage = "lowered"

