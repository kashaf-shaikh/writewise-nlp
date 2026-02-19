# ml_context/spell_context_features.py

from typing import Dict
import numpy as np


class SpellContextFeatureBuilder:
    """
    Builds ML features for a single spelling error using sentence context.
    """

    def build_features(
        self,
        word: str,
        pos_tag: str,
        sentence_tense: str,
        edit_distance: int,
        word_index: int,
        sentence_length: int,
        has_time_marker: bool
    ) -> Dict:

        return {
            "word_length": len(word),
            "edit_distance": edit_distance,
            "is_verb": int(pos_tag.startswith("VB")),
            "is_past_sentence": int(sentence_tense == "past"),
            "is_future_sentence": int(sentence_tense == "future"),
            "has_time_marker": int(has_time_marker),
            "relative_position": word_index / max(sentence_length, 1)
        }
