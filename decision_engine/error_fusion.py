# decision_engine/error_fusion.py

from typing import List, Dict
from decision_engine.severity_manager import SeverityManager


CONTRACTIONS = {
    "dont", "doesnt", "didnt", "cant", "couldnt", "shouldnt",
    "wouldnt", "wont", "isnt", "arent", "wasnt", "werent",
    "hasnt", "havent", "hadnt",
    "couldve", "shouldve", "wouldve",
    "im", "youre", "were", "theyre", "its",
    "theres", "heres", "whats", "whos"
}


class ErrorFusionEngine:
    """
    Final decision maker for all detected issues.
    """

    def fuse(
        self,
        spell_errors,
        grammar_issues,
        sentences,
        writing_style,
        ml_spell_confidences=None
    ):
        # Safe defaults
        spell_errors = spell_errors or []
        grammar_issues = grammar_issues or []
        sentences = sentences or []
        ml_spell_confidences = ml_spell_confidences or {}

        final_issues = []
        sentences_with_contractions = set()

        # -------------------------------------------------
        # 1️⃣ Process SPELL issues
        # -------------------------------------------------
        for error in spell_errors:
            try:
                issue = self._process_spell_error(
                    error, writing_style, ml_spell_confidences
                )
                if issue:
                    final_issues.append(issue)
            except Exception:
                continue

        # -------------------------------------------------
        # 2️⃣ Detect STYLE issues
        # -------------------------------------------------
        for sentence_id, sentence in enumerate(sentences):
            try:
                style_issues = detect_contraction_style_issue(
                    sentence=sentence,
                    sentence_id=sentence_id,
                    writing_style=writing_style
                )

                if style_issues:
                    sentences_with_contractions.add(sentence_id)
                    final_issues.extend(style_issues)
            except Exception:
                continue

        # -------------------------------------------------
        # 3️⃣ Add GRAMMAR issues with SUPPRESSION
        # -------------------------------------------------
        for issue in grammar_issues:
            try:
                sentence_id = issue.get("sentence_id")

                if (
                    writing_style == "formal"
                    and sentence_id in sentences_with_contractions
                ):
                    continue

                final_issues.append(issue)

            except Exception:
                continue

        return final_issues

    def _process_spell_error(
        self,
        error: dict,
        writing_style: str,
        ml_spell_confidences: dict
    ) -> dict | None:

        severity = SeverityManager.classify("spelling")

        # Work on copy (avoid mutation side-effects)
        error_copy = dict(error)

        word = (
            error_copy.get("word")
            or error_copy.get("token")
            or error_copy.get("error_word")
        )

        if not word:
            error_copy["severity"] = severity
            error_copy["issue_type"] = "spelling"
            return error_copy

        confidence = ml_spell_confidences.get(word, 1.0)

        if confidence < 0.7:
            error_copy["type"] = "suggestion"

        error_copy["severity"] = severity
        error_copy["issue_type"] = "spelling"

        return error_copy


def detect_contraction_style_issue(sentence, sentence_id, writing_style):

    issues = []

    if writing_style != "formal":
        return issues

    if not isinstance(sentence, str):
        return issues

    tokens = sentence.lower().split()

    for token in tokens:
        if token in CONTRACTIONS:
            issues.append({
                "sentence_id": sentence_id,
                "type": "style",
                "message": "Avoid informal contractions in formal academic writing.",
                "token": token
            })

    return issues
