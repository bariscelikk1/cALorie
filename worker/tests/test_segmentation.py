from analysis.models import Activity
from analysis.segmentation import FrameLabel, TimelineSegment, build_segments, normalize_segments, smooth_labels


def labels(activity, count, start=0, fps=10):
    return [FrameLabel((start + index) / fps, activity, .9) for index in range(count)]


def test_short_exercise_segment_becomes_unknown():
    result = build_segments(labels(Activity.SQUAT, 5), 10, .5)
    assert result[0].activity is Activity.UNKNOWN


def test_brief_unknown_gap_merges_same_exercise_sets():
    segments = [
        TimelineSegment(Activity.SQUAT, 0, 20, 0, 2, .9),
        TimelineSegment(Activity.UNKNOWN, 20, 25, 2, 2.5, .2),
        TimelineSegment(Activity.SQUAT, 25, 45, 2.5, 4.5, .9),
    ]
    result = normalize_segments(segments, 10)
    assert len(result) == 1
    assert result[0].activity is Activity.SQUAT


def test_smoothing_bridges_brief_missing_pose():
    sequence = labels(Activity.SQUAT, 10) + labels(Activity.UNKNOWN, 2, 10) + labels(Activity.SQUAT, 10, 12)
    result = smooth_labels(sequence, 10)
    assert all(item.activity is Activity.SQUAT for item in result)


def test_multi_exercise_sequence_preserves_transitions():
    sequence = labels(Activity.SQUAT, 20) + labels(Activity.IDLE, 15, 20) + labels(Activity.PUSH_UP, 20, 35)
    result = build_segments(sequence, 10, 5.5)
    assert [segment.activity for segment in result] == [Activity.SQUAT, Activity.IDLE, Activity.PUSH_UP]

