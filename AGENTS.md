# CivicData Bridge Agent Instructions

CivicData Bridge prepares municipal datasets for open-data review. Keep v0.1.0 honest: it drafts metadata and checklists, but it does not publish to CKAN, host dashboards, store a data warehouse, or make autonomous redaction/exemption decisions.

## Required verification

Run these before push or release:

```bash
python -m pytest -q
bash scripts/verify-docs.sh
python scripts/check-civiccore-placeholder-imports.py
python -m ruff check .
bash scripts/verify-release.sh
```

## Dependency boundary

CivicData Bridge may depend on `civiccore==0.2.0`. CivicCore must never import CivicData Bridge. Do not import from CivicCore placeholder packages.

## UX and documentation

Every frontend or docs change must be browser checked at desktop and mobile widths. Current-facing docs must clearly separate shipped v0.1.0 behavior from roadmap behavior.
