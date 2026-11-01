"""Модели данных подсистемы цифровой концентрации."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, UTCDateTime, utc_now
from app.core.models import Project, Task


class Mode(StrEnum):
    SOFT = "soft"
    STRICT = "strict"


class ListMode(StrEnum):
    BLACK = "black"  # блокировать перечисленные ресурсы
    WHITE = "white"  # разрешить только перечисленные ресурсы


class UnlockPolicy(StrEnum):
    NONE = "none"
    PASSWORD = "password"  # досрочное снятие строгого режима паролем доверенного лица


class ResourceType(StrEnum):
    SITE = "site"
    APP = "app"


class RuleKind(StrEnum):
    LIST = "list"  # элемент черного или белого списка
    EXCEPTION = "exception"  # разрешенный ресурс, приоритетнее запрещающих правил


class SessionStatus(StrEnum):
    ACTIVE = "active"
    FINISHED = "finished"


class EndReason(StrEnum):
    COMPLETED = "completed"
    EARLY_SOFT = "early_soft"
    PASSWORD = "password"
    RECOVERED = "recovered"


class BlockAction(StrEnum):
    BLOCKED = "blocked"
    TERMINATED = "terminated"


def enum_column(enum_cls: type[StrEnum]) -> Enum:
    """Хранит значения перечисления строками с проверочным ограничением."""
    return Enum(
        enum_cls,
        name=enum_cls.__name__.lower(),
        native_enum=False,
        create_constraint=True,
        length=20,
        values_callable=lambda e: [m.value for m in e],
    )


class FocusProfile(Base):
    __tablename__ = "focus_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    duration_min: Mapped[int]
    mode: Mapped[Mode] = mapped_column(enum_column(Mode), default=Mode.SOFT)
    site_mode: Mapped[ListMode] = mapped_column(enum_column(ListMode), default=ListMode.BLACK)
    app_mode: Mapped[ListMode] = mapped_column(enum_column(ListMode), default=ListMode.BLACK)
    unlock_policy: Mapped[UnlockPolicy] = mapped_column(
        enum_column(UnlockPolicy), default=UnlockPolicy.NONE
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey("project.id", ondelete="SET NULL"))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("task.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now, onupdate=utc_now)

    rules: Mapped[list["FocusRule"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan", order_by="FocusRule.id"
    )
    project: Mapped[Project | None] = relationship()
    task: Mapped[Task | None] = relationship()


class FocusRule(Base):
    __tablename__ = "focus_rule"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("focus_profile.id", ondelete="CASCADE"))
    resource_type: Mapped[ResourceType] = mapped_column(enum_column(ResourceType))
    kind: Mapped[RuleKind] = mapped_column(enum_column(RuleKind), default=RuleKind.LIST)
    value: Mapped[str] = mapped_column(String(500))  # домен или полный путь к exe
    title: Mapped[str | None] = mapped_column(String(200))

    profile: Mapped[FocusProfile] = relationship(back_populates="rules")


class FocusSession(Base):
    __tablename__ = "focus_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("focus_profile.id", ondelete="SET NULL")
    )
    profile_name: Mapped[str] = mapped_column(String(100))
    # Снимок профиля на момент запуска: изменение профиля не влияет на активную сессию
    profile_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    mode: Mapped[Mode] = mapped_column(enum_column(Mode))
    task_id: Mapped[int | None] = mapped_column(ForeignKey("task.id", ondelete="SET NULL"))
    started_at: Mapped[datetime] = mapped_column(UTCDateTime)
    planned_end_at: Mapped[datetime] = mapped_column(UTCDateTime)
    ended_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    status: Mapped[SessionStatus] = mapped_column(
        enum_column(SessionStatus), default=SessionStatus.ACTIVE
    )
    end_reason: Mapped[EndReason | None] = mapped_column(enum_column(EndReason))
    unlock_hash: Mapped[str | None] = mapped_column(String(200))

    block_events: Mapped[list["FocusBlockEvent"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="FocusBlockEvent.id"
    )
    task: Mapped[Task | None] = relationship()


class FocusBlockEvent(Base):
    __tablename__ = "focus_block_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("focus_session.id", ondelete="CASCADE"))
    occurred_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)
    resource_type: Mapped[ResourceType] = mapped_column(enum_column(ResourceType))
    target: Mapped[str] = mapped_column(String(500))
    action: Mapped[BlockAction] = mapped_column(enum_column(BlockAction))

    session: Mapped[FocusSession] = relationship(back_populates="block_events")
