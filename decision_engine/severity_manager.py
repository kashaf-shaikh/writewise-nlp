# decision_engine/severity_manager.py

class SeverityManager:
    """
    Assigns severity levels to issues.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @staticmethod
    def classify(issue_type: str) -> str:
        if issue_type in {"spelling"}:
            return SeverityManager.MEDIUM

        if issue_type in {
            "tense_mismatch",
            "subject_verb_agreement",
            "missing_auxiliary"
        }:
            return SeverityManager.HIGH

        return SeverityManager.LOW
