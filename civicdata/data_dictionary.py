"""Data dictionary drafting for controlled municipal exports."""

from dataclasses import dataclass

from civicdata.dataset_normalization import normalize_schema_fields


@dataclass(frozen=True)
class DictionaryEntry:
    field_name: str
    source_name: str
    data_type: str
    description: str
    publication_notes: tuple[str, ...]


def draft_data_dictionary(fields: list[dict[str, str]]) -> list[DictionaryEntry]:
    """Create a staff-reviewable data dictionary draft from source schema fields."""

    entries: list[DictionaryEntry] = []
    for source, normalized in zip(fields, normalize_schema_fields(fields), strict=True):
        description = source.get("description", "").strip()
        if not description:
            description = "Description requires source-system owner review before publication."
        entries.append(
            DictionaryEntry(
                field_name=normalized.normalized_name,
                source_name=normalized.source_name,
                data_type=normalized.data_type,
                description=description,
                publication_notes=normalized.notes,
            )
        )
    return entries
