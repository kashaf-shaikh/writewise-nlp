"""
feature_extractor.py

Extracts linguistic, spelling,
and readability features from text.
LanguageTool dependency removed.
"""

import os
import nltk
import textstat
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize, sent_tokenize

from context_analyzer.sentence_parser import SentenceParser
from context_analyzer.grammar_rules import GrammarRuleChecker

# -------------------------------------------------
# NLTK Safe Setup
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NLTK_DATA_PATH = os.path.join(BASE_DIR, "..", "nltk_data")

os.makedirs(NLTK_DATA_PATH, exist_ok=True)
nltk.data.path.append(NLTK_DATA_PATH)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=NLTK_DATA_PATH)

# -------------------------------------------------
# Initialize tools (once)
# -------------------------------------------------

spell_checker = SpellChecker()
sentence_parser = SentenceParser()
grammar_checker = GrammarRuleChecker()


def extract_all_features(text: str) -> dict:

    if not text or not text.strip():
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0.0,
            "char_count": 0,
            "unique_words": 0,
            "lexical_diversity": 0.0,
            "avg_word_length": 0.0,
            "grammar_errors": 0,
            "spelling_errors": 0,
            "error_density": 0.0,
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0
        }

    # -----------------------------
    # Tokenization
    # -----------------------------

    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    words_alpha = [word for word in words if word.isalpha()]

    word_count = len(words_alpha)
    sentence_count = len(sentences)
    char_count = len(text)
    unique_words = len(set(words_alpha))

    avg_sentence_length = (
        word_count / sentence_count if sentence_count > 0 else 0.0
    )

    lexical_diversity = (
        unique_words / word_count if word_count > 0 else 0.0
    )

    avg_word_length = (
        sum(len(word) for word in words_alpha) / word_count
        if word_count > 0 else 0.0
    )

    # -----------------------------
    # Grammar errors (Custom Rule Engine)
    # -----------------------------

    grammar_errors = 0
    try:
        parsed = sentence_parser.parse(text)
        sentences_data = parsed.get("sentences", [])

        for sentence_data in sentences_data:
            issues = grammar_checker.check(sentence_data)
            grammar_errors += len(issues)

    except Exception:
        grammar_errors = 0

    # -----------------------------
    # Spelling errors
    # -----------------------------

    misspelled_words = spell_checker.unknown(words_alpha)
    spelling_errors = len(misspelled_words)

    # -----------------------------
    # Error density
    # -----------------------------

    total_errors = grammar_errors + spelling_errors

    error_density = (
        (total_errors / word_count) * 100 if word_count > 0 else 0.0
    )

    # -----------------------------
    # Readability
    # -----------------------------

    flesch_reading_ease = textstat.flesch_reading_ease(text)
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_length, 2),
        "char_count": char_count,
        "unique_words": unique_words,
        "lexical_diversity": round(lexical_diversity, 2),
        "avg_word_length": round(avg_word_length, 2),
        "grammar_errors": grammar_errors,
        "spelling_errors": spelling_errors,
        "error_density": round(error_density, 2),
        "flesch_reading_ease": round(flesch_reading_ease, 2),
        "flesch_kincaid_grade": round(flesch_kincaid_grade, 2)
    }
