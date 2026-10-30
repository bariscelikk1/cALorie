from .base import RepetitionCounter


class JumpingJackCounter(RepetitionCounter):
    def update(self, metrics: dict[str, float]) -> None:
        arms_up = metrics["wrist_above_shoulder"] >= 0.5
        legs_open = metrics["ankle_to_shoulder_ratio"] >= 1.35
        closed = metrics["ankle_to_shoulder_ratio"] <= 0.9 and not arms_up
        self.valid_updates += 1
        if arms_up and legs_open:
            self.stage = "open"
        elif closed:
            if self.stage == "open":
                self.repetitions += 1
            self.stage = "closed"

