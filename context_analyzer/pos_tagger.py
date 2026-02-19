# context_analyzer/pos_tagger.py

import os
import nltk
from typing import List, Tuple

# -------------------------------------------------
# NLTK Safe Initialization (Render Compatible)
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NLTK_DATA_PATH = os.path.join(BASE_DIR, "..", "nltk_data")

# Ensure nltk_data directory exists
os.makedirs(NLTK_DATA_PATH, exist_ok=True)

# Add custom nltk_data path
nltk.data.path.append(NLTK_DATA_PATH)


def _ensure_nltk_resource(resource_name: str, download_name: str):
    """
    Ensures required NLTK resource is available.
    Downloads only if missing.
    """
    try:
        nltk.data.find(resource_name)
    except LookupError:
        nltk.download(download_name, download_dir=NLTK_DATA_PATH)


# Ensure required resources
_ensure_nltk_resource("tokenizers/punkt", "punkt")
_ensure_nltk_resource("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger")


# -------------------------------------------------
# POS Tagger Class
# -------------------------------------------------

class POSTagger:
    """
    Lightweight POS tagging wrapper.
    Keeps NLP logic isolated and reusable.
    """

    @staticmethod
    def tokenize(sentence: str) -> List[str]:
        return nltk.word_tokenize(sentence)

    @staticmethod
    def pos_tag(tokens: List[str]) -> List[Tuple[str, str]]:
        return nltk.pos_tag(tokens)
