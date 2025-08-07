from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from fastapi import FastAPI, Response
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


from fastapi import Body

@app.post("/predict", response_model=PredictionResponse)
async def predict(text: str = Body(..., embed=True)):
  
# @app.post("/predict", response_model=PredictionResponse)
# async def predict(request: PredictionRequest):
    """
    Enhanced prediction endpoint with:
    - Detailed response format
    - Confidence scores
    - Processing time tracking
    - Model metadata
    """
    start_time = time()
    try:
        try:
            model = ModelTrainer.load_model()
        except Exception as e:
            model_load_error.inc()
            raise ModelLoadError(f"Model loading failed: {str(e)}")

        # Process prediction
        prediction = model.predict([request.text])
        
        # Get additional prediction details if available
        response_data = {
            "text": request.text,
            "prediction": prediction.tolist()[0],
            "prediction_label": "positive" if prediction[0] == 1 else "negative",
            "model_version": "1.0.0",
            "model_type": "SentimentAnalysis",
            "timestamp": datetime.utcnow(),
            "status": "success",
            "processing_time_ms": (time() - start_time) * 1000
        }

        # Add confidence scores if model supports predict_proba
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba([request.text])[0]
            response_data.update({
                "confidence": float(np.max(probabilities)),
                "probabilities": {
                    "negative": float(probabilities[0]),
                    "positive": float(probabilities[1])
                }
            })

        prediction_counter.inc()
        return response_data

    except ValueError as e:
        error_counter.labels(error_type="input_validation").inc()
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_details": str(e),
                "text": request.text,
                "timestamp": datetime.utcnow(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )
        
    except ModelLoadError as e:
        error_counter.labels(error_type="model_load").inc()
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "error_details": str(e),
                "timestamp": datetime.utcnow(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )
        
    except Exception as e:
        error_counter.labels(error_type="unexpected").inc()
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_details": "Internal server error",
                "timestamp": datetime.utcnow(),
                "processing_time_ms": (time() - start_time) * 1000
            }
        )
    except Exception as e:
        # Catch-all for other errors
        error_counter.labels(error_type="unexpected").inc()
        raise HTTPException(status_code=500, detail="Internal server error")
