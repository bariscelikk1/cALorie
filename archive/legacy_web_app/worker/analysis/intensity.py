from .models import Exercise, Intensity


TEMPO_THRESHOLDS = {
    Exercise.SQUAT: (12.0, 25.0),
    Exercise.JUMPING_JACK: (25.0, 45.0),
    Exercise.PUSH_UP: (10.0, 22.0),
    Exercise.PULL_UP: (5.0, 12.0),
    Exercise.LUNGE: (10.0, 24.0),
    Exercise.SIT_UP: (12.0, 28.0),
    Exercise.MOUNTAIN_CLIMBER: (30.0, 60.0),
    Exercise.BURPEE: (8.0, 16.0),
    Exercise.PLANK: (1.0, 2.0),
}


def classify_intensity(exercise: Exercise, repetitions_per_minute: float) -> Intensity:
    moderate, vigorous = TEMPO_THRESHOLDS[exercise]
    if repetitions_per_minute < moderate:
        return Intensity.LIGHT
    if repetitions_per_minute < vigorous:
        return Intensity.MODERATE
    return Intensity.VIGOROUS
