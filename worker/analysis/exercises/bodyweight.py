from .base import RepetitionCounter


class PullUpCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        self.valid_updates += 1
        angle = metrics["elbow_angle"]
        if angle <= 85:
            self.stage = "up"
        elif angle >= 150:
            if self.stage == "up":
                self.repetitions += 1
            self.stage = "down"


class LungeCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        self.valid_updates += 1
        low = min(metrics["left_knee_angle"], metrics["right_knee_angle"])
        if low <= 105:
            self.stage = "lowered"
        elif low >= 155:
            if self.stage == "lowered":
                self.repetitions += 1
            self.stage = "standing"


class SitUpCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        self.valid_updates += 1
        angle = metrics["hip_angle"]
        if angle <= 80:
            self.stage = "up"
        elif angle >= 135:
            if self.stage == "up":
                self.repetitions += 1
            self.stage = "down"


class MountainClimberCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        self.valid_updates += 1
        left, right = metrics["left_knee_angle"], metrics["right_knee_angle"]
        side = "left" if left + 25 < right else "right" if right + 25 < left else None
        if side and self.stage not in {side, "unknown"}:
            self.repetitions += 1
        if side:
            self.stage = side


class BurpeeCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        self.valid_updates += 1
        horizontal = metrics["torso_horizontal"] >= 0.5
        standing = metrics["knee_angle"] >= 150 and not horizontal
        if horizontal:
            self.stage = "floor"
        elif standing:
            if self.stage == "floor":
                self.repetitions += 1
            self.stage = "standing"
