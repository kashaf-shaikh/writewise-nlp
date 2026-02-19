# ml_context/style_features.py

import re
from typing import Dict


class StyleFeatureBuilder:
    """
    Extracts features to classify writing style
    (casual / neutral / formal).
    """

    CASUAL_WORDS = {
        "bro", "lol", "omg", "wanna", "gonna", "kinda", "dude"
    }

    def build(self, text: str) -> Dict:
        text_lower = text.lower()
        tokens = text_lower.split()

        contractions = sum(1 for t in tokens if "'" in t)
        casual_words = sum(1 for t in tokens if t in self.CASUAL_WORDS)
        exclamations = text.count("!")
        ellipsis = text.count("...")

        avg_sentence_length = max(len(tokens), 1)

        return {
            "contraction_count": contractions,
            "casual_word_count": casual_words,
            "exclamation_count": exclamations,
            "ellipsis_count": ellipsis,
            "avg_sentence_length": avg_sentence_length
        }
