"""Dataset normalization helpers for CivicData Bridge v0.1.1."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class NormalizedField:
    source_name: str
    normalized_name: str
    data_type: str
    notes: tuple[str, ...]


def normalize_field_name(name: str) -> str:
    """Return a CKAN-friendly snake_case field name."""

    cleaned = re.sub(r"[^0-9A-Za-z]+", "_", name.strip().lower()).strip("_")
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned or "field"


def normalize_schema_fields(fields: list[dict[str, str]]) -> list[NormalizedField]:
    """Normalize source schema metadata without mutating or publishing source data."""

    normalized: list[NormalizedField] = []
    for field in fields:
        source_name = field.get("name", "").strip()
        data_type = field.get("type", "text").strip().lower() or "text"
        notes: list[str] = []
        if "date" in data_type or "time" in data_type:
            notes.append("Use ISO 8601 date/time values before publication.")
        if any(token in source_name.lower() for token in ("address", "parcel", "lat", "lon")):
            notes.append("Geospatial values require city-approved geocoding validation.")
        normalized.append(
            NormalizedField(
                source_name=source_name,
                normalized_name=normalize_field_name(source_name),
                data_type=data_type,
                notes=tuple(notes),
            )
        )
    return normalized
