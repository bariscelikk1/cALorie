import math

from .models import Point


def joint_angle(a: Point, vertex: Point, c: Point) -> float:
    """Return the smaller 0..180 degree angle at ``vertex``."""
    first = (a.x - vertex.x, a.y - vertex.y)
    second = (c.x - vertex.x, c.y - vertex.y)
    first_length = math.hypot(*first)
    second_length = math.hypot(*second)
    if first_length == 0 or second_length == 0:
        raise ValueError("Cannot calculate an angle from coincident points")
    cosine = (first[0] * second[0] + first[1] * second[1]) / (
        first_length * second_length
    )
    return math.degrees(math.acos(max(-1.0, min(1.0, cosine))))


def distance(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0

