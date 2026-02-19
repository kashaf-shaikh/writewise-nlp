"""
generate_features.py

This script reads the raw text dataset, extracts NLP features
from each text sample, and generates a machine-learning-ready
feature dataset in CSV format.
"""

import pandas as pd
from nlp.feature_extractor import extract_text_features


def generate_feature_dataset(
    input_csv: str,
    output_csv: str
) -> None:
    """
    Generate feature dataset from raw text CSV.

    Parameters
    ----------
    input_csv : str
        Path to raw dataset CSV containing text and quality_grade.
    output_csv : str
        Path where feature dataset CSV will be saved.
    """

    # Load raw dataset
    df = pd.read_csv(input_csv)

    feature_rows = []

    # Process each row
    for _, row in df.iterrows():
        text = row["text"]
        grade = row["quality_grade"]

        # Extract NLP features
        features = extract_text_features(text)

        # Add target label
        features["quality_grade"] = grade

        feature_rows.append(features)

    # Create DataFrame from features
    feature_df = pd.DataFrame(feature_rows)

    # Save ML-ready dataset
    feature_df.to_csv(output_csv, index=False, encoding="utf-8")

    print("Feature dataset generated successfully!")
    print(f"Saved to: {output_csv}")


if __name__ == "__main__":
    generate_feature_dataset(
        input_csv="dataset/text_quality_dataset.csv",
        output_csv="dataset/text_quality_features.csv"
    )
