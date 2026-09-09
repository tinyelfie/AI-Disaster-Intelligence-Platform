from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DisasterInput(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime
    weather_rainfall: Optional[float] = None
    weather_wind_speed: Optional[float] = None
    social_signal_score: Optional[float] = None


class DisasterOutput(BaseModel):
    disaster_type: str
    severity_score: float
    risk_level: str
    population_at_risk: int
    confidence: float
    timestamp: datetime
