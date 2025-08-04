import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from trainer import ModelTrainer

def load_sample_data():
    """
    Loads and preprocesses the training data.
    - Uses pandas to read the dataset
    - Performs necessary preprocessing steps
    - Splits features and target variables
    - Returns preprocessed X (features) and y (target)
    """
    data = {
        'text': [
            "This product is amazing!",
            "Terrible experience, would not recommend",
            "Pretty good service overall",
            "Not worth the money at all",
            "Absolutely love it, best purchase ever"
        ],
        'sentiment': [1, 0, 1, 0, 1]  # 1 for positive, 0 for negative
    }
    pass

def main():
    """
    Main training pipeline that:
    1. Loads the data using load_sample_data()
    2. Initializes the ModelTrainer
    3. Performs model training
    4. Evaluates model performance
    5. Saves the trained model
    """
     # Load data
    logger.info("Loading training data...")
    df = load_sample_data()
    
    # Initialize and train model
    trainer = ModelTrainer()
    logger.info("Training model...")
    trainer.train(df['text'], df['sentiment'])
    
    # Save the model
    trainer.save_model()
    logger.info("Model training completed and saved")

if __name__ == "__main__":
    main()
