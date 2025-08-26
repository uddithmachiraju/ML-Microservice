from pathlib import Path 

raw_data_path = Path("data/raw/Reviews.csv") 
preprocessed_data_path = Path("data/processed/processed.csv")
train_path = Path("data/processed/train.csv")
eval_path = Path("data/processed/eval.csv")
test_path = Path("data/processed/test.csv") 
model_saving_path = Path("models/model.pkl")
vectorizer_saving_path = Path("models/vectorizer.pkl") 

# Ensure folders exist, not files
raw_data_path.parent.mkdir(parents = True, exist_ok = True)
preprocessed_data_path.parent.mkdir(parents = True, exist_ok = True)
train_path.parent.mkdir(parents = True, exist_ok = True)
eval_path.parent.mkdir(parents = True, exist_ok = True)
test_path.parent.mkdir(parents = True, exist_ok = True)
model_saving_path.parent.mkdir(parents = True, exist_ok = True)
vectorizer_saving_path.parent.mkdir(parents = True, exist_ok = True) 

g_drive_link = "1a05UwEeg1_vAZojx0eBAE_4qX4Fs9vYY"