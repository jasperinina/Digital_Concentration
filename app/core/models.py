"""Общие модели данных.

Project и Task — минимальная версия для привязки профилей концентрации к задачам.
Подсистема учета времени расширяет эти модели, не меняя существующие поля
(см. соглашение о взаимодействии подсистем).
"""

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base, UTCDateTime, utc_now


class Project(Base):
    __tablename__ = "project"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("project.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    planned_minutes: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=utc_now)

    project: Mapped[Project] = relationship(back_populates="tasks")

    @property
    def full_name(self) -> str:
        return f"{self.project.name} / {self.name}"


class AppSetting(Base):
    """Настройки «ключ — значение». Ключи имеют префикс подсистемы: focus., tt."""

    __tablename__ = "app_setting"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(1000))
