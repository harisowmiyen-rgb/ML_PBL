import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from backend.app.ml.model import DarkPatternClassifier, LABEL_MAP

def export_metadata():
    model_dir = os.path.join(os.path.dirname(__file__), "models", "dark-pattern-distilbert")
    os.makedirs(model_dir, exist_ok=True)
    metadata = {
        "model_architecture": "DistilBERT & Calibrated NLP Pipeline",
        "taxonomy_classes": LABEL_MAP,
        "input_features": "Sublinear TF-IDF (1-3 ngrams) & Embeddings",
        "weights": {
            "ml_weight": 0.60,
            "rule_weight": 0.40
        },
        "thresholds": {
            "high": 0.80,
            "medium": 0.60
        }
    }
    with open(os.path.join(model_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Exported model metadata to: {model_dir}/metadata.json")

if __name__ == "__main__":
    export_metadata()
