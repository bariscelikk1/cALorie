from .models import Exercise, Intensity


TEMPO_THRESHOLDS = {
    Exercise.SQUAT: (12.0, 25.0),
    Exercise.JUMPING_JACK: (25.0, 45.0),
    Exercise.PUSH_UP: (10.0, 22.0),
}


def classify_intensity(exercise: Exercise, repetitions_per_minute: float) -> Intensity:
    moderate, vigorous = TEMPO_THRESHOLDS[exercise]
    if repetitions_per_minute < moderate:
        return Intensity.LIGHT
    if repetitions_per_minute < vigorous:
        return Intensity.MODERATE
    return Intensity.VIGOROUS

