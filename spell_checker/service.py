# spell_checker/service.py

import os
import re
from difflib import get_close_matches
from nlp.spell_normalizer import normalize_word

from spell_checker.rules import should_ignore


# ---------------------------
# Dictionary Loading (ONCE)
# ---------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICTIONARY_PATH = os.path.join(BASE_DIR, "resources", "english_words.txt")

with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
    DICTIONARY = set(word.strip() for word in f if word.strip())


# ---------------------------
# Tokenization Pattern
# ---------------------------
WORD_PATTERN = re.compile(r"\b\w+\b")


# ---------------------------
# Helper: Context Extraction
# ---------------------------

def extract_context(text: str, start_index: int) -> str:
    """
    Returns the sentence containing the error word.
    """
    sentence_start = max(
        text.rfind(".", 0, start_index),
        text.rfind("!", 0, start_index),
        text.rfind("?", 0, start_index)
    )

    sentence_end = min(
        idx for idx in [
            text.find(".", start_index),
            text.find("!", start_index),
            text.find("?", start_index)
        ] if idx != -1
    ) if any(p in text[start_index:] for p in ".!?") else len(text)

    return text[sentence_start + 1: sentence_end + 1].strip()


# ---------------------------
# Helper: Suggestion Generator
# ---------------------------

def generate_suggestions(word: str) -> list:
    """
    Returns up to 5 close dictionary matches.
    """
    return get_close_matches(word, DICTIONARY, n=5, cutoff=0.8)


# ---------------------------
# MAIN SPELL CHECK FUNCTION
# ---------------------------

def check_spelling(text: str) -> list:
    """
    Input: Raw paragraph text
    Output: List of issue dictionaries
    """

    issues = []
    issue_id = 1

    for match in WORD_PATTERN.finditer(text):
        original_word = match.group()
        start_index = match.start()
        length = len(original_word)

        normalized_word = original_word.lower()

        # Apply to ignore rules
        if should_ignore(original_word):
            continue

        # Dictionary lookup (with normalization)
        if normalized_word not in DICTIONARY:

            # Try normalized forms
            normalized_forms = normalize_word(normalized_word)

            is_valid = False
            for form in normalized_forms:
                if form in DICTIONARY:
                    is_valid = True
                    break

            # If still invalid after normalization, mark as error
            if not is_valid:
                suggestions = generate_suggestions(normalized_word)

                issue = {
                    "issue_id": issue_id,
                    "issue_type": "spelling",  # NEW
                    "source": "spell_checker",  # NEW

                    "error_word": original_word,
                    "start_index": start_index,
                    "length": length,
                    "end_index": start_index + length,  # NEW

                    "reason": f"The word '{original_word}' is not spelled correctly.",
                    "context": extract_context(text, start_index),
                    "suggestions": suggestions
                }

                issues.append(issue)
                issue_id += 1

    return issues
