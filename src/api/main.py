from fastapi import FastAPI, HTTPException, Request, Body
from pydantic import BaseModel
import numpy as np
from fastapi import Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from src.model.trainer import ModelTrainer
import logging
from prometheus_fastapi_instrumentator import Instrumentator
from time import time
from typing import Dict, Any
from typing import Literal, Optional
from datetime import datetime


# Initialize FastAPI app with metadata
app = FastAPI(title="ML Model Serving API")
Instrumentator().instrument(app).expose(app)

# Prometheus metrics counter
prediction_counter = Counter('model_predictions_total',
                           'Total number of predictions made',
                           ['error_type'])

error_counter = Counter(
    'http_errors_total',
    'Total API errors',
    ['status_code']
)

model_load_error = Counter('model_load_errors_total', 'Total model loading failures')

class ModelLoadError(Exception):
    """Custom exception for model loading failures"""
    pass

# Input Model
class PredictionRequest(BaseModel):
    """
    Pydantic model for request validation
    Ensures that incoming requests contain the required 'text' field
    """
    text: str

# Output Model
class PredictionResponse(BaseModel):
    """
    Enhanced response model with:
    - Prediction details
    - Confidence scores
    - Model metadata
    - Processing timings
    """
    text: str
    prediction: int
    prediction_label: str
    confidence: Optional[float] = None
    probabilities: Optional[dict] = None
    model_version: str
    model_type: str
    processing_time_ms: float
    timestamp: datetime
    status: Literal["success", "error"]
    error_details: Optional[str] = None

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

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    start_time = time()
    try:
        logging.info("Loading model...")
        model = ModelTrainer.load_model()
        logging.info("Model loaded successfully.")

        prediction = model.predict([request.text])
        logging.info(f"Prediction made: {prediction}")

        # Increment prediction counter with "none" as no error occurred
        logging.info("Incrementing prediction_counter with error_type=none")
        prediction_counter.labels(error_type="none").inc()

        response_data = {
            "text": request.text,
            "prediction": int(prediction[0]),
            "prediction_label": "positive" if prediction[0] == 1 else "negative",
            "model_version": "1.0.0",
            "model_type": "SentimentAnalysis",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "processing_time_ms": (time() - start_time) * 1000
        }

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([request.text])[0]
            response_data.update({
                "confidence": float(np.max(probabilities)),
                "probabilities": {
                    "negative": float(probabilities[0]),
                    "positive": float(probabilities[1])
                }
            })

        return response_data

    except ValueError as e:
        logging.info("Incrementing prediction_counter with error_type=none")
        prediction_counter.labels(error_type="value_error").inc()
        error_counter.labels(status_code="400").inc()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_details": str(e),
                "text": request.text,
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )

    except ModelLoadError as e:
        logging.info("Incrementing prediction_counter with error_type=none")
        prediction_counter.labels(error_type="model_load_error").inc()
        error_counter.labels(status_code="503").inc()
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "error_details": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )

    except Exception as e:
        logging.error(f"Error in predict: {e}", exc_info=True)
        logging.info("Incrementing prediction_counter with error_type=none")
        prediction_counter.labels(error_type="unknown_error").inc()
        error_counter.labels(status_code="500").inc()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_details": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )

# Debug endpoint (optional)
@app.post("/predict_debug")
async def predict_debug(request: Request):
    """
    Temporary endpoint to debug request format
    """
    raw_body = await request.body()
    return {
        "raw_body": raw_body.decode(),
        "headers": dict(request.headers)
    }

# test response
@app.post("/predict_test")
async def predict_test(request: PredictionRequest):
    """Test endpoint that returns all fields with sample data"""
    return {
        "text": request.text,
        "prediction": 1,
        "prediction_label": "positive",
        "confidence": 0.95,
        "probabilities": {"negative": 0.05, "positive": 0.95},
        "model_version": "1.0.0",
        "model_type": "SentimentAnalysis",
        "processing_time_ms": 42.5,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "success"
    }
