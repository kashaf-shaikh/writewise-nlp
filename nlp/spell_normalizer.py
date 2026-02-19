"""
spell_normalizer.py

Lightweight, rule-based word normalization for spell checking.
This module does NOT perform grammar checking or ML-based lemmatization.
"""

from typing import Set


IRREGULAR_MAP = {
    "written": "write",
    "wrote": "write",
    "taken": "take",
    "given": "give",
    "done": "do",
    "gone": "go"
}


def normalize_word(word: str) -> Set[str]:
    """
    Generate safe normalized forms of a word for dictionary checking.

    Parameters:
        word (str): input word (already lowercased)

    Returns:
        Set[str]: possible base forms including original word
    """
    forms = set()
    forms.add(word)

    # Irregular verbs
    if word in IRREGULAR_MAP:
        forms.add(IRREGULAR_MAP[word])

    # Plural normalization
    if word.endswith("ies") and len(word) > 4:
        forms.add(word[:-3] + "y")

    if word.endswith("s") and len(word) > 3:
        forms.add(word[:-1])

    # Verb suffixes
    if word.endswith("ing") and len(word) > 5:
        forms.add(word[:-3])
        forms.add(word[:-3] + "e")

    if word.endswith("ed") and len(word) > 4:
        forms.add(word[:-2])

    # Noun suffixes
    for suffix in ("tion", "ment", "ness", "ity"):
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            forms.add(word[:-len(suffix)])

    return forms
