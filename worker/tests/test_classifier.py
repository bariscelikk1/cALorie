from analysis.classifier import classify_frame
from analysis.models import Activity, FrameFeatures


def feature(**values):
    return FrameFeatures(timestamp=0, valid=True, **values)


def test_classifies_push_up_from_horizontal_body_and_elbow_motion():
    label, score = classify_frame(feature(torso_horizontal=True, body_angle=175, elbow_angle=90, elbow_velocity=30, motion=.02))
    assert label is Activity.PUSH_UP
    assert score >= .8


def test_classifies_open_jumping_jack():
    label, _ = classify_frame(feature(wrists_up=True, ankle_to_shoulder_ratio=1.6, motion=.02))
    assert label is Activity.JUMPING_JACK


def test_still_pose_is_idle_and_missing_pose_unknown():
    assert classify_frame(feature(knee_angle=175))[0] is Activity.IDLE
    assert classify_frame(FrameFeatures(timestamp=0, valid=False))[0] is Activity.UNKNOWN


def test_classifies_new_bodyweight_movements():
    assert classify_frame(feature(wrists_up=True, ankle_to_shoulder_ratio=.8, elbow_angle=75, elbow_velocity=20, motion=.02))[0] is Activity.PULL_UP
    assert classify_frame(feature(knee_angle=95, left_knee_angle=95, right_knee_angle=160, knee_asymmetry=65, motion=.02))[0] is Activity.LUNGE
    assert classify_frame(feature(torso_horizontal=True, hip_angle=75, body_angle=120, motion=.02))[0] is Activity.SIT_UP
    assert classify_frame(feature(torso_horizontal=True, body_angle=165, left_knee_angle=80, right_knee_angle=160, knee_asymmetry=80, motion=.02))[0] is Activity.MOUNTAIN_CLIMBER
    assert classify_frame(feature(torso_horizontal=True, body_angle=175, motion=0))[0] is Activity.PLANK
