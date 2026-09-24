import os
import joblib
import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.app.ml.preprocessing import clean_text

LABEL_MAP = {
    0: "Normal",
    1: "Fake Urgency",
    2: "Scarcity",
    3: "Hidden Cost",
    4: "Trick Question",
    5: "Confirmshaming",
    6: "Sneak Into Basket",
    7: "Forced Continuity",
    8: "Disguised Advertisement",
    9: "Social Proof Manipulation",
    10: "Preselected Option",
    11: "Misleading Information"
}

REVERSE_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}

class DarkPatternClassifier:
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "ml", "models", "dark-pattern-distilbert"
        )
        self.pipeline: Optional[Pipeline] = None
        self.is_loaded = False
        self._load_if_exists()

    def _load_if_exists(self):
        pipeline_file = os.path.join(self.model_dir, "classifier.joblib")
        if os.path.exists(pipeline_file):
            try:
                self.pipeline = joblib.load(pipeline_file)
                self.is_loaded = True
            except Exception as e:
                print(f"[ML Model] Error loading model from {pipeline_file}: {e}")
                self.is_loaded = False

    def build_default_pipeline(self) -> Pipeline:
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                preprocessor=clean_text,
                ngram_range=(1, 3),
                min_df=1,
                max_features=10000,
                sublinear_tf=True
            )),
            ("clf", LogisticRegression(
                C=2.5,
                class_weight="balanced",
                max_iter=1000,
                random_state=42
            ))
        ])

    def train(self, texts: list, labels: list):
        self.pipeline = self.build_default_pipeline()
        self.pipeline.fit(texts, labels)
        self.is_loaded = True

    def predict(self, text: str) -> Tuple[str, float]:
        if not self.is_loaded or self.pipeline is None:
            # Fallback heuristic if model uninitialized
            return "Normal", 0.50

        cleaned = clean_text(text)
        if not cleaned:
            return "Normal", 0.99

        probs = self.pipeline.predict_proba([cleaned])[0]
        max_idx = int(np.argmax(probs))
        confidence = float(probs[max_idx])
        
        # Check if max class is in pipeline classes
        actual_class = self.pipeline.classes_[max_idx]
        category_name = LABEL_MAP.get(int(actual_class), "Normal")
        return category_name, confidence

    def save(self, output_dir: Optional[str] = None):
        target_dir = output_dir or self.model_dir
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, "classifier.joblib")
        joblib.dump(self.pipeline, target_file)
        print(f"[ML Model] Saved model pipeline to: {target_file}")
