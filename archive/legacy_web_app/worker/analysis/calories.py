from .models import Exercise, Intensity
from .met import met_value


def estimate_calories(met: float, weight_kg: float, duration_seconds: float) -> float:
    if not 30 <= weight_kg <= 250:
        raise ValueError("Body weight must be between 30 and 250 kg")
    if duration_seconds <= 0:
        raise ValueError("Duration must be positive")
    if met <= 0:
        raise ValueError("MET must be positive")
    minutes = duration_seconds / 60.0
    return met * 3.5 * weight_kg / 200.0 * minutes


def calorie_summary(
    exercise: Exercise,
    intensity: Intensity,
    weight_kg: float,
    duration_seconds: float,
    confidence: str,
) -> tuple[float, float, float, float]:
    met = met_value(exercise, intensity)
    estimate = estimate_calories(met, weight_kg, duration_seconds)
    uncertainty = {"high": 0.15, "medium": 0.25, "low": 0.35}[confidence]
    return (
        met,
        round(estimate, 2),
        round(estimate * (1 - uncertainty), 2),
        round(estimate * (1 + uncertainty), 2),
    )

