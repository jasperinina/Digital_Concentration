from datetime import UTC, datetime, timedelta, timezone

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError, StatementError

from app.core.db import Base, create_db_engine
from app.core.models import Project, Task
from app.focus.domain.models import (
    FocusProfile,
    FocusRule,
    FocusSession,
    ListMode,
    Mode,
    ResourceType,
    RuleKind,
    SessionStatus,
)


def make_session(profile: FocusProfile, task: Task | None = None) -> FocusSession:
    start = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)
    return FocusSession(
        profile_id=profile.id,
        profile_name=profile.name,
        profile_snapshot={"name": profile.name},
        mode=profile.mode,
        task_id=task.id if task else None,
        started_at=start,
        planned_end_at=start + timedelta(minutes=profile.duration_min),
    )


def test_migrations_create_all_tables(db_path, session_factory):
    tables = set(inspect(create_db_engine(db_path)).get_table_names())
    assert {
        "project",
        "task",
        "app_setting",
        "focus_profile",
        "focus_rule",
        "focus_session",
        "focus_block_event",
    } <= tables


def test_migrations_match_models(db_path, session_factory):
    """Схема после миграций совпадает с моделями — иначе нужна новая миграция."""
    with create_db_engine(db_path).connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []


def test_profile_with_rules_roundtrip(session):
    profile = FocusProfile(name="Учеба", duration_min=45, mode=Mode.STRICT)
    profile.rules = [
        FocusRule(resource_type=ResourceType.SITE, value="vk.com"),
        FocusRule(resource_type=ResourceType.SITE, kind=RuleKind.EXCEPTION, value="dev.vk.com"),
    ]
    session.add(profile)
    session.commit()
    session.expunge_all()

    loaded = session.scalars(select(FocusProfile)).one()
    assert loaded.mode is Mode.STRICT
    assert loaded.site_mode is ListMode.BLACK
    assert [r.value for r in loaded.rules] == ["vk.com", "dev.vk.com"]
    # перечисления хранятся строковыми значениями
    raw = session.execute(text("SELECT mode FROM focus_profile")).scalar_one()
    assert raw == "strict"


def test_profile_name_is_unique(session):
    session.add_all(
        [FocusProfile(name="Учеба", duration_min=45), FocusProfile(name="Учеба", duration_min=60)]
    )
    with pytest.raises(IntegrityError):
        session.commit()


def test_deleting_profile_keeps_session_history(session):
    profile = FocusProfile(name="Глубокая работа", duration_min=90)
    session.add(profile)
    session.flush()
    session.add(make_session(profile))
    session.commit()

    session.delete(profile)
    session.commit()
    session.expunge_all()

    remaining = session.scalars(select(FocusSession)).one()
    assert remaining.profile_id is None
    assert remaining.profile_name == "Глубокая работа"
    assert remaining.status is SessionStatus.ACTIVE


def test_deleting_task_unlinks_session(session):
    task = Task(name="Глава 2", project=Project(name="ВКР"))
    profile = FocusProfile(name="Учеба", duration_min=45)
    session.add_all([task, profile])
    session.flush()
    session.add(make_session(profile, task))
    session.commit()

    session.delete(task)
    session.commit()
    session.expunge_all()

    assert session.scalars(select(FocusSession)).one().task_id is None


def test_datetime_is_stored_in_utc(session):
    profile = FocusProfile(name="Учеба", duration_min=45)
    session.add(profile)
    session.flush()
    focus = make_session(profile)
    focus.started_at = datetime(2026, 11, 1, 13, 0, tzinfo=timezone(timedelta(hours=3)))
    session.add(focus)
    session.commit()
    session.expunge_all()

    loaded = session.scalars(select(FocusSession)).one()
    assert loaded.started_at == datetime(2026, 11, 1, 10, 0, tzinfo=UTC)
    assert loaded.started_at.tzinfo is UTC


def test_naive_datetime_is_rejected(session):
    profile = FocusProfile(name="Учеба", duration_min=45)
    session.add(profile)
    session.flush()
    focus = make_session(profile)
    focus.started_at = datetime(2026, 11, 1, 10, 0)
    session.add(focus)
    with pytest.raises(StatementError):
        session.commit()
