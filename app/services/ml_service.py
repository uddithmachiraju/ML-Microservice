
import pickle 
import numpy as np 
import pandas as pd
from pathlib import Path
from typing import Union, List
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import CustomException
from app.core.config import settings

setup_logging()
logger = get_logger("mlservice") 

class MLModelService:
    """Service for loading and running ML Model Predictions"""
    
    def __init__(self):
        self.model = None
        self.model_info = {}
        self._load_model()

    def _load_model(self):
        """Load the trained ML model"""
        model_path = Path(settings.model_path)

        if not model_path.exists():
            raise CustomException(
                message = "Model file not found", 
                status_code = 500, 
                details = f"Model file not found in {model_path}"
            )
        
        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f) 

            self.model_info = {
                "model_type": type(self.model).__name__, 
                "model_path": str(model_path), 
                "loaded_at": pd.Timestamp.now().isoformat() 
            }
            logger.info(f"Successfully loaded model: {self.model_info["model_type"]}") 

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise CustomException(
                message = "Failed to load ML Model", 
                status_code = 500, 
                details = str(e) 
            )
        
    def predict(self, features: Union[List, np.ndarray, pd.DataFrame]) -> dict:
        """Make predictions using the loaded model"""
        if self.model is None:
            raise CustomException(
                message = "Model not loaded", 
                status_code = 500, 
                details = "ML model is not properly initilized"
            )
        
        try:
            # Convert input into appropiate format
            if isinstance(features, list):
                features = np.array(features).reshape(1, -1) if len(np.array(features).shape) == 1 else np.array(features)
            elif isinstance(features, dict):
                features = pd.DataFrame([features])

            # Make predictions
            prediction = self.model.predict(features) 

            # Get prediction probabilities
            prediction_proba = None 
            if hasattr(self.model, "predict_proba"):
                try:
                    proba = self.model.predict_proba(features)
                    prediction_proba = proba.tolist() if isinstance(proba, np.ndarray) else proba
                except Exception as e:
                    logger.warning(f"Could not get prediction probabilities: {str(e)}") 

            # Format result
            result = {
                "prediction": prediction.tolist() if isinstance(prediction, np.ndarray) else prediction,
                "model_info": {
                    "model_type": self.model_info.get("model_type"),
                    "prediction_timestamp": pd.Timestamp.now().isoformat(),
                }
            }
            
            if prediction_proba is not None:
                result["prediction_probabilities"] = prediction_proba
                if isinstance(prediction_proba, list) and len(prediction_proba) > 0:
                    result["confidence"] = max(prediction_proba[0]) if isinstance(prediction_proba[0], list) else max(prediction_proba)
            
            logger.debug(f"Made prediction: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise CustomException(
                message="Prediction failed",
                status_code=500,
                details=str(e)
            )
        
    def get_model_info(self) -> dict:
        """Get information about the model"""
        return self.model_info 

    def health_check(self) -> dict:
        """Chech if the model is loaded and functioning"""
        try:
            if self.model is None:
                return {
                    "status": "unhealthy", 
                    "error": "Model not loaded"
                }
            
            if hasattr(self.model, "n_features_in_"):
                dummy_features = np.zeros((1, self.model.n_features_in_))
                self.model.predict(dummy_features)
            
            return {
                "status": "healthy", 
                "model_info": self.model_info
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e) 
            }