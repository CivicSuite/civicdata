# CivicData Bridge User Manual

## Non-technical staff guide

CivicData Bridge helps a city prepare datasets before they are published to an open-data portal. It is a preparation and review tool with optional saved CKAN package/publication-plan workpapers, not an automatic publishing robot.

### What staff can do today

1. Review source fields and normalize them into clear open-data names.
2. Draft a data dictionary so residents understand what each field means.
3. Prepare CKAN-style package metadata for a future open-data portal handoff.
4. Run a deterministic preflight for PII or exempt-record field names.
5. Create an archive bundle checklist tied to records-retention schedules.
6. Draft a publication checklist for recurring datasets.
7. Retrieve saved CKAN package and publication-plan workpapers when IT enables persistence and retrieval auth.

### Required human review

Every dataset still needs staff approval before publication. Staff must confirm the source-system owner, redaction/exemption status, open-data license, retention schedule, and publication target.

### What v0.1.2 does not do

CivicData Bridge does not publish directly to CKAN, does not host dashboards, does not store a data warehouse, does not make legal exemption decisions, and does not redact records automatically.

## IT and technical guide

### Runtime

Install with `python -m pip install -e ".[dev]"` and run with `python -m uvicorn civicdata.main:app --host 127.0.0.1 --port 8137`.

Set `CIVICDATA_PUBLICATION_DB_URL` to enable SQLAlchemy-backed CKAN package draft and publication-plan records. Set `CIVICDATA_AUTH_TOKEN_ROLES` to a JSON token-to-role map before exposing persisted retrieval. Leave the database variable unset for deterministic stateless operation.

### Architecture

```mermaid
flowchart LR
  A[Source schema export] --> B[CivicData normalization]
  B --> C[Data dictionary draft]
  B --> D[PII/exemption preflight]
  C --> E[CKAN package metadata draft]
  D --> E
  E --> F[Staff approval]
  F --> G[Future CKAN handoff]
  B --> H[Archive bundle checklist]
```

### Endpoints

The public endpoints are listed in `README.md`. All v0.1.2 endpoints are deterministic and local. They do not perform live connector calls or publish data to external services. Retrieval endpoints require both `CIVICDATA_PUBLICATION_DB_URL` and `CIVICDATA_AUTH_TOKEN_ROLES`.

### Dependency contract

CivicData Bridge depends on `civiccore==0.4.0`. CivicCore must not import CivicData Bridge.

### Verification

Run `bash scripts/verify-release.sh` before release. The script checks docs, tests, Ruff, build artifacts, and package metadata.
