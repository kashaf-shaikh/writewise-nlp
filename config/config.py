"""
config.py

Central configuration for Text Quality Analyzer project.
"""

import os

# Base project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "ml")
LOG_DIR = os.path.join(BASE_DIR, "logs")

FEATURE_FILE = os.path.join(DATASET_DIR, "text_quality_features.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "text_quality_model.pkl")

# Prediction thresholds
CONFIDENCE_THRESHOLD = 60.0
MIN_WORD_COUNT = 3
MIN_CHAR_COUNT = 20
