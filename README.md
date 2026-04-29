# CivicData Bridge

CivicData Bridge is the CivicSuite open-data preparation module. Version 0.1.1 ships the local package, FastAPI runtime, deterministic helper functions, optional database-backed publication workpapers, tests, release gates, public documentation, and browser-verified sample UI for preparing municipal datasets before human-approved publication.

## Shipping in v0.1.1

- Dataset field normalization for CKAN-friendly names, date/time hints, and geospatial-review notes.
- Data-dictionary draft generation from source schema metadata.
- CKAN/open-data package metadata drafts with license and redaction blockers.
- Optional SQLAlchemy-backed CKAN package and publication-plan workpaper records through `CIVICDATA_PUBLICATION_DB_URL`.
- PII/exemption preflight review that blocks readiness until staff review clears findings.
- Records-retention archive bundle checklist support.
- Scheduled publication planning checklists that require human approval.
- FastAPI endpoints, health check, static public UI, and release verification scripts.

## Not shipped yet

- Live CKAN publication or API writeback.
- BI dashboards or dashboard hosting.
- Data warehouse storage or long-term operational data storage beyond archive-bundle planning.
- Autonomous redaction or automatic exemption decisions.
- External connector runtime, approval queues, or CivicRecords exemption-engine integration.

## Install and run locally

CivicData Bridge v0.1.1 is pinned to `civiccore==0.3.0`.

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn civicdata.main:app --host 127.0.0.1 --port 8137
```

Open `http://127.0.0.1:8137/civicdata` for the browser sample and `http://127.0.0.1:8137/docs` for FastAPI docs.

Set `CIVICDATA_PUBLICATION_DB_URL` to persist CKAN package drafts and publication plans. Without it, CivicData Bridge remains deterministic and stateless.

## API surface

- `GET /` reports current product state and boundaries.
- `GET /health` reports `civicdata` and `civiccore` versions.
- `GET /civicdata` renders the public sample page.
- `POST /api/v1/civicdata/normalize` normalizes field metadata.
- `POST /api/v1/civicdata/data-dictionary` drafts data-dictionary entries.
- `POST /api/v1/civicdata/ckan-package` drafts CKAN package metadata.
- `GET /api/v1/civicdata/ckan-package/{package_id}` retrieves a persisted CKAN package draft when persistence is configured.
- `POST /api/v1/civicdata/redaction-review` flags PII/exemption review needs.
- `POST /api/v1/civicdata/archive-bundle` prepares records-retention archive checklists.
- `POST /api/v1/civicdata/publication-plan` prepares human-approved publication checklists.
- `GET /api/v1/civicdata/publication-plan/{plan_id}` retrieves a persisted publication plan when persistence is configured.

## Verification

```bash
python -m pytest -q
bash scripts/verify-docs.sh
python scripts/check-civiccore-placeholder-imports.py
python -m ruff check .
bash scripts/verify-release.sh
```

## Licensing

Code is Apache 2.0. Documentation is CC BY 4.0 unless otherwise noted. CivicData Bridge is designed for local municipal operation and does not require outbound runtime calls in the default profile.
