CivicData Bridge v0.1.0

CivicData Bridge prepares municipal datasets for open-data review. It ships dataset normalization, data-dictionary drafts, CKAN package metadata drafts, PII/exemption preflight, archive-bundle checklists, publication planning, FastAPI endpoints, tests, docs, and browser QA evidence.

It does not ship live CKAN publishing, BI dashboards, data warehouse storage, autonomous redaction, or external connector runtime.

Run locally:
  python -m pip install -e ".[dev]"
  python -m uvicorn civicdata.main:app --host 127.0.0.1 --port 8137

Important routes:
  /health
  /civicdata
  /api/v1/civicdata/normalize
  /api/v1/civicdata/data-dictionary
  /api/v1/civicdata/ckan-package
  /api/v1/civicdata/redaction-review
  /api/v1/civicdata/archive-bundle
  /api/v1/civicdata/publication-plan

License: Apache 2.0 code, CC BY 4.0 docs.
