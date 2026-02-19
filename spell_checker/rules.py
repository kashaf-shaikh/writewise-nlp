# spell_checker/rules.py

import re

URL_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|\S+@\S+\.\S+)"
)

def is_numeric(word: str) -> bool:
    return word.replace(".", "", 1).isdigit()


def is_all_caps(word: str) -> bool:
    return word.isupper()


def is_short(word: str) -> bool:
    return len(word) <= 2


def is_url_or_email(word: str) -> bool:
    return bool(URL_PATTERN.match(word))


def is_punctuation_only(word: str) -> bool:
    return all(not ch.isalnum() for ch in word)


def should_ignore(word: str) -> bool:
    """
    Returns True if the word should NOT be spell-checked
    """
    return (
        is_numeric(word)
        or is_all_caps(word)
        or is_short(word)
        or is_url_or_email(word)
        or is_punctuation_only(word)
    )
