"""
app.py

Flask backend for the Intelligent Text Quality Analyzer project.

Responsibilities:
- Start Flask web server
- Serve frontend UI (index.html)
- Provide REST API endpoint (/predict)
- Connect frontend with ML prediction logic

IMPORTANT:
- This file DOES NOT contain ML logic
- It only calls existing functions from main.py
"""

import os
import joblib
from flask import Flask, request, jsonify, render_template

from spell_checker.service import check_spelling
from config.config import MODEL_FILE
from config.logging_config import setup_logger
from main import load_model, predict_text_quality
from ml_context.style_classifier import WritingStyleClassifier


# -------------------------------------------------
# Base Directory (IMPORTANT for Render deployment)
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# -------------------------------------------------
# Load Context Models Safely (Absolute Paths)
# -------------------------------------------------

SPELL_CONTEXT_MODEL_PATH = os.path.join(
    BASE_DIR, "ml_context", "spell_context_model.pkl"
)

STYLE_CLASSIFIER_MODEL_PATH = os.path.join(
    BASE_DIR, "ml_context", "style_classifier.pkl"
)

SPELL_CONTEXT_MODEL = joblib.load(SPELL_CONTEXT_MODEL_PATH)

STYLE_CLASSIFIER = WritingStyleClassifier(
    model_path=STYLE_CLASSIFIER_MODEL_PATH
)


# -------------------------------------------------
# Flask App Initialization
# -------------------------------------------------

app = Flask(__name__)

# Initialize logger for Flask app
logger = setup_logger("FlaskApp")

# Load trained ML model ONCE at startup
logger.info("Loading ML model at server startup...")
model = load_model(MODEL_FILE)
logger.info("ML model loaded successfully")


# -------------------------------------------------
# Routes
# -------------------------------------------------

@app.route("/api/spell-check", methods=["POST"])
def spell_check_api():
    """
    API endpoint for spell checking.
    Expects JSON: { "text": "<paragraph>" }
    Returns: { "issues": [...] }
    """
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"issues": [], "error": "No text provided"}), 400

    text = data["text"]

    issues = check_spelling(text)

    return jsonify({"issues": issues}), 200


@app.route("/", methods=["GET"])
def home():
    """
    Serve frontend UI.
    """
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Prediction API endpoint.
    """

    data = request.get_json()

    if not data or "text" not in data:
        logger.warning("Invalid API request: 'text' field missing")
        return jsonify({
            "error": True,
            "message": "JSON body must contain 'text' field"
        }), 400

    user_text = data["text"]

    result = predict_text_quality(
        user_text,
        model,
        spell_context_model=SPELL_CONTEXT_MODEL,
        style_classifier=STYLE_CLASSIFIER
    )

    if result.get("error"):
        logger.warning(f"Prediction failed: {result['message']}")
        return jsonify(result), 400

    logger.info("Prediction served successfully via API")
    return jsonify(result), 200


# -------------------------------------------------
# Application Entry Point
# -------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting Flask server...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
