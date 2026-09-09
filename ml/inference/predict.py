"""
ML inference module for disaster prediction.
Rule-based baseline (acts as ML proxy).
"""

def run_inference(input_data: dict) -> dict:
    rainfall = input_data.get("weather_rainfall", 0) or 0
    wind = input_data.get("weather_wind_speed", 0) or 0
    social = input_data.get("social_signal_score", 0) or 0

    # Flood
    if rainfall > 120 and social > 0.75:
        return {
            "disaster_type": "flood",
            "severity_score": round(min(1.0, rainfall / 200), 2),
            "risk_level": "HIGH",
            "population_at_risk": 150000,
            "confidence": 0.9
        }

    # Fire
    if wind > 45 and social > 0.6:
        return {
            "disaster_type": "fire",
            "severity_score": round(min(1.0, wind / 80), 2),
            "risk_level": "MEDIUM",
            "population_at_risk": 60000,
            "confidence": 0.85
        }

    # Earthquake
    if social > 0.65:
        return {
            "disaster_type": "earthquake",
            "severity_score": 0.7,
            "risk_level": "MEDIUM",
            "population_at_risk": 80000,
            "confidence": 0.8
        }

    # No Disaster
    return {
        "disaster_type": "none",
        "severity_score": 0.2,
        "risk_level": "LOW",
        "population_at_risk": 10000,
        "confidence": 0.6
    }
