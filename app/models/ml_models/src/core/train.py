import joblib
from app.core.logging import get_logger, setup_logging
from app.models.ml_models.src.features.data_ingestion import load_data
from sklearn.ensemble import RandomForestClassifier
from app.models.ml_models.src.config import train_path, model_saving_path 

# Setup logging
setup_logging()
logger = get_logger("ml") 

def train_model(X_train, y_train):
    logger.info("Training RandomForest Classifier")
    model = RandomForestClassifier(
        n_estimators = 100,
        class_weight = {0: 2.533, 1: 4.222, 2: 0.422},
        random_state = 42
    )
    model.fit(X_train, y_train)
    return model

def main():
    # Load the training dataset
    train_df = load_data(train_path)
    logger.info("Loaded training dataset")

    # Separate features and labels
    X_train = train_df.drop(columns = ["Sentiment"])
    y_train = train_df["Sentiment"]
    logger.info("Separated features and labels")

    # Train the model
    model = train_model(X_train, y_train)

    # Save the model 
    joblib.dump(model, model_saving_path)
    logger.info(f"Saved the trained model to {model_saving_path}")

if __name__ == "__main__":
    main()