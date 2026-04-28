"""PII and exemption review helpers for CivicData Bridge."""

from dataclasses import dataclass

PII_MARKERS = (
    "ssn",
    "social_security",
    "dob",
    "birth_date",
    "email",
    "phone",
    "home_address",
    "driver_license",
)
EXEMPTION_MARKERS = ("juvenile", "medical", "victim", "confidential", "sealed", "exempt")


@dataclass(frozen=True)
class RedactionFinding:
    field_name: str
    category: str
    reason: str


@dataclass(frozen=True)
class RedactionReview:
    ready_for_publication: bool
    findings: tuple[RedactionFinding, ...]
    required_action: str


def review_fields_for_publication(field_names: list[str]) -> RedactionReview:
    """Flag fields that require human redaction/exemption review before release."""

    findings: list[RedactionFinding] = []
    for name in field_names:
        lower = name.lower()
        if any(marker in lower for marker in PII_MARKERS):
            findings.append(
                RedactionFinding(
                    field_name=name,
                    category="pii",
                    reason="Potential personally identifiable information requires review.",
                )
            )
        if any(marker in lower for marker in EXEMPTION_MARKERS):
            findings.append(
                RedactionFinding(
                    field_name=name,
                    category="exemption",
                    reason="Potential exempt or confidential record requires review.",
                )
            )
    ready = not findings
    return RedactionReview(
        ready_for_publication=ready,
        findings=tuple(findings),
        required_action=(
            "Human redaction/exemption review required before publication."
            if findings
            else "No PII marker detected by this deterministic preflight; staff approval still required."
        ),
    )
