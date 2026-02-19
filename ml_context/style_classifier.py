# ml_context/style_classifier.py

import joblib
from ml_context.style_features import StyleFeatureBuilder


class WritingStyleClassifier:
    """
    Predicts writing style using a trained ML model.
    """

    def __init__(self, model_path: str):
        self.model = joblib.load(model_path)
        self.feature_builder = StyleFeatureBuilder()

    def predict_style(self, text: str) -> str:
        features = self.feature_builder.build(text)
        feature_vector = [features[key] for key in sorted(features.keys())]

        prediction = self.model.predict([feature_vector])[0]

        return prediction  # casual / neutral / formal
