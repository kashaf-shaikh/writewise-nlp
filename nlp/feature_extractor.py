"""
feature_extractor.py

This module extracts linguistic, grammatical, spelling,
and readability features from a paragraph of text.
These features are used for text quality analysis
and machine learning model training.
"""

import nltk
import language_tool_python
import textstat
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK resources (run once)
nltk.download('punkt')

# Initialize tools (created once for performance)
grammar_tool = language_tool_python.LanguageTool('en-US')
spell_checker = SpellChecker()


def extract_all_features(text: str) -> dict:
    """
    Extract comprehensive NLP features from input text.

    Parameters
    ----------
    text : str
        Input paragraph.

    Returns
    -------
    dict
        Dictionary containing extracted numeric features.
    """

    # Handle empty input safely
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

    # Tokenization
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    words_alpha = [word for word in words if word.isalpha()]

    # Basic statistics
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

    # Grammar checking
    grammar_matches = grammar_tool.check(text)
    grammar_errors = len(grammar_matches)

    # Spelling checking
    misspelled_words = spell_checker.unknown(words_alpha)
    spelling_errors = len(misspelled_words)

    # Error density (per 100 words)
    total_errors = grammar_errors + spelling_errors
    error_density = (
        (total_errors / word_count) * 100 if word_count > 0 else 0.0
    )

    # Readability scores
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
