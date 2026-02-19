# context_analyzer/sentence_parser.py

import re
from typing import Dict, List, Optional
from context_analyzer.pos_tagger import POSTagger


class SentenceParser:
    """
    Parses raw text into sentence-level linguistic context.
    This module is deterministic and ML-free (Phase 2.1).
    """

    VERB_TAGS = {"VB", "VBD", "VBG", "VBN", "VBP", "VBZ"}
    NOUN_TAGS = {"NN", "NNS", "NNP", "NNPS", "PRP"}

    PAST_MARKERS = {"yesterday", "ago", "last"}
    FUTURE_MARKERS = {"tomorrow", "next", "will"}

    def parse(self, text: str) -> Dict:
        sentences = self._split_sentences(text)
        parsed_sentences = []

        for idx, sentence in enumerate(sentences):
            tokens = POSTagger.tokenize(sentence)
            pos_tags = POSTagger.pos_tag(tokens)

            subject = self._extract_subject(pos_tags)
            main_verb = self._extract_main_verb(pos_tags)
            tense = self._detect_tense(pos_tags, tokens)

            parsed_sentences.append({
                "sentence_id": idx,
                "text": sentence,
                "tokens": tokens,
                "pos_tags": pos_tags,
                "subject": subject,
                "main_verb": main_verb,
                "tense": tense
            })

        return {"sentences": parsed_sentences}

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        raw_sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in raw_sentences if s.strip()]

    def _extract_subject(self, pos_tags: List) -> Optional[str]:
        for word, tag in pos_tags:
            if tag in self.NOUN_TAGS:
                return word
        return None

    def _extract_main_verb(self, pos_tags: List) -> Optional[str]:
        for word, tag in pos_tags:
            if tag in self.VERB_TAGS:
                return word
        return None

    def _detect_tense(self, pos_tags: List, tokens: List[str]) -> str:
        token_set = {t.lower() for t in tokens}

        # Explicit future
        if "will" in token_set or token_set & self.FUTURE_MARKERS:
            return "future"

        # Past tense via verb form or adverb
        for _, tag in pos_tags:
            if tag == "VBD":
                return "past"

        if token_set & self.PAST_MARKERS:
            return "past"

        return "present"
