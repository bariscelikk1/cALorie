# Labeling rules

## Unit of data

One manifest row represents one continuous clip containing one exercise or an
`unknown` period. Do not create several rows that point to overlapping time
ranges from the same source video unless the overlap is intentional and
documented.

## Exercise labels

The project supports exactly 15 exercises plus `unknown`. The canonical names
are stored in `config/classes.json`; dataset-specific names must be mapped to
those names before training.

- `squat`: standing, lowering the hips by bending both knees, then returning to standing.
- `push_up`: supported horizontally, lowering and raising the torso through elbow flexion.
- `jumping_jack`: arms and legs open and close together while jumping or stepping.
- `pull_up`: hanging movement that raises the torso by flexing the elbows and shoulders.
- `lunge`: split stance or alternating step with a lowered rear/front knee.
- `sit_up`: supine movement that raises the torso toward the legs.
- `bench_press`: supine press that moves a barbell or weights away from the chest and back.
- `deadlift`: standing hip-hinge that lifts a weight from a lowered position and returns it.
- `plank`: static supported horizontal posture; measure duration, not repetitions.
- `shoulder_press`: hands/weights press from shoulder level to overhead.
- `dumbbell_row`: bent or supported torso with elbow pulling the hand/weight toward the torso.
- `tricep_extension`: elbow extends against resistance while the upper arm stays comparatively stable.
- `bicep_curl`: elbow flexes to bring the hand/weight toward the shoulder.
- `lateral_raise`: arms rise laterally from the sides toward shoulder height.
- `lat_pulldown`: seated or kneeling pull that brings an overhead bar toward the upper torso.
- `unknown`: rest, transitions, unsupported exercise, incomplete setup, camera adjustment, or ambiguous motion.

## Repetition counting

Count only complete cycles. Record the visible count in `repetition_count`.
Use an empty value for plank and unknown clips. Do not guess when the beginning
or end of a repetition is outside the clip; add a note and exclude the partial
cycle.

## People and splits

`person_id` identifies the performer, not the video. A person may belong to
only one of `train`, `validation`, or `test`. All clips derived from the same
source video must remain in one split. Unknown person IDs are unacceptable for
the final evaluation set.

## Review status

Use one of:

- `pending`: imported but not manually checked.
- `approved`: label, person, time range, and count manually checked.
- `rejected`: corrupt, ambiguous, duplicated, unusable pose, or prohibited by license.
