# Test model prediction
from src.model.trainer import ModelTrainer

model = ModelTrainer.load_model()
prediction = model.predict(["This is a great product!"])
print(f"Prediction: {prediction}")
