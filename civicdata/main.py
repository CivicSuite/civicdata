"""FastAPI runtime foundation for CivicData Bridge."""

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicdata import __version__
from civicdata.archive_bundle import create_archive_bundle_plan
from civicdata.ckan_package import build_ckan_package_draft
from civicdata.data_dictionary import draft_data_dictionary
from civicdata.dataset_normalization import normalize_schema_fields
from civicdata.public_ui import render_public_lookup_page
from civicdata.publication_plan import draft_publication_plan
from civicdata.redaction_review import review_fields_for_publication


app = FastAPI(
    title="CivicData Bridge",
    version=__version__,
    description="Open-data normalization, CKAN package drafts, archive bundles, and redaction-review support for CivicSuite.",
)

@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    """Return an empty favicon response so browser QA has a clean console."""

    return Response(status_code=204)


class FieldDefinition(BaseModel):
    name: str
    type: str = "text"
    description: str = ""


class NormalizeRequest(BaseModel):
    fields: list[FieldDefinition]


class CKANPackageRequest(BaseModel):
    title: str
    source_system: str
    owner_department: str
    license_id: str
    fields: list[FieldDefinition]


class ArchiveBundleRequest(BaseModel):
    dataset_title: str
    retention_schedule: str
    files: list[str]


class RedactionReviewRequest(BaseModel):
    field_names: list[str]


class PublicationPlanRequest(BaseModel):
    dataset_title: str
    cadence: str
    target: str = "CKAN"


def _fields_to_dicts(fields: list[FieldDefinition]) -> list[dict[str, str]]:
    return [field.model_dump() for field in fields]


@app.get("/")
def root() -> dict[str, str]:
    """Return current product state without overstating unshipped behavior."""

    return {
        "name": "CivicData Bridge",
        "version": __version__,
        "status": "open-data foundation",
        "message": (
            "CivicData Bridge package, API foundation, dataset normalization, data-dictionary drafts, "
            "CKAN package metadata drafts, PII/exemption review preflight, archive-bundle checklists, "
            "publication planning, and public UI foundation are online; live CKAN publishing, BI dashboards, "
            "data warehouse storage, autonomous redaction, and external connector runtime are not implemented yet."
        ),
        "next_step": "Post-v0.1.1 roadmap: live connector imports, staff approval queues, and CKAN handoff adapters",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return dependency/version health for deployment smoke checks."""

    return {
        "status": "ok",
        "service": "civicdata",
        "version": __version__,
        "civiccore_version": CIVICCORE_VERSION,
    }


@app.get("/civicdata", response_class=HTMLResponse)
def public_civicdata_page() -> str:
    """Return the public sample open-data preparation UI."""

    return render_public_lookup_page()


@app.post("/api/v1/civicdata/normalize")
def normalize_dataset(request: NormalizeRequest) -> dict[str, object]:
    return {"fields": [field.__dict__ for field in normalize_schema_fields(_fields_to_dicts(request.fields))]}


@app.post("/api/v1/civicdata/data-dictionary")
def data_dictionary(request: NormalizeRequest) -> dict[str, object]:
    return {"entries": [entry.__dict__ for entry in draft_data_dictionary(_fields_to_dicts(request.fields))]}


@app.post("/api/v1/civicdata/ckan-package")
def ckan_package(request: CKANPackageRequest) -> dict[str, object]:
    draft = build_ckan_package_draft(
        title=request.title,
        source_system=request.source_system,
        owner_department=request.owner_department,
        license_id=request.license_id,
        fields=_fields_to_dicts(request.fields),
    )
    return {
        **draft.__dict__,
        "dictionary": [entry.__dict__ for entry in draft.dictionary],
        "redaction_review": {
            **draft.redaction_review.__dict__,
            "findings": [finding.__dict__ for finding in draft.redaction_review.findings],
        },
    }


@app.post("/api/v1/civicdata/redaction-review")
def redaction_review(request: RedactionReviewRequest) -> dict[str, object]:
    review = review_fields_for_publication(request.field_names)
    return {**review.__dict__, "findings": [finding.__dict__ for finding in review.findings]}


@app.post("/api/v1/civicdata/archive-bundle")
def archive_bundle(request: ArchiveBundleRequest) -> dict[str, object]:
    return create_archive_bundle_plan(
        dataset_title=request.dataset_title,
        retention_schedule=request.retention_schedule,
        files=request.files,
    ).__dict__


@app.post("/api/v1/civicdata/publication-plan")
def publication_plan(request: PublicationPlanRequest) -> dict[str, object]:
    return draft_publication_plan(
        dataset_title=request.dataset_title,
        cadence=request.cadence,
        target=request.target,
    ).__dict__
