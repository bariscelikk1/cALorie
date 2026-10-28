import pytest

from analysis.geometry import joint_angle
from analysis.models import Point


def test_joint_angle_right_angle():
    assert joint_angle(Point(1, 0), Point(0, 0), Point(0, 1)) == pytest.approx(90)


def test_joint_angle_straight_line():
    assert joint_angle(Point(-1, 0), Point(0, 0), Point(1, 0)) == pytest.approx(180)


def test_joint_angle_rejects_coincident_points():
    with pytest.raises(ValueError):
        joint_angle(Point(0, 0), Point(0, 0), Point(1, 0))
