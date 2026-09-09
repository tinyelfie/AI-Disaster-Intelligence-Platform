"""
Fusion Module

Weighted average of the three model outputs → severity score.
No separate model file — pure Python logic.

Used directly by the backend:
    from ml.fusion.fusion import get_severity, fuse_predictions
"""


def get_severity(sat_prob: float, tweet_urgency: float, weather_risk: float) -> str:
    """
    Weighted combination of three model confidence scores.

    Weights (from spec):
        satellite  → 0.40
        nlp tweet  → 0.35
        weather    → 0.25

    Args:
        sat_prob:      Satellite disaster probability (0-1)
        tweet_urgency: NLP urgency / disaster probability (0-1)
        weather_risk:  XGBoost weather risk score (0-1)

    Returns:
        Severity level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    """
    score = (0.40 * sat_prob) + (0.35 * tweet_urgency) + (0.25 * weather_risk)

    if score > 0.75:  return "CRITICAL"
    if score > 0.50:  return "HIGH"
    if score > 0.25:  return "MEDIUM"
    return "LOW"


def get_fusion_score(sat_prob: float, tweet_urgency: float, weather_risk: float) -> float:
    """Return the raw numeric fusion score (0-1)."""
    return round((0.40 * sat_prob) + (0.35 * tweet_urgency) + (0.25 * weather_risk), 4)


def fuse_predictions(
    satellite_result: dict,
    nlp_result: dict,
    weather_result: dict,
) -> dict:
    """
    Full fusion — takes the raw dicts from each predict.py and returns
    a unified disaster assessment.

    Args:
        satellite_result: output from ml.satellite.predict.predict()
        nlp_result:       output from ml.nlp.predict.predict()
        weather_result:   output from ml.forecasting.predict.predict()

    Returns:
        {
            "severity":       str,    # CRITICAL | HIGH | MEDIUM | LOW
            "fusion_score":   float,  # 0-1
            "disaster_type":  str,    # dominant type from satellite
            "confidence":     float,  # average of model confidences
            "breakdown": {
                "satellite_contribution": float,
                "nlp_contribution":       float,
                "weather_contribution":   float,
            }
        }
    """
    sat_prob      = satellite_result.get("probability",        0.0)
    tweet_urgency = nlp_result.get("urgency_score",            0.0)
    weather_risk  = weather_result.get("risk_score",           0.0)

    sat_contrib   = round(0.40 * sat_prob,      4)
    nlp_contrib   = round(0.35 * tweet_urgency, 4)
    wx_contrib    = round(0.25 * weather_risk,  4)
    fusion_score  = round(sat_contrib + nlp_contrib + wx_contrib, 4)

    severity = get_severity(sat_prob, tweet_urgency, weather_risk)

    # Confidence = weighted average of individual model probabilities
    confidence = round(
        (0.40 * sat_prob) + (0.35 * tweet_urgency) + (0.25 * weather_risk), 4
    )

    return {
        "severity":      severity,
        "fusion_score":  fusion_score,
        "disaster_type": satellite_result.get("disaster_type", "unknown"),
        "confidence":    confidence,
        "breakdown": {
            "satellite_contribution": sat_contrib,
            "nlp_contribution":       nlp_contrib,
            "weather_contribution":   wx_contrib,
        },
    }
