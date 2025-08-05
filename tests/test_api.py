# Test API endpoints using requests
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(f"Health check: {response.json()}")

# Prediction
data = {"text": "This product is amazing!"}
response = requests.post("http://localhost:8000/predict", json=data)
print(f"Prediction response: {response.json()}")
