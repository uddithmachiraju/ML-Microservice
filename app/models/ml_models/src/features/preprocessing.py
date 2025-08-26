import re
import nltk
import string
import joblib 
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm 
from .data_ingestion import load_data
from app.core.logging import get_logger, setup_logging
from ..config import raw_data_path, preprocessed_data_path, train_path, eval_path, test_path, vectorizer_saving_path, g_drive_link

# Setup logging
setup_logging()
logger = get_logger("ml") 

# Download NLTK resources
logger.info(f"Downloading NLTK resources") 
nltk.download('wordnet')
nltk.download('stopwords')

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return " ".join(tokens)

def preprocess_dataframe(df):
    logger.info("Dropped Unnecessary Columns")
    df.drop(columns=["Id", "ProductId", "UserId", "ProfileName", "Time"], inplace=True)

    logger.info("Dropped Rows with missing values")
    df.dropna(subset=["Text", "Summary", "Score"], inplace=True)

    df["HelpfulnessRatio"] = df.apply(
        lambda row: row["HelpfulnessNumerator"] / row["HelpfulnessDenominator"]
        if row["HelpfulnessDenominator"] > 0 else 0,
        axis=1
    )

    logger.info("Cleaning Text & Summary")
    tqdm.pandas(desc="Cleaning Text")
    df["Cleaned_Text"] = df["Text"].progress_apply(clean_text)
    df["Cleaned_Summary"] = df["Summary"].progress_apply(clean_text)

    df["Cleaned_Text"] = df["Cleaned_Text"].fillna("")
    df["Cleaned_Summary"] = df["Cleaned_Summary"].fillna("")

    logger.info("Encoding Sentiment (1, 2) - Negative(0), (3) - Neutral(1), (4, 5) - Positive(2)")
    df["Sentiment"] = df["Score"].apply(lambda x: 0 if x <= 2 else 1 if x == 3 else 2)

    return df

def split_and_vectorize(df):
    logger.info("Splitting the data into Train, Eval, and Test sets")
    X = df["Cleaned_Text"]
    y = df["Sentiment"]

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size = 0.3, random_state = 42, stratify = y)
    X_eval, X_test, y_eval, y_test = train_test_split(X_temp, y_temp, test_size = 0.5, random_state = 42, stratify = y_temp)

    logger.info(f"Train size: {len(X_train)}, Eval size: {len(X_eval)}, Test size: {len(X_test)}")

    logger.info("Vectorizing text into TF-IDF")
    vectorizer = TfidfVectorizer(max_features = 1000)
    tqdm.pandas(desc = "Vectorizing Text")
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_eval_vectorized = vectorizer.transform(X_eval)
    X_test_vectorized = vectorizer.transform(X_test)
    
    joblib.dump(vectorizer, vectorizer_saving_path)
    logger.info(f"Saved Vectorizer in {vectorizer_saving_path}") 

    return (X_train_vectorized, y_train), (X_eval_vectorized, y_eval), (X_test_vectorized, y_test), vectorizer

def save_split_data(X_train, y_train, X_eval, y_eval, X_test, y_test):
    logger.info("Saving split datasets")
    train_df = pd.DataFrame(X_train.toarray())
    train_df["Sentiment"] = y_train.values
    train_df.to_csv(train_path, index = False)

    eval_df = pd.DataFrame(X_eval.toarray())
    eval_df["Sentiment"] = y_eval.values
    eval_df.to_csv(eval_path, index = False)

    test_df = pd.DataFrame(X_test.toarray())
    test_df["Sentiment"] = y_test.values
    test_df.to_csv(test_path, index = False)

    logger.info("Saved Train, Eval, and Test datasets successfully")

def main():
    df = load_data(path = g_drive_link, use_drive = True) 
    df = preprocess_dataframe(df)
    df.to_csv(preprocessed_data_path, index = False)
    logger.info("Saved the preprocessed data")

    (X_train, y_train), (X_eval, y_eval), (X_test, y_test), _ = split_and_vectorize(df)
    save_split_data(X_train, y_train, X_eval, y_eval, X_test, y_test)

if __name__ == "__main__":
    main()