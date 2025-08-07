from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from fastapi import FastAPI, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from src.model.trainer import ModelTrainer
import logging
from prometheus_fastapi_instrumentator import Instrumentator

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
    Enhanced prediction endpoint with:
    - Success/error tracking
    - Error classification
    - Prometheus metrics
    """
    try:
        try:
            model = ModelTrainer.load_model()
        except Exception as e:
            model_load_error.inc()
            raise ModelLoadError(f"Model loading failed: {str(e)}")

       # Process prediction
        prediction = model.predict([request.text])
        prediction_counter.inc()  # Only increment on full success
      
        return {
            "prediction": prediction.tolist()[0],
            "status": "success"
        }

    except ValueError as e:
        # Handle input validation errors
        error_counter.labels(error_type="input_validation").inc()
        raise HTTPException(status_code=400, detail=str(e))
        
    except ModelLoadError as e:
        # Handle model loading errors
        error_counter.labels(error_type="model_load").inc()
        raise HTTPException(status_code=503, detail="Service unavailable")
        
    except Exception as e:
        # Catch-all for other errors
        error_counter.labels(error_type="unexpected").inc()
        raise HTTPException(status_code=500, detail="Internal server error")
