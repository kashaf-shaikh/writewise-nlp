"""
train_model.py

Trains a Random Forest classifier for text quality prediction
and evaluates its performance using standard ML metrics.
"""

import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


def train_and_evaluate_model(feature_file_path: str, model_output_path: str) -> None:
    """
    Train Random Forest model and evaluate performance.

    Args:
        feature_file_path (str): Path to feature CSV file.
        model_output_path (str): Path to save trained model.
    """

    # Load feature dataset
    df = pd.read_csv(feature_file_path)

    # Split features and label
    X = df.drop(columns=["quality_grade"])
    y = df["quality_grade"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    print("\n========== MODEL EVALUATION ==========")
    print(f"Train Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
    print(f"Test Accuracy : {accuracy_score(y_test, y_test_pred):.4f}")

    print("\nClassification Report (Test Data):")
    print(classification_report(y_test, y_test_pred))

    print("Confusion Matrix (Test Data):")
    print(confusion_matrix(y_test, y_test_pred))

    joblib.dump(model, model_output_path)
    print(f"\nModel saved at: {model_output_path}")


if __name__ == "__main__":

    # 🔹 Get project root directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    feature_csv_path = os.path.join(
        BASE_DIR, "dataset", "text_quality_features.csv"
    )

    model_save_path = os.path.join(
        BASE_DIR, "ml", "text_quality_model.pkl"
    )

    train_and_evaluate_model(
        feature_file_path=feature_csv_path,
        model_output_path=model_save_path
    )
