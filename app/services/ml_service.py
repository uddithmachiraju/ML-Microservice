import joblib
import numpy as np 
import pandas as pd
from pathlib import Path
from typing import Union, List
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import CustomException
from app.core.config import settings
from app.models.ml_models.src.features.preprocessing import clean_text

setup_logging()
logger = get_logger("mlservice") 

class MLModelService:
    """Service for loading and running ML Model Predictions"""

    def __init__(self):
        self.model = None 
        self.vectorizer = None 
        self.model_info = {} 
        self._load_model() 

    def _load_model(self):
        """Load the trained ML model and vectorizer"""
        model_path = Path(settings.model_path) 
        vectorizer_path = Path(settings.vectorizer_path) 

        if not model_path.exists():
            raise CustomException(
                message = "Model file not found", 
                status_code = 500, 
                details = f"Model file not found in {model_path}" 
            ) 
        if not vectorizer_path.exists():
            raise CustomException(
                message = "Vectorizer file not found", 
                status_code = 500, 
                details = f"Vectorizer file not found in {vectorizer_path}" 
            ) 

        try:
            with open(model_path, "rb") as f:
                self.model = joblib.load(f) 

            with open(vectorizer_path, "rb") as f:
                self.vectorizer = joblib.load(f) 

            self.model_info = {
                "model_type" : type(self.model).__name__, 
                "vectorizer_type" : type(self.vectorizer).__name__, 
                "model_path" : str(model_path), 
                "vectorizer_path" : str(vectorizer_path), 
                "loaded_at" : pd.Timestamp.now().isoformat() 
            } 
            logger.info(f"Successfully loaded model: {self.model_info['model_type']}, "
                        f"vectorizer: {self.model_info['vectorizer_type']}") 

        except Exception as e:
            logger.error(f"Failed to load model/vectorizer: {str(e)}") 
            raise CustomException(
                message = "Failed to load ML Model", 
                status_code = 500, 
                details = str(e) 
            ) 

    def predict(self, text : Union[str, List[str]]) -> dict:
        """Make predictions for raw text input"""
        if self.model is None or self.vectorizer is None:
            raise CustomException(
                message = "Model/Vectorizer not loaded", 
                status_code = 500, 
                details = "ML model or vectorizer is not properly initialized" 
            ) 

        try:
            # Handle input
            if isinstance(text, str):
                text = [text] 
            cleaned_texts = [clean_text(t) for t in text] 

            # Vectorize
            features = self.vectorizer.transform(cleaned_texts) 

            # Predict
            prediction = self.model.predict(features) 

            # Try to get probabilities
            prediction_proba = None 
            if hasattr(self.model, "predict_proba"):
                try:
                    prediction_proba = self.model.predict_proba(features).tolist() 
                except Exception as e:
                    logger.warning(f"Could not get prediction probabilities: {str(e)}") 

            # Sentiment mapping (customize as per training)
            sentiment_map = {0 : "Negative", 1 : "Neutral", 2 : "Positive"} 
            sentiments = [sentiment_map.get(p, "Unknown") for p in prediction] 

            result = {
                "prediction" : sentiments if len(sentiments) > 1 else sentiments[0], 
                "raw_prediction" : prediction.tolist(), 
                "model_info" : {
                    "model_type" : self.model_info.get("model_type"), 
                    "prediction_timestamp" : pd.Timestamp.now().isoformat(), 
                } 
            } 

            if prediction_proba is not None:
                result["prediction_probabilities"] = prediction_proba 
                result["confidence"] = (
                    max(prediction_proba[0]) if isinstance(prediction_proba[0], list) 
                    else max(prediction_proba) 
                ) 

            logger.debug(f"Made prediction: {result}") 
            return result 

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}") 
            raise CustomException(
                message = "Prediction failed", 
                status_code = 500, 
                details = str(e) 
            ) 
        
    def get_model_info(self) -> dict:
        """Get information about the model"""
        return self.model_info 

    def health_check(self) -> dict:
        """Check if the model and vectorizer are loaded and functioning"""
        try:
            if self.model is None or self.vectorizer is None:
                return {
                    "status": "unhealthy", 
                    "error": "Model or vectorizer not loaded" 
                } 

            # Run a dummy prediction with text input
            dummy_text = ["health check input"] 
            cleaned = [clean_text(t) for t in dummy_text] 
            features = self.vectorizer.transform(cleaned) 
            _ = self.model.predict(features) 

            return {
                "status": "healthy", 
                "model_info": self.model_info 
            } 
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e) 
            } 
        
ml_service = MLModelService() 