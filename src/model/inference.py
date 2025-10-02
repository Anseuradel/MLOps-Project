from src.model.model import sentimentClassifier

import os
import config

def load_classifier()
   # Initialize model
   model = SentimentClassifier(n_classes=config.N_CLASSES).to(config.DEVICE)
   best_model_path = os.path.join(config.MODEL_TRAINING_OUTPUT_DIR, "best_model.pth")
  
  if os.path.exists(best_model_path):
     print(f"🔄 Loading previous model from {best_model_path}")
     model.load_state_dict(torch.load(best_model_path, map_location=config.DEVICE))
  else: 
    
