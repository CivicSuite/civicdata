"""CKAN/open-data package draft helpers."""

from dataclasses import dataclass

from civicdata.data_dictionary import DictionaryEntry, draft_data_dictionary
from civicdata.redaction_review import RedactionReview, review_fields_for_publication


@dataclass(frozen=True)
class CKANPackageDraft:
    title: str
    slug: str
    license_id: str
    source_system: str
    owner_department: str
    dictionary: tuple[DictionaryEntry, ...]
    redaction_review: RedactionReview
    ready_for_staff_review: bool
    blockers: tuple[str, ...]


def _slugify(value: str) -> str:
    return "-".join(part for part in value.lower().replace("_", "-").split() if part).strip("-")


def build_ckan_package_draft(
    *,
    title: str,
    source_system: str,
    owner_department: str,
    license_id: str,
    fields: list[dict[str, str]],
) -> CKANPackageDraft:
    """Build metadata for a CKAN package without publishing it."""

    dictionary = tuple(draft_data_dictionary(fields))
    redaction_review = review_fields_for_publication([entry.source_name for entry in dictionary])
    blockers: list[str] = []
    if not license_id.strip():
        blockers.append("Open-data license is required before CKAN publication.")
    if not redaction_review.ready_for_publication:
        blockers.append("Redaction/exemption review must be cleared before publication.")
    return CKANPackageDraft(
        title=title.strip(),
        slug=_slugify(title) or "dataset",
        license_id=license_id.strip(),
        source_system=source_system.strip(),
        owner_department=owner_department.strip(),
        dictionary=dictionary,
        redaction_review=redaction_review,
        ready_for_staff_review=not blockers,
        blockers=tuple(blockers),
    )
