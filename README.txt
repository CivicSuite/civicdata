CivicData Bridge v0.1.2

CivicData Bridge prepares municipal datasets for open-data review. It ships dataset normalization, data-dictionary drafts, CKAN package metadata drafts, optional database-backed CKAN package/publication-plan workpapers, bearer-token protection for persisted retrieval, PII/exemption preflight, archive-bundle checklists, publication planning, FastAPI endpoints, tests, docs, and browser QA evidence.

It does not ship live CKAN publishing, BI dashboards, data warehouse storage, autonomous redaction, or external connector runtime.

Run locally:
  python -m pip install -e ".[dev]"
  python -m uvicorn civicdata.main:app --host 127.0.0.1 --port 8137

Set CIVICDATA_PUBLICATION_DB_URL to persist CKAN package drafts and publication plans. Set CIVICDATA_AUTH_TOKEN_ROLES to a JSON token-to-role map before exposing persisted retrieval. Without the database variable, CivicData Bridge remains deterministic and stateless. Without the auth variable, persisted retrieval endpoints return actionable 503 guidance. With auth configured, anonymous callers receive 401 and unauthorized roles receive 403.

Important routes:
  /health
  /civicdata
  /api/v1/civicdata/normalize
  /api/v1/civicdata/data-dictionary
  /api/v1/civicdata/ckan-package
  /api/v1/civicdata/ckan-package/{package_id}
  /api/v1/civicdata/redaction-review
  /api/v1/civicdata/archive-bundle
  /api/v1/civicdata/publication-plan
  /api/v1/civicdata/publication-plan/{plan_id}

License: Apache 2.0 code, CC BY 4.0 docs.
