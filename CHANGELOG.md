# Changelog

All notable changes to CivicData Bridge are documented here. This project follows Keep a Changelog style and uses semantic versioning.

## [0.1.1] - 2026-04-28

### Added

- Optional SQLAlchemy-backed CKAN package draft and publication-plan workpaper records via `CIVICDATA_PUBLICATION_DB_URL`.
- CKAN package and publication-plan retrieval endpoints for persisted records.

### Changed

- Dependency-alignment release: moved CivicData Bridge to `civiccore==0.3.0` while preserving the existing v0.1.0 runtime foundation behavior.
- Updated CI, verification gates, package metadata, docs, runtime tests, landing page, and public UI labels for the v0.1.1 release.

## [0.1.0] - 2026-04-27

### Added

- CivicData Bridge package and FastAPI runtime foundation.
- Dataset field normalization helpers.
- Data-dictionary draft generation.
- CKAN/open-data package metadata draft support.
- PII/exemption redaction preflight.
- Records-retention archive bundle checklist support.
- Scheduled publication planning checklist support.
- Browser-verified public UI and docs landing page.
- Release gates for docs, tests, Ruff, build artifacts, package metadata, and placeholder imports.

### Not Shipped

- Live CKAN publication.
- BI dashboard hosting.
- Data warehouse storage.
- Autonomous redaction or exemption decisions.
- External connector runtime.
