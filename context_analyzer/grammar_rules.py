# context_analyzer/grammar_rules.py

from typing import Dict, List


class GrammarRuleChecker:
    """
    Detects basic grammar issues using deterministic rule-based logic.

    Phase 2.3 – Enhanced:
    Now includes human-readable suggestions for each grammar issue.
    This does NOT auto-correct text.
    It only guides the user for manual correction.
    """

    def check(self, sentence_data: Dict) -> List[Dict]:
        """
        Analyze a parsed sentence and return detected grammar issues.

        Parameters
        ----------
        sentence_data : Dict
            Output from SentenceParser containing subject, verb, tense, etc.

        Returns
        -------
        List[Dict]
            List of grammar issue dictionaries.
        """

        issues = []

        subject = sentence_data.get("subject")
        verb = sentence_data.get("main_verb")
        tense = sentence_data.get("tense")
        pos_tags = sentence_data.get("pos_tags", [])
        sentence_id = sentence_data.get("sentence_id")

        if not subject or not verb:
            return issues

        # -----------------------------
        # Rule 1: Subject–Verb Agreement
        # -----------------------------
        if self._subject_verb_mismatch(subject, pos_tags):
            issues.append({
                "type": "subject_verb_agreement",
                "message": "Possible subject–verb agreement error.",
                "suggestion": self._get_suggestion("subject_verb_agreement"),
                "sentence_id": sentence_id
            })

        # -----------------------------
        # Rule 2: Tense Mismatch
        # -----------------------------
        if self._tense_mismatch(tense, pos_tags):
            issues.append({
                "type": "tense_mismatch",
                "message": "Possible tense inconsistency in sentence.",
                "suggestion": self._get_suggestion("tense_mismatch"),
                "sentence_id": sentence_id
            })

        # -----------------------------
        # Rule 3: Missing Auxiliary Verb
        # -----------------------------
        if self._missing_auxiliary(pos_tags):
            issues.append({
                "type": "missing_auxiliary",
                "message": "Possible missing auxiliary verb.",
                "suggestion": self._get_suggestion("missing_auxiliary"),
                "sentence_id": sentence_id
            })

        return issues

    # =====================================================
    # INTERNAL RULE METHODS
    # =====================================================

    def _subject_verb_mismatch(self, subject: str, pos_tags: List) -> bool:
        subject_is_plural = False

        for word, tag in pos_tags:
            if word == subject:
                subject_is_plural = tag in {"NNS", "NNPS"}
                continue

            if tag == "VBZ" and subject_is_plural:
                return True
            if tag == "VBP" and not subject_is_plural:
                return True

        return False

    def _tense_mismatch(self, tense: str, pos_tags: List) -> bool:
        for _, tag in pos_tags:
            if tense == "past" and tag in {"VBZ", "VBP"}:
                return True
            if tense == "future" and tag == "VBD":
                return True
        return False

    def _missing_auxiliary(self, pos_tags: List) -> bool:
        verbs = [tag for _, tag in pos_tags if tag.startswith("VB")]
        auxiliaries = {"is", "are", "was", "were", "has", "have", "had"}

        if "VBG" in verbs or "VBN" in verbs:
            for word, _ in pos_tags:
                if word.lower() in auxiliaries:
                    return False
            return True

        return False

    # =====================================================
    # SUGGESTION GENERATOR
    # =====================================================

    def _get_suggestion(self, issue_type: str) -> str:
        """
        Return human-readable suggestion text
        for a detected grammar issue.
        """

        suggestions = {
            "subject_verb_agreement":
                "Ensure that the verb form matches the subject (singular subjects take singular verbs, plural subjects take plural verbs).",

            "tense_mismatch":
                "Maintain consistent verb tense throughout the sentence. Check whether the time reference matches the verb form.",

            "missing_auxiliary":
                "Check whether an auxiliary verb (is, are, was, were, has, have, had) is required for correct sentence structure."
        }

        return suggestions.get(
            issue_type,
            "Review the sentence structure for grammatical accuracy."
        )