# Production Depth: Publication Workpaper Persistence

## Summary

CivicData Bridge now supports optional SQLAlchemy-backed CKAN package draft and publication-plan workpaper records through `CIVICDATA_PUBLICATION_DB_URL`.

## Shipped

- `PublicationWorkpaperRepository` with schema-aware SQLAlchemy tables.
- Persisted CKAN package draft records with `package_id`.
- Persisted publication-plan records with `plan_id`.
- Retrieval endpoints:
  - `GET /api/v1/civicdata/ckan-package/{package_id}`
  - `GET /api/v1/civicdata/publication-plan/{plan_id}`
- Actionable `503` guidance when persistence is not configured.
- Regression tests for repository reload, API round trip, missing-record `404`, no-config `503`, and stateless fallback behavior.

## Still Not Shipped

- Live CKAN publication or API writeback.
- BI dashboards.
- Data warehouse storage.
- Autonomous redaction.
- External connector runtime.
