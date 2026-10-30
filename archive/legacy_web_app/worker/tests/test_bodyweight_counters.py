from analysis.exercises import LungeCounter, MountainClimberCounter, PullUpCounter, SitUpCounter


def test_pull_up_and_sit_up_cycles():
    pull = PullUpCounter()
    sit = SitUpCounter()
    for angle in [165, 70, 165, 70, 165]:
        pull.update({"elbow_angle": angle})
    for angle in [150, 70, 150, 70, 150]:
        sit.update({"hip_angle": angle})
    assert pull.repetitions == 2
    assert sit.repetitions == 2


def test_lunge_and_mountain_climber_cycles():
    lunge = LungeCounter()
    climber = MountainClimberCounter()
    for left, right in [(165, 165), (95, 160), (165, 165), (160, 95), (165, 165)]:
        lunge.update({"left_knee_angle": left, "right_knee_angle": right})
    for left, right in [(80, 160), (160, 80), (80, 160), (160, 80)]:
        climber.update({"left_knee_angle": left, "right_knee_angle": right})
    assert lunge.repetitions == 2
    assert climber.repetitions == 3
