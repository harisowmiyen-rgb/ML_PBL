import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from backend.app.ml.model import DarkPatternClassifier, LABEL_MAP

def run_evaluation():
    test_path = os.path.join(os.path.dirname(__file__), "data", "processed", "test.csv")
    if not os.path.exists(test_path):
        test_path = os.path.join(os.path.dirname(__file__), "data", "dark_patterns.csv")

    df = pd.read_csv(test_path)
    clf = DarkPatternClassifier()
    if not clf.is_loaded:
        print("Model not found on disk. Training first...")
        clf.train(df["text"].tolist(), df["label"].tolist())
        clf.save()

    preds = []
    true_labels = df["label"].tolist()

    for text in df["text"]:
        cat_name, _ = clf.predict(text)
        rev = {v: k for k, v in LABEL_MAP.items()}
        preds.append(rev.get(cat_name, 0))

    acc = accuracy_score(true_labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, preds, average="macro", zero_division=0)

    print("=" * 60)
    print("             MODEL PERFORMANCE EVALUATION REPORT")
    print("=" * 60)
    print(f"Overall Accuracy : {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro Precision  : {precision:.4f}")
    print(f"Macro Recall     : {recall:.4f}")
    print(f"Macro F1-Score   : {f1:.4f}")
    print("=" * 60)
    
    target_names = [LABEL_MAP[i] for i in sorted(list(set(true_labels)))]
    print("\nDetailed Per-Class Performance:")
    print(classification_report(true_labels, preds, target_names=target_names, zero_division=0))
    
    print("\nConfusion Matrix:")
    print(confusion_matrix(true_labels, preds))
    print("=" * 60)

if __name__ == "__main__":
    run_evaluation()
