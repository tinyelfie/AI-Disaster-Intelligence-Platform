from datetime import datetime
from app.schemas.disaster import DisasterInput, DisasterOutput

def run_disaster_inference(data: DisasterInput) -> DisasterOutput:
    # TEMPORARY placeholder (will connect real ML later)
    return DisasterOutput(
        disaster_type="flood",
        severity_score=0.82,
        risk_level="HIGH",
        population_at_risk=150000,
        confidence=0.90,
        timestamp=datetime.utcnow()
    )
