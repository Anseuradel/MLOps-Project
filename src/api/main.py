from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from src.model.trainer import ModelTrainer
import logging

# Initialize FastAPI app with metadata
app = FastAPI(title="ML Model Serving API")

# Prometheus metrics counter
prediction_counter = Counter('model_predictions_total', 'Total number of predictions made')

class PredictionRequest(BaseModel):
    """
    Pydantic model for request validation
    Ensures that incoming requests contain the required 'text' field
    """
    text: str

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes
    Returns 200 if the service is healthy
    Used by K8s liveness and readiness probes
    """
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    Exposes:
    - Total prediction count
    - Response times
    - Error rates
    """
    return Response(
        generate_latest().decode('utf-8'),
        media_type=CONTENT_TYPE_LATEST
    )

@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    Main prediction endpoint
    1. Validates input using PredictionRequest model
    2. Performs prediction using loaded model
    3. Increments metrics counter
    4. Returns prediction result
    """
    try:
        model = ModelTrainer.load_model()
        prediction = model.predict([request.text])
        prediction_counter.inc()  # Increment prediction counter
        # Add prediction logic here
        return {
            "prediction": prediction.tolist()[0],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
