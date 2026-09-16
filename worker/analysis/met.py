from .models import Exercise, Intensity

# Practical V1 values based on the 2024 Adult Compendium categories. They are
# configuration, not a claim that video alone measures a person's metabolism.
MET_VALUES: dict[Exercise, dict[Intensity, float]] = {
    Exercise.SQUAT: {
        Intensity.LIGHT: 3.5,
        Intensity.MODERATE: 5.0,
        Intensity.VIGOROUS: 6.0,
    },
    Exercise.JUMPING_JACK: {
        Intensity.LIGHT: 5.0,
        Intensity.MODERATE: 7.0,
        Intensity.VIGOROUS: 8.0,
    },
    Exercise.PUSH_UP: {
        Intensity.LIGHT: 3.8,
        Intensity.MODERATE: 6.0,
        Intensity.VIGOROUS: 8.0,
    },
}


def met_value(exercise: Exercise, intensity: Intensity) -> float:
    return MET_VALUES[exercise][intensity]

