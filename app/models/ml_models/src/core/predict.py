import joblib
from app.core.logging import setup_logging, get_logger
from sklearn.metrics import classification_report, accuracy_score
from ..features.data_ingestion import load_data
from src.config import test_path, model_saving_path

# setup logging
setup_logging() 
logger = get_logger("ml")

def main():
    # Load the test dataset
    test_df = load_data(test_path)
    logger.info("Loaded test dataset")

    # Separate features and labels
    X_test = test_df.drop(columns=["Sentiment"])
    y_test = test_df["Sentiment"]
    logger.info("Separated test features and labels")

    # Load the saved model
    model = joblib.load(model_saving_path)
    logger.info("Loaded trained model")

    # Make predictions
    logger.info("Predicting on test data")
    y_pred = model.predict(X_test)

    # Print evaluation metrics
    logger.info("Generating classification report for test set")
    print(classification_report(y_test, y_pred))

    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Test Accuracy: {accuracy}")
    print(f"Accuracy: {accuracy}")

if __name__ == "__main__":
    main()