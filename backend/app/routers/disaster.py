from fastapi import APIRouter
from app.schemas.disaster import DisasterInput, DisasterOutput
from app.services.ml_service import run_disaster_inference

router = APIRouter(prefix="/predict", tags=["Disaster Prediction"])

@router.post("/disaster", response_model=DisasterOutput)
def predict_disaster(data: DisasterInput):
    result = run_disaster_inference(data)
    return result
