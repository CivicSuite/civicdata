from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from civicdata.main import app, _dispose_publication_repository
from civicdata.persistence import PublicationWorkpaperRepository


client = TestClient(app)

FIELDS = [{"name": "Permit Date", "type": "date", "description": "Issued date."}]


def _auth_headers(token: str = "reader-token") -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_repository_persists_ckan_package_and_publication_plan(tmp_path: Path) -> None:
    db_path = tmp_path / "civicdata.db"
    db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"

    repository = PublicationWorkpaperRepository(db_url=db_url)
    package = repository.create_ckan_package(
        title="Permit Activity",
        source_system="Permits",
        owner_department="Planning",
        license_id="CC-BY-4.0",
        fields=FIELDS,
    )
    plan = repository.create_publication_plan(dataset_title="Permit Activity", cadence="weekly")
    repository.engine.dispose()

    reloaded = PublicationWorkpaperRepository(db_url=db_url)
    stored_package = reloaded.get_ckan_package(package.package_id)
    stored_plan = reloaded.get_publication_plan(plan.plan_id)
    reloaded.engine.dispose()

    assert stored_package is not None
    assert stored_package.slug == "permit-activity"
    assert stored_package.dictionary[0]["field_name"] == "permit_date"
    assert stored_plan is not None
    assert stored_plan.human_approval_required is True
    assert "Confirm source-system export authority." in stored_plan.actions
    db_path.unlink()


def test_publication_persistence_api_round_trip(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicdata-api.db"
    monkeypatch.setenv("CIVICDATA_PUBLICATION_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    monkeypatch.setenv(
        "CIVICDATA_AUTH_TOKEN_ROLES",
        '{"reader-token": ["workpaper_reader"], "admin-token": ["data_admin"]}',
    )
    _dispose_publication_repository()

    created_package = client.post(
        "/api/v1/civicdata/ckan-package",
        json={
            "title": "Permit Activity",
            "source_system": "Permits",
            "owner_department": "Planning",
            "license_id": "CC-BY-4.0",
            "fields": FIELDS,
        },
    )
    package_id = created_package.json()["package_id"]
    fetched_package = client.get(
        f"/api/v1/civicdata/ckan-package/{package_id}",
        headers=_auth_headers(),
    )
    created_plan = client.post(
        "/api/v1/civicdata/publication-plan",
        json={"dataset_title": "Permit Activity", "cadence": "weekly"},
    )
    plan_id = created_plan.json()["plan_id"]
    fetched_plan = client.get(
        f"/api/v1/civicdata/publication-plan/{plan_id}",
        headers=_auth_headers("admin-token"),
    )

    _dispose_publication_repository()
    monkeypatch.delenv("CIVICDATA_PUBLICATION_DB_URL")
    monkeypatch.delenv("CIVICDATA_AUTH_TOKEN_ROLES")

    assert created_package.status_code == 200
    assert package_id
    assert fetched_package.status_code == 200
    assert fetched_package.json()["ready_for_staff_review"] is True
    assert created_plan.status_code == 200
    assert plan_id
    assert fetched_plan.status_code == 200
    assert fetched_plan.json()["human_approval_required"] is True
    db_path.unlink()


def test_get_ckan_package_without_auth_config_returns_actionable_503(monkeypatch) -> None:
    monkeypatch.delenv("CIVICDATA_PUBLICATION_DB_URL", raising=False)
    monkeypatch.delenv("CIVICDATA_AUTH_TOKEN_ROLES", raising=False)
    _dispose_publication_repository()

    response = client.get("/api/v1/civicdata/ckan-package/example")

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["message"] == "CivicData Bridge persisted publication workpaper retrieval auth is not configured."
    assert "Set CIVICDATA_AUTH_TOKEN_ROLES" in detail["fix"]


def test_get_ckan_package_requires_bearer_token(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "civicdata-auth.db"
    monkeypatch.setenv("CIVICDATA_PUBLICATION_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CIVICDATA_AUTH_TOKEN_ROLES", '{"reader-token": ["workpaper_reader"]}')
    _dispose_publication_repository()

    created_package = client.post(
        "/api/v1/civicdata/ckan-package",
        json={
            "title": "Permit Activity",
            "source_system": "Permits",
            "owner_department": "Planning",
            "license_id": "CC-BY-4.0",
            "fields": FIELDS,
        },
    )
    package_id = created_package.json()["package_id"]
    response = client.get(f"/api/v1/civicdata/ckan-package/{package_id}")

    _dispose_publication_repository()
    monkeypatch.delenv("CIVICDATA_PUBLICATION_DB_URL")
    monkeypatch.delenv("CIVICDATA_AUTH_TOKEN_ROLES")

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["message"] == "Bearer token required."
    assert "Authorization header" in detail["fix"]
    db_path.unlink()


def test_get_publication_plan_missing_id_returns_actionable_404(
    monkeypatch, tmp_path: Path
) -> None:
    db_path = tmp_path / "civicdata-missing.db"
    monkeypatch.setenv("CIVICDATA_PUBLICATION_DB_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CIVICDATA_AUTH_TOKEN_ROLES", '{"reader-token": ["workpaper_reader"]}')
    _dispose_publication_repository()

    response = client.get("/api/v1/civicdata/publication-plan/missing", headers=_auth_headers())

    _dispose_publication_repository()
    monkeypatch.delenv("CIVICDATA_PUBLICATION_DB_URL")
    monkeypatch.delenv("CIVICDATA_AUTH_TOKEN_ROLES")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["message"] == "Publication plan record not found."
    assert "POST /api/v1/civicdata/publication-plan" in detail["fix"]
    db_path.unlink()
