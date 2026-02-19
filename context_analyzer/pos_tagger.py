# context_analyzer/pos_tagger.py

import os
import nltk
from typing import List, Tuple

# -------------------------------------------------
# Safe NLTK Setup (Render-compatible)
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NLTK_DATA_PATH = os.path.join(BASE_DIR, "..", "nltk_data")

os.makedirs(NLTK_DATA_PATH, exist_ok=True)
nltk.data.path.append(NLTK_DATA_PATH)

# Ensure punkt
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", download_dir=NLTK_DATA_PATH)

# Ensure averaged perceptron tagger (NEW FIX)
try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
except LookupError:
    nltk.download("averaged_perceptron_tagger_eng", download_dir=NLTK_DATA_PATH)


class POSTagger:
    """
    Lightweight POS tagging wrapper.
    """

    @staticmethod
    def tokenize(sentence: str) -> List[str]:
        return nltk.word_tokenize(sentence)

    @staticmethod
    def pos_tag(tokens: List[str]) -> List[Tuple[str, str]]:
        return nltk.pos_tag(tokens)
