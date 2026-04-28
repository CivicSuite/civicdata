"""Records-retention archive bundle drafting."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveBundlePlan:
    dataset_title: str
    retention_schedule: str
    manifest_items: tuple[str, ...]
    ready_for_archive_review: bool
    required_action: str


def create_archive_bundle_plan(
    *, dataset_title: str, retention_schedule: str, files: list[str]
) -> ArchiveBundlePlan:
    """Create a records-retention archive checklist, not a ZIP or long-term store."""

    cleaned_files = tuple(item.strip() for item in files if item.strip())
    missing = not retention_schedule.strip() or not cleaned_files
    return ArchiveBundlePlan(
        dataset_title=dataset_title.strip(),
        retention_schedule=retention_schedule.strip(),
        manifest_items=cleaned_files,
        ready_for_archive_review=not missing,
        required_action=(
            "Add retention schedule and at least one manifest item before archive review."
            if missing
            else "Archive bundle manifest is ready for staff records-retention review."
        ),
    )
