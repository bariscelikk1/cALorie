from .base import RepetitionCounter


class PushUpCounter(RepetitionCounter):
    EXTENDED_ANGLE = 155.0
    LOWERED_ANGLE = 100.0

    def update(self, metrics: dict[str, float]) -> None:
        angle = metrics["elbow_angle"]
        body_angle = metrics.get("body_angle", 180.0)
        self.valid_updates += 1
        if body_angle < 145.0:
            return
        if angle >= self.EXTENDED_ANGLE:
            if self.stage == "lowered":
                self.repetitions += 1
            self.stage = "extended"
        elif angle <= self.LOWERED_ANGLE and self.stage in {"extended", "unknown"}:
            self.stage = "lowered"

