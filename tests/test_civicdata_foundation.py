from civicdata import __version__
from civicdata.archive_bundle import create_archive_bundle_plan
from civicdata.ckan_package import build_ckan_package_draft
from civicdata.data_dictionary import draft_data_dictionary
from civicdata.dataset_normalization import normalize_field_name, normalize_schema_fields
from civicdata.publication_plan import draft_publication_plan
from civicdata.redaction_review import review_fields_for_publication


def test_version_is_release_version():
    assert __version__ == "0.1.2"


def test_normalize_field_names_and_notes_dates_geospatial_fields():
    assert normalize_field_name("Permit Issued Date") == "permit_issued_date"
    fields = normalize_schema_fields([
        {"name": "Permit Issued Date", "type": "datetime"},
        {"name": "Parcel Address", "type": "text"},
    ])
    assert fields[0].normalized_name == "permit_issued_date"
    assert "ISO 8601" in fields[0].notes[0]
    assert "geocoding" in fields[1].notes[0]


def test_data_dictionary_defaults_missing_descriptions_to_review_required():
    entries = draft_data_dictionary([{"name": "Case ID", "type": "integer"}])
    assert entries[0].field_name == "case_id"
    assert "requires source-system owner review" in entries[0].description


def test_redaction_review_blocks_pii_and_exempt_fields():
    review = review_fields_for_publication(["case_id", "resident_email", "sealed_notes"])
    assert review.ready_for_publication is False
    assert {finding.category for finding in review.findings} == {"pii", "exemption"}
    assert "Human redaction" in review.required_action


def test_redaction_review_clear_still_requires_staff_approval():
    review = review_fields_for_publication(["case_id", "status"])
    assert review.ready_for_publication is True
    assert "staff approval" in review.required_action


def test_ckan_package_requires_license_and_clear_redaction_review():
    draft = build_ckan_package_draft(
        title="311 Requests",
        source_system="311 service platform",
        owner_department="Administration",
        license_id="",
        fields=[{"name": "resident_email", "type": "text"}],
    )
    assert draft.slug == "311-requests"
    assert draft.ready_for_staff_review is False
    assert "Open-data license" in draft.blockers[0]
    assert "Redaction" in draft.blockers[1]


def test_ckan_package_can_be_ready_for_staff_review_but_does_not_publish():
    draft = build_ckan_package_draft(
        title="Permit Activity",
        source_system="Permit system",
        owner_department="Planning",
        license_id="CC-BY-4.0",
        fields=[{"name": "permit_id", "type": "text", "description": "Permit identifier."}],
    )
    assert draft.ready_for_staff_review is True
    assert draft.license_id == "CC-BY-4.0"


def test_archive_bundle_requires_retention_schedule_and_manifest():
    plan = create_archive_bundle_plan(dataset_title="Budget", retention_schedule="", files=[])
    assert plan.ready_for_archive_review is False
    assert "retention schedule" in plan.required_action


def test_archive_bundle_ready_for_staff_retention_review():
    plan = create_archive_bundle_plan(
        dataset_title="Budget", retention_schedule="FIN-004 seven years", files=["budget.csv"]
    )
    assert plan.ready_for_archive_review is True
    assert plan.manifest_items == ("budget.csv",)


def test_publication_plan_is_human_approved_checklist_not_autonomous_publish():
    plan = draft_publication_plan(dataset_title="311", cadence="weekly")
    assert plan.target == "CKAN"
    assert plan.human_approval_required is True
    assert "Have staff approve" in plan.actions[-1]
