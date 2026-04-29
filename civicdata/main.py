"""FastAPI runtime foundation for CivicData Bridge."""

import os

from civiccore import __version__ as CIVICCORE_VERSION
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from civicdata import __version__
from civicdata.archive_bundle import create_archive_bundle_plan
from civicdata.ckan_package import build_ckan_package_draft
from civicdata.data_dictionary import draft_data_dictionary
from civicdata.dataset_normalization import normalize_schema_fields
from civicdata.persistence import (
    PublicationWorkpaperRepository,
    StoredCKANPackage,
    StoredPublicationPlan,
)
from civicdata.public_ui import render_public_lookup_page
from civicdata.publication_plan import draft_publication_plan
from civicdata.redaction_review import review_fields_for_publication


app = FastAPI(
    title="CivicData Bridge",
    version=__version__,
    description="Open-data normalization, CKAN package drafts, archive bundles, and redaction-review support for CivicSuite.",
)

_publication_repository: PublicationWorkpaperRepository | None = None
_publication_db_url: str | None = None


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
        "status": "open-data foundation plus publication workpaper persistence",
        "message": (
            "CivicData Bridge package, API foundation, dataset normalization, data-dictionary drafts, "
            "CKAN package metadata drafts, PII/exemption review preflight, archive-bundle checklists, "
            "publication planning, optional database-backed CKAN package/publication-plan workpapers, and "
            "public UI foundation are online; live CKAN publishing, BI dashboards, data warehouse storage, "
            "autonomous redaction, and external connector runtime are not implemented yet."
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
    if _publication_database_url() is not None:
        stored = _get_publication_repository().create_ckan_package(
            title=request.title,
            source_system=request.source_system,
            owner_department=request.owner_department,
            license_id=request.license_id,
            fields=_fields_to_dicts(request.fields),
        )
        return _stored_ckan_package_response(stored)

    draft = build_ckan_package_draft(
        title=request.title,
        source_system=request.source_system,
        owner_department=request.owner_department,
        license_id=request.license_id,
        fields=_fields_to_dicts(request.fields),
    )
    return {
        "package_id": None,
        **draft.__dict__,
        "dictionary": [entry.__dict__ for entry in draft.dictionary],
        "redaction_review": {
            **draft.redaction_review.__dict__,
            "findings": [finding.__dict__ for finding in draft.redaction_review.findings],
        },
    }


@app.get("/api/v1/civicdata/ckan-package/{package_id}")
def get_ckan_package(package_id: str) -> dict[str, object]:
    if _publication_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicData publication workpaper persistence is not configured.",
                "fix": "Set CIVICDATA_PUBLICATION_DB_URL to retrieve persisted CKAN package drafts.",
            },
        )
    stored = _get_publication_repository().get_ckan_package(package_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "CKAN package draft record not found.",
                "fix": "Use a package_id returned by POST /api/v1/civicdata/ckan-package.",
            },
        )
    return _stored_ckan_package_response(stored)


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
    if _publication_database_url() is not None:
        stored = _get_publication_repository().create_publication_plan(
            dataset_title=request.dataset_title,
            cadence=request.cadence,
            target=request.target,
        )
        return _stored_publication_plan_response(stored)

    plan = draft_publication_plan(
        dataset_title=request.dataset_title,
        cadence=request.cadence,
        target=request.target,
    )
    payload = plan.__dict__
    payload["plan_id"] = None
    return payload


@app.get("/api/v1/civicdata/publication-plan/{plan_id}")
def get_publication_plan(plan_id: str) -> dict[str, object]:
    if _publication_database_url() is None:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "CivicData publication workpaper persistence is not configured.",
                "fix": "Set CIVICDATA_PUBLICATION_DB_URL to retrieve persisted publication plans.",
            },
        )
    stored = _get_publication_repository().get_publication_plan(plan_id)
    if stored is None:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Publication plan record not found.",
                "fix": "Use a plan_id returned by POST /api/v1/civicdata/publication-plan.",
            },
        )
    return _stored_publication_plan_response(stored)


def _publication_database_url() -> str | None:
    return os.environ.get("CIVICDATA_PUBLICATION_DB_URL")


def _get_publication_repository() -> PublicationWorkpaperRepository:
    global _publication_db_url, _publication_repository
    db_url = _publication_database_url()
    if db_url is None:
        raise RuntimeError("CIVICDATA_PUBLICATION_DB_URL is not configured.")
    if _publication_repository is None or db_url != _publication_db_url:
        _dispose_publication_repository()
        _publication_db_url = db_url
        _publication_repository = PublicationWorkpaperRepository(db_url=db_url)
    return _publication_repository


def _dispose_publication_repository() -> None:
    global _publication_repository
    if _publication_repository is not None:
        _publication_repository.engine.dispose()
        _publication_repository = None


def _stored_ckan_package_response(stored: StoredCKANPackage) -> dict[str, object]:
    return {
        "package_id": stored.package_id,
        "title": stored.title,
        "slug": stored.slug,
        "license_id": stored.license_id,
        "source_system": stored.source_system,
        "owner_department": stored.owner_department,
        "dictionary": list(stored.dictionary),
        "redaction_review": stored.redaction_review,
        "ready_for_staff_review": stored.ready_for_staff_review,
        "blockers": list(stored.blockers),
        "created_at": stored.created_at.isoformat(),
    }


def _stored_publication_plan_response(stored: StoredPublicationPlan) -> dict[str, object]:
    return {
        "plan_id": stored.plan_id,
        "dataset_title": stored.dataset_title,
        "cadence": stored.cadence,
        "target": stored.target,
        "human_approval_required": stored.human_approval_required,
        "actions": list(stored.actions),
        "created_at": stored.created_at.isoformat(),
    }
