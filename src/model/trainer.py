import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import joblib
import logging
import os

# Configure logging for the model trainer
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        """
        Initialize the model pipeline with:
        1. TF-IDF Vectorizer: Converts text to numerical features
        2. Logistic Regression: Classification model for sentiment analysis
        """
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000)),  # Convert text to TF-IDF features
            ('classifier', LogisticRegression(max_iter=1000))  # Classification model
        ])
        
    def train(self, X, y):
        """
        Train the model with provided data
        Args:
            X: Input features (text data)
            y: Target labels (sentiment: 0 or 1)
        """
        logger.info("Starting model training...")
        self.model.fit(X, y)  # Train the entire pipeline
        logger.info("Model training completed")
        
    def save_model(self, path="models/model.joblib"):
        """
        Save the trained model to disk
        Args:
            path: Path where the model should be saved
        """
        # Convert to absolute path for reliability
        absolute_path = os.path.abspath(path)
        # Extract the directory path
        directory = os.path.dirname(absolute_path)
        # Create model directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        # Save model using joblib
        logger.info(f"Saving model to {absolute_path}")
        joblib.dump(self.model, absolute_path)
        
    @staticmethod
    def load_model(path="src/model/models/model.joblib"):
        """
        Load a trained model from disk
        Args:
            path: Path to the saved model file
        Returns:
            Loaded model object
        """
        logger.info(f"Loading model from {path}")
        return joblib.load(path)
