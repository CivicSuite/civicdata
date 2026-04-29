from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine

from civicdata.ckan_package import build_ckan_package_draft
from civicdata.publication_plan import draft_publication_plan


metadata = sa.MetaData()

ckan_package_records = sa.Table(
    "ckan_package_records",
    metadata,
    sa.Column("package_id", sa.String(36), primary_key=True),
    sa.Column("title", sa.String(255), nullable=False),
    sa.Column("slug", sa.String(255), nullable=False),
    sa.Column("license_id", sa.String(100), nullable=False),
    sa.Column("source_system", sa.String(255), nullable=False),
    sa.Column("owner_department", sa.String(255), nullable=False),
    sa.Column("dictionary", sa.JSON(), nullable=False),
    sa.Column("redaction_review", sa.JSON(), nullable=False),
    sa.Column("ready_for_staff_review", sa.Boolean(), nullable=False),
    sa.Column("blockers", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicdata",
)

publication_plan_records = sa.Table(
    "publication_plan_records",
    metadata,
    sa.Column("plan_id", sa.String(36), primary_key=True),
    sa.Column("dataset_title", sa.String(255), nullable=False),
    sa.Column("cadence", sa.String(100), nullable=False),
    sa.Column("target", sa.String(100), nullable=False),
    sa.Column("human_approval_required", sa.Boolean(), nullable=False),
    sa.Column("actions", sa.JSON(), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    schema="civicdata",
)


@dataclass(frozen=True)
class StoredCKANPackage:
    package_id: str
    title: str
    slug: str
    license_id: str
    source_system: str
    owner_department: str
    dictionary: tuple[dict[str, object], ...]
    redaction_review: dict[str, object]
    ready_for_staff_review: bool
    blockers: tuple[str, ...]
    created_at: datetime


@dataclass(frozen=True)
class StoredPublicationPlan:
    plan_id: str
    dataset_title: str
    cadence: str
    target: str
    human_approval_required: bool
    actions: tuple[str, ...]
    created_at: datetime


class PublicationWorkpaperRepository:
    """SQLAlchemy-backed CKAN package and publication-plan workpaper records."""

    def __init__(self, *, db_url: str | None = None, engine: Engine | None = None) -> None:
        base_engine = engine or create_engine(db_url or "sqlite+pysqlite:///:memory:", future=True)
        if base_engine.dialect.name == "sqlite":
            self.engine = base_engine.execution_options(schema_translate_map={"civicdata": None})
        else:
            self.engine = base_engine
            with self.engine.begin() as connection:
                connection.execute(sa.text("CREATE SCHEMA IF NOT EXISTS civicdata"))
        metadata.create_all(self.engine)

    def create_ckan_package(
        self,
        *,
        title: str,
        source_system: str,
        owner_department: str,
        license_id: str,
        fields: list[dict[str, str]],
    ) -> StoredCKANPackage:
        draft = build_ckan_package_draft(
            title=title,
            source_system=source_system,
            owner_department=owner_department,
            license_id=license_id,
            fields=fields,
        )
        stored = StoredCKANPackage(
            package_id=str(uuid4()),
            title=draft.title,
            slug=draft.slug,
            license_id=draft.license_id,
            source_system=draft.source_system,
            owner_department=draft.owner_department,
            dictionary=tuple(entry.__dict__ for entry in draft.dictionary),
            redaction_review={
                **draft.redaction_review.__dict__,
                "findings": [finding.__dict__ for finding in draft.redaction_review.findings],
            },
            ready_for_staff_review=draft.ready_for_staff_review,
            blockers=draft.blockers,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                ckan_package_records.insert().values(
                    package_id=stored.package_id,
                    title=stored.title,
                    slug=stored.slug,
                    license_id=stored.license_id,
                    source_system=stored.source_system,
                    owner_department=stored.owner_department,
                    dictionary=list(stored.dictionary),
                    redaction_review=stored.redaction_review,
                    ready_for_staff_review=stored.ready_for_staff_review,
                    blockers=list(stored.blockers),
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_ckan_package(self, package_id: str) -> StoredCKANPackage | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(ckan_package_records).where(
                    ckan_package_records.c.package_id == package_id
                )
            ).mappings().first()
        if row is None:
            return None
        return _row_to_ckan_package(row)

    def create_publication_plan(
        self, *, dataset_title: str, cadence: str, target: str = "CKAN"
    ) -> StoredPublicationPlan:
        plan = draft_publication_plan(dataset_title=dataset_title, cadence=cadence, target=target)
        stored = StoredPublicationPlan(
            plan_id=str(uuid4()),
            dataset_title=plan.dataset_title,
            cadence=plan.cadence,
            target=plan.target,
            human_approval_required=plan.human_approval_required,
            actions=plan.actions,
            created_at=datetime.now(UTC),
        )
        with self.engine.begin() as connection:
            connection.execute(
                publication_plan_records.insert().values(
                    plan_id=stored.plan_id,
                    dataset_title=stored.dataset_title,
                    cadence=stored.cadence,
                    target=stored.target,
                    human_approval_required=stored.human_approval_required,
                    actions=list(stored.actions),
                    created_at=stored.created_at,
                )
            )
        return stored

    def get_publication_plan(self, plan_id: str) -> StoredPublicationPlan | None:
        with self.engine.begin() as connection:
            row = connection.execute(
                sa.select(publication_plan_records).where(
                    publication_plan_records.c.plan_id == plan_id
                )
            ).mappings().first()
        if row is None:
            return None
        return _row_to_publication_plan(row)


def _row_to_ckan_package(row: object) -> StoredCKANPackage:
    data = dict(row)
    return StoredCKANPackage(
        package_id=data["package_id"],
        title=data["title"],
        slug=data["slug"],
        license_id=data["license_id"],
        source_system=data["source_system"],
        owner_department=data["owner_department"],
        dictionary=tuple(data["dictionary"]),
        redaction_review=data["redaction_review"],
        ready_for_staff_review=data["ready_for_staff_review"],
        blockers=tuple(data["blockers"]),
        created_at=data["created_at"],
    )


def _row_to_publication_plan(row: object) -> StoredPublicationPlan:
    data = dict(row)
    return StoredPublicationPlan(
        plan_id=data["plan_id"],
        dataset_title=data["dataset_title"],
        cadence=data["cadence"],
        target=data["target"],
        human_approval_required=data["human_approval_required"],
        actions=tuple(data["actions"]),
        created_at=data["created_at"],
    )
