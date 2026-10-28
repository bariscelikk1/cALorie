from analysis.exercises import JumpingJackCounter, PushUpCounter, SquatCounter


def test_squat_synthetic_sequence_counts_two_repetitions():
    counter = SquatCounter()
    for angle in [170, 140, 95, 120, 165, 145, 100, 130, 170]:
        counter.update({"knee_angle": angle})
    assert counter.repetitions == 2


def test_partial_squat_is_not_counted():
    counter = SquatCounter()
    for angle in [170, 140, 120, 165]:
        counter.update({"knee_angle": angle})
    assert counter.repetitions == 0


def test_jumping_jack_requires_arms_and_legs():
    counter = JumpingJackCounter()
    sequence = [(0, 0.7), (1, 1.5), (0, 0.7)]
    for arms, ratio in sequence:
        counter.update(
            {"wrist_above_shoulder": arms, "ankle_to_shoulder_ratio": ratio}
        )
    assert counter.repetitions == 1


def test_push_up_rejects_bent_body():
    counter = PushUpCounter()
    counter.update({"elbow_angle": 170, "body_angle": 175})
    counter.update({"elbow_angle": 90, "body_angle": 120})
    counter.update({"elbow_angle": 170, "body_angle": 175})
    assert counter.repetitions == 0


def test_push_up_counts_complete_cycle():
    counter = PushUpCounter()
    for elbow in [170, 130, 90, 120, 165]:
        counter.update({"elbow_angle": elbow, "body_angle": 175})
    assert counter.repetitions == 1
