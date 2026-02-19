"""
main.py

Core logic for the Intelligent Text Quality Analyzer.
"""

import os
import joblib
import pandas as pd

from spell_checker.service import check_spelling
from context_analyzer.sentence_parser import SentenceParser
from context_analyzer.grammar_rules import GrammarRuleChecker
from decision_engine.error_fusion import ErrorFusionEngine
from ml_context.spell_context_features import SpellContextFeatureBuilder

from config.config import (
    MODEL_FILE,
    CONFIDENCE_THRESHOLD,
    MIN_WORD_COUNT,
    MIN_CHAR_COUNT
)
from config.logging_config import setup_logger
from nlp.feature_extractor import extract_all_features


# -------------------------------------------------
# Logger Initialization
# -------------------------------------------------

logger = setup_logger(__name__)


# -------------------------------------------------
# Core Engine Initialization (Loaded Once)
# -------------------------------------------------

sentence_parser = SentenceParser()
grammar_checker = GrammarRuleChecker()
fusion_engine = ErrorFusionEngine()
spell_feature_builder = SpellContextFeatureBuilder()


# -------------------------------------------------
# Input Validation
# -------------------------------------------------

def validate_input_text(text: str) -> dict:

    if not text or not text.strip():
        return {"is_valid": False, "message": "Input text is empty."}

    cleaned_text = text.strip()

    if len(cleaned_text) < MIN_CHAR_COUNT:
        return {
            "is_valid": False,
            "message": "Text is too short for reliable analysis."
        }

    word_count = len(cleaned_text.split())
    if word_count < MIN_WORD_COUNT:
        return {
            "is_valid": False,
            "message": "Text does not contain enough words."
        }

    if cleaned_text.isnumeric():
        return {
            "is_valid": False,
            "message": "Text contains only numbers."
        }

    alpha_ratio = sum(c.isalpha() for c in cleaned_text) / len(cleaned_text)
    if alpha_ratio < 0.5:
        return {
            "is_valid": False,
            "message": "Text contains too many non-alphabetic characters."
        }

    return {"is_valid": True, "message": "Valid input."}


# -------------------------------------------------
# Model Loader (Render Safe)
# -------------------------------------------------

def load_model(model_path: str):
    """
    Load trained ML model safely (Render compatible).
    """

    logger.info("Loading ML model...")

    try:
        # Convert to absolute path if needed
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, model_path)

        model = joblib.load(model_path)

        logger.info("ML model loaded successfully")
        return model

    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        raise


# -------------------------------------------------
# Prediction Logic
# -------------------------------------------------

def predict_text_quality(
    text: str,
    model,
    spell_context_model=None,
    style_classifier=None
) -> dict:

    # -----------------------------
    # Step 1: Validate input
    # -----------------------------
    validation = validate_input_text(text)
    if not validation["is_valid"]:
        logger.warning(f"Input validation failed: {validation['message']}")
        return {
            "error": True,
            "message": validation["message"]
        }

    # -----------------------------
    # Phase 2: Language Analysis
    # -----------------------------
    language_issues = []
    writing_style = "neutral"
    ml_spell_confidences = {}

    # -----------------------------
    # Spell checking
    # -----------------------------
    spell_errors = check_spelling(text)

    # -----------------------------
    # Sentence context
    # -----------------------------
    sentence_context = sentence_parser.parse(text)
    sentence_data_list = sentence_context.get("sentences", [])

    # -----------------------------
    # ML-based spell confidence
    # -----------------------------
    if spell_context_model and spell_errors:

        for error in spell_errors:

            word = (
                error.get("word")
                or error.get("token")
                or error.get("error_word")
            )

            if not word:
                continue

            try:
                features = spell_feature_builder.build_features(
                    word=word,
                    pos_tag="",
                    sentence_tense="present",
                    edit_distance=error.get("edit_distance", 1),
                    word_index=error.get("index", 0),
                    sentence_length=len(text.split()),
                    has_time_marker=False
                )

                vector = [features[k] for k in sorted(features.keys())]
                prob = spell_context_model.predict_proba([vector])[0][1]

                ml_spell_confidences[word] = prob

            except Exception as e:
                logger.warning(
                    f"Spell context prediction failed for '{word}': {e}"
                )

    # -----------------------------
    # Grammar rules
    # -----------------------------
    grammar_issues = []
    for sentence_data in sentence_data_list:
        try:
            grammar_issues.extend(grammar_checker.check(sentence_data))
        except Exception as e:
            logger.warning(f"Grammar check failed: {e}")

    # -----------------------------
    # Writing style (ML)
    # -----------------------------
    if style_classifier:
        try:
            writing_style = style_classifier.predict_style(text)
        except Exception as e:
            logger.warning(f"Style prediction failed: {e}")
            writing_style = "neutral"

    # -----------------------------
    # Hybrid Style Refinement
    # -----------------------------
    if writing_style == "formal":

        normalized_text = (
            text.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
        )

        words = normalized_text.split()
        word_count = len(words)

        contractions = {
            "don't", "can't", "won't", "isn't", "aren't", "wasn't",
            "weren't", "hasn't", "haven't", "hadn't",
            "i'm", "you're", "we're", "they're",
            "it's", "that's", "there's", "what's"
        }

        contraction_count = sum(
            1 for w in words if w.lower() in contractions
        )

        if contraction_count >= 2 and word_count >= 8:
            writing_style = "casual"

    # -----------------------------
    # Sentence text list
    # -----------------------------
    sentences_text = [
        s["text"] if isinstance(s, dict) else s
        for s in sentence_data_list
    ]

    # -----------------------------
    # Issue fusion
    # -----------------------------
    try:
        language_issues = fusion_engine.fuse(
            spell_errors=spell_errors,
            grammar_issues=grammar_issues,
            sentences=sentences_text,
            writing_style=writing_style,
            ml_spell_confidences=ml_spell_confidences
        )
    except Exception as e:
        logger.error(f"Issue fusion failed: {e}")
        language_issues = []

    # -----------------------------
    # ML Prediction
    # -----------------------------
    try:
        features = extract_all_features(text)
        feature_df = pd.DataFrame([features])

        probabilities = model.predict_proba(feature_df)[0]
        class_labels = model.classes_

        best_index = probabilities.argmax()
        predicted_grade = str(class_labels[best_index])

        confidence_score = float(probabilities[best_index] * 100)
        is_confident = bool(confidence_score >= CONFIDENCE_THRESHOLD)

        logger.info(
            f"Prediction -> Grade: {predicted_grade}, "
            f"Confidence: {confidence_score:.2f}%"
        )

    except Exception as e:
        logger.error(f"ML prediction failed: {e}")
        return {
            "error": True,
            "message": "Prediction engine failed."
        }

    # -----------------------------
    # Final Response
    # -----------------------------
    return {
        "error": False,
        "predicted_grade": predicted_grade,
        "confidence": round(confidence_score, 2),
        "is_confident": is_confident,
        "writing_style": writing_style,
        "language_issues": language_issues
    }
