from dataclasses import dataclass
from collections import Counter

from .config import MERGE_GAP_SECONDS, MIN_SEGMENT_SECONDS, MISSING_POSE_GRACE_SECONDS, SMOOTHING_WINDOW_SECONDS
from .models import Activity


@dataclass
class FrameLabel:
    timestamp: float
    activity: Activity
    confidence: float


@dataclass
class TimelineSegment:
    activity: Activity
    start_index: int
    end_index: int
    start_seconds: float
    end_seconds: float
    confidence: float

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


def smooth_labels(labels: list[FrameLabel], fps: float) -> list[FrameLabel]:
    if not labels:
        return []
    radius = max(1, round(SMOOTHING_WINDOW_SECONDS * fps / 2))
    grace = max(1, round(MISSING_POSE_GRACE_SECONDS * fps))
    output: list[FrameLabel] = []
    for index, label in enumerate(labels):
        window_start = max(0, index - radius)
        window = labels[window_start: min(len(labels), index + radius + 1)]
        usable = [item for item in window if item.activity is not Activity.UNKNOWN]
        if label.activity is Activity.UNKNOWN and usable:
            nearest_known = min(
                abs(index - (window_start + offset))
                for offset, item in enumerate(window)
                if item.activity is not Activity.UNKNOWN
            )
            if nearest_known <= grace:
                winner = Counter(item.activity for item in usable).most_common(1)[0][0]
                confidence = sum(item.confidence for item in usable if item.activity is winner) / max(
                    1, sum(item.activity is winner for item in usable)
                )
                output.append(FrameLabel(label.timestamp, winner, confidence * 0.8))
                continue
        winner = Counter(item.activity for item in window).most_common(1)[0][0]
        winner_items = [item for item in window if item.activity is winner]
        confidence = sum(item.confidence for item in winner_items) / len(winner_items)
        output.append(FrameLabel(label.timestamp, winner, confidence))
    return output


def build_segments(labels: list[FrameLabel], fps: float, duration_seconds: float) -> list[TimelineSegment]:
    if not labels:
        return []
    segments: list[TimelineSegment] = []
    start = 0
    for index in range(1, len(labels) + 1):
        if index < len(labels) and labels[index].activity is labels[start].activity:
            continue
        end_seconds = labels[index].timestamp if index < len(labels) else duration_seconds
        portion = labels[start:index]
        segments.append(TimelineSegment(
            activity=labels[start].activity,
            start_index=start,
            end_index=index,
            start_seconds=labels[start].timestamp,
            end_seconds=end_seconds,
            confidence=sum(item.confidence for item in portion) / len(portion),
        ))
        start = index
    return normalize_segments(segments, fps)


def normalize_segments(segments: list[TimelineSegment], fps: float) -> list[TimelineSegment]:
    minimum = max(MIN_SEGMENT_SECONDS, 1 / fps)
    for segment in segments:
        if segment.duration_seconds < minimum and segment.activity not in {Activity.UNKNOWN, Activity.IDLE}:
            segment.activity = Activity.UNKNOWN

    changed = True
    while changed and len(segments) >= 3:
        changed = False
        merged: list[TimelineSegment] = []
        index = 0
        while index < len(segments):
            if index + 2 < len(segments):
                left, gap, right = segments[index:index + 3]
                if (
                    left.activity is right.activity
                    and gap.activity in {Activity.IDLE, Activity.UNKNOWN}
                    and gap.duration_seconds <= MERGE_GAP_SECONDS
                ):
                    merged.append(TimelineSegment(
                        left.activity, left.start_index, right.end_index,
                        left.start_seconds, right.end_seconds,
                        (left.confidence + right.confidence) / 2,
                    ))
                    index += 3
                    changed = True
                    continue
            merged.append(segments[index])
            index += 1
        segments = merged

    compact: list[TimelineSegment] = []
    for segment in segments:
        if compact and compact[-1].activity is segment.activity:
            previous = compact[-1]
            previous.end_index = segment.end_index
            previous.end_seconds = segment.end_seconds
            previous.confidence = (previous.confidence + segment.confidence) / 2
        else:
            compact.append(segment)
    return compact
