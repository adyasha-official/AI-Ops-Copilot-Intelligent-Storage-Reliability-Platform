"""Rule-based weighted risk score (0..1). Not ML: the data is simulated and unlabeled."""
import logging

logger = logging.getLogger("risk")

# (value at which risk contribution is 0, value at which it is 1)
RANGES = {
    "temperature": (30.0, 65.0),          # deg C
    "reallocated_sectors": (0.0, 500.0),  # count
    "power_on_hours": (0.0, 60000.0),     # hours
    "seek_error_rate": (0.0, 100.0),      # arbitrary rate units
}
WEIGHTS = {
    "temperature": 0.30,
    "reallocated_sectors": 0.35,
    "power_on_hours": 0.15,
    "seek_error_rate": 0.20,
}
MEDIUM_AT = 0.40
HIGH_AT = 0.70


def normalize(value: float, lo: float, hi: float) -> float:
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def contributions(temperature, reallocated_sectors, power_on_hours, seek_error_rate) -> dict:
    values = {
        "temperature": temperature,
        "reallocated_sectors": reallocated_sectors,
        "power_on_hours": power_on_hours,
        "seek_error_rate": seek_error_rate,
    }
    return {k: round(WEIGHTS[k] * normalize(v, *RANGES[k]), 4) for k, v in values.items()}


def risk_level(score: float) -> str:
    if score >= HIGH_AT:
        return "HIGH"
    if score >= MEDIUM_AT:
        return "MEDIUM"
    return "LOW"


def calculate_risk(temperature, reallocated_sectors, power_on_hours, seek_error_rate) -> tuple[float, str]:
    parts = contributions(temperature, reallocated_sectors, power_on_hours, seek_error_rate)
    score = round(min(1.0, sum(parts.values())), 3)
    return score, risk_level(score)


def top_factors(temperature, reallocated_sectors, power_on_hours, seek_error_rate, n=2) -> list[str]:
    """Human-readable names of the biggest contributors (used for explanations)."""
    parts = contributions(temperature, reallocated_sectors, power_on_hours, seek_error_rate)
    return [k for k, _ in sorted(parts.items(), key=lambda kv: kv[1], reverse=True)[:n]]
