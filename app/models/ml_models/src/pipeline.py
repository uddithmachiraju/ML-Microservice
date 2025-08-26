import joblib
from app.models.ml_models.src.features.data_ingestion import load_data
from app.models.ml_models.src.features.preprocessing import preprocess_dataframe, split_and_vectorize, save_split_data
from app.models.ml_models.src.core.train import train_model
from app.models.ml_models.src.core.evaluate import main as evaluate_model
from app.models.ml_models.src.config import (
    g_drive_link,
    preprocessed_data_path,
    model_saving_path
)
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("pipeline")

def main():
    # Ingest Data
    logger.info("Loading data from Google Drive")
    df = load_data(path=g_drive_link, use_drive=True)

    # Preprocess Data
    logger.info("Preprocessing dataframe")
    df = preprocess_dataframe(df)
    df.to_csv(preprocessed_data_path, index=False)
    logger.info(f"Saved preprocessed data at {preprocessed_data_path}")

    # Split + Vectorize
    logger.info("Splitting and vectorizing")
    (X_train, y_train), (X_eval, y_eval), (X_test, y_test), _ = split_and_vectorize(df)

    # Save split datasets
    save_split_data(X_train, y_train, X_eval, y_eval, X_test, y_test)

    # Train Model
    logger.info("Training model")
    model = train_model(X_train, y_train)

    # Save Model
    joblib.dump(model, model_saving_path)
    logger.info(f"Saved trained model at {model_saving_path}")

    # Evaluate Model
    logger.info("Evaluating model on test dataset")
    evaluate_model()

if __name__ == "__main__":
    main()
