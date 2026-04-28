"""Scheduled publication planning for CivicData Bridge."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PublicationPlan:
    dataset_title: str
    cadence: str
    target: str
    human_approval_required: bool
    actions: tuple[str, ...]


def draft_publication_plan(*, dataset_title: str, cadence: str, target: str = "CKAN") -> PublicationPlan:
    """Draft a scheduled publication checklist without contacting external systems."""

    return PublicationPlan(
        dataset_title=dataset_title.strip(),
        cadence=cadence.strip(),
        target=target.strip() or "CKAN",
        human_approval_required=True,
        actions=(
            "Confirm source-system export authority.",
            "Run normalization and data-dictionary review.",
            "Clear PII/exemption review.",
            "Confirm open-data license.",
            "Have staff approve package before publication.",
        ),
    )
