# context_analyzer/grammar_rules.py

from typing import Dict, List


class GrammarRuleChecker:
    """
    Detects basic grammar issues using sentence context.
    Phase 2.3: Rule-based triggers only.
    """

    def check(self, sentence_data: Dict) -> List[Dict]:
        issues = []

        subject = sentence_data.get("subject")
        verb = sentence_data.get("main_verb")
        tense = sentence_data.get("tense")
        pos_tags = sentence_data.get("pos_tags", [])
        sentence_id = sentence_data.get("sentence_id")

        if not subject or not verb or not isinstance(pos_tags, list):
            return issues

        try:
            # Rule 1: Subject–Verb Agreement
            if self._subject_verb_mismatch(subject, pos_tags):
                issues.append({
                    "type": "subject_verb_agreement",
                    "message": "Possible subject–verb agreement error.",
                    "sentence_id": sentence_id
                })

            # Rule 2: Tense mismatch
            if self._tense_mismatch(tense, pos_tags):
                issues.append({
                    "type": "tense_mismatch",
                    "message": "Possible tense inconsistency in sentence.",
                    "sentence_id": sentence_id
                })

            # Rule 3: Missing auxiliary verb
            if self._missing_auxiliary(pos_tags):
                issues.append({
                    "type": "missing_auxiliary",
                    "message": "Possible missing auxiliary verb.",
                    "sentence_id": sentence_id
                })

        except Exception:
            # Silent fail to prevent full pipeline crash
            return issues

        return issues

    def _subject_verb_mismatch(self, subject: str, pos_tags: List) -> bool:
        subject_is_plural = False

        for item in pos_tags:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue

            word, tag = item

            if word.lower() == subject.lower():
                subject_is_plural = tag in {"NNS", "NNPS"}
                continue

            if tag == "VBZ" and subject_is_plural:
                return True
            if tag == "VBP" and not subject_is_plural:
                return True

        return False

    def _tense_mismatch(self, tense: str, pos_tags: List) -> bool:
        for item in pos_tags:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue

            _, tag = item

            if tense == "past" and tag in {"VBZ", "VBP"}:
                return True
            if tense == "future" and tag == "VBD":
                return True

        return False

    def _missing_auxiliary(self, pos_tags: List) -> bool:
        verbs = []

        for item in pos_tags:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                continue

            _, tag = item
            if tag.startswith("VB"):
                verbs.append(tag)

        auxiliaries = {"is", "are", "was", "were", "has", "have", "had"}

        if "VBG" in verbs or "VBN" in verbs:
            for item in pos_tags:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    continue

                word, _ = item
                if word.lower() in auxiliaries:
                    return False

            return True

        return False
