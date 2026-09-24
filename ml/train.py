import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.model_selection import train_test_split
from backend.app.ml.model import DarkPatternClassifier

def run_training():
    dataset_path = os.path.join(os.path.dirname(__file__), "data", "dark_patterns.csv")
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    df = pd.read_csv(dataset_path)
    print(f"Loaded dataset: {len(df)} samples across {df['pattern_type'].nunique()} classes.")

    # 80% train, 20% holdout (10% val, 10% test)
    train_df, holdout_df = train_test_split(
        df, test_size=0.20, random_state=42, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        holdout_df, test_size=0.50, random_state=42
    )

    print(f"Split sizes -> Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    proc_dir = os.path.join(os.path.dirname(__file__), "data", "processed")
    os.makedirs(proc_dir, exist_ok=True)
    train_df.to_csv(os.path.join(proc_dir, "train.csv"), index=False)
    val_df.to_csv(os.path.join(proc_dir, "val.csv"), index=False)
    test_df.to_csv(os.path.join(proc_dir, "test.csv"), index=False)

    clf = DarkPatternClassifier()
    clf.train(train_df["text"].tolist(), train_df["label"].tolist())
    
    # Save model artifact
    clf.save()
    print("Model successfully trained and persisted.")

if __name__ == "__main__":
    run_training()
