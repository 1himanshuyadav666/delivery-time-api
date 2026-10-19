from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
FEATURES = ["distance_km", "prep_time_min", "traffic_level", "rain"]

app = FastAPI(title="Delivery Time Predictor", version="1.0.0",
              description="Predict delivery duration from order and traffic features.")
model = joblib.load(HERE / "model.joblib")


class Order(BaseModel):
    distance_km: float = Field(..., gt=0, le=50, description="Delivery distance in km")
    prep_time_min: int = Field(..., ge=0, le=120, description="Food preparation time")
    traffic_level: int = Field(..., ge=1, le=3, description="Traffic: 1=low, 2=medium, 3=high")
    rain: int = Field(..., ge=0, le=1, description="Rain indicator: 0=no, 1=yes")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
def predict(order: Order):
    row = pd.DataFrame([order.model_dump()])[FEATURES]
    return {
        "delivery_min": round(float(model.predict(row)[0]), 1),
        "model_version": app.version,
    }
