from fastapi.testclient import TestClient

from civicdata import __version__
from civicdata.main import app

client = TestClient(app)


def test_root_reports_honest_current_state():
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "CivicData Bridge"
    assert payload["version"] == __version__
    assert payload["status"] == "open-data foundation"
    assert "live CKAN publishing" in payload["message"]
    assert "not implemented yet" in payload["message"]


def test_health_reports_civiccore_pin():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "civicdata"
    assert payload["version"] == "0.1.0"
    assert payload["civiccore_version"] == "0.2.0"


def test_public_ui_contains_version_boundaries_and_dependency():
    response = client.get("/civicdata")
    assert response.status_code == 200
    text = response.text
    assert "CivicData Bridge v0.1.0" in text
    assert "No live CKAN publication" in text
    assert "civiccore==0.2.0" in text


def test_api_endpoints_return_deterministic_payloads():
    fields = [{"name": "Permit Date", "type": "date", "description": "Issued date."}]
    assert client.post("/api/v1/civicdata/normalize", json={"fields": fields}).status_code == 200
    assert client.post("/api/v1/civicdata/data-dictionary", json={"fields": fields}).status_code == 200
    assert client.post(
        "/api/v1/civicdata/ckan-package",
        json={
            "title": "Permit Activity",
            "source_system": "Permits",
            "owner_department": "Planning",
            "license_id": "CC-BY-4.0",
            "fields": fields,
        },
    ).status_code == 200
    assert client.post(
        "/api/v1/civicdata/redaction-review", json={"field_names": ["resident_email"]}
    ).json()["ready_for_publication"] is False
    assert client.post(
        "/api/v1/civicdata/archive-bundle",
        json={"dataset_title": "Budget", "retention_schedule": "FIN-004", "files": ["budget.csv"]},
    ).status_code == 200
    assert client.post(
        "/api/v1/civicdata/publication-plan", json={"dataset_title": "311", "cadence": "weekly"}
    ).json()["human_approval_required"] is True
