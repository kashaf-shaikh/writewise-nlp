# ml_context/train_style_classifier.py

import pandas as pd
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from ml_context.style_features import StyleFeatureBuilder


def train_style_classifier():
    data = pd.read_csv("dataset1/writing_style_dataset.csv")

    feature_builder = StyleFeatureBuilder()

    X = []
    y = []

    for _, row in data.iterrows():
        features = feature_builder.build(row["text"])
        X.append([features[key] for key in sorted(features.keys())])
        y.append(row["label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000, multi_class="auto")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("\nWriting Style Classifier Evaluation")
    print("----------------------------------")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, "ml_context/style_classifier.pkl")
    print("\nModel saved as ml_context/style_classifier.pkl")


if __name__ == "__main__":
    train_style_classifier()
