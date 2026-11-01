"""Подключение к локальной базе SQLite и общие типы столбцов."""

import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import DateTime, Engine, MetaData, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.types import TypeDecorator

APP_DIR_NAME = "NormDev"
DB_FILE_NAME = "normdev.db"

# Единые имена ограничений нужны Alembic для изменения таблиц SQLite
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UTCDateTime(TypeDecorator):
    """Дата и время в UTC. SQLite не хранит часовой пояс, поэтому значения
    записываются без него, а при чтении снова помечаются как UTC."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Ожидается дата и время с часовым поясом")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect):
        return value.replace(tzinfo=UTC) if value is not None else None


def utc_now() -> datetime:
    return datetime.now(UTC)


def default_db_path() -> Path:
    """Путь к файлу БД: переменная NORMDEV_DB или %LOCALAPPDATA%\\NormDev\\normdev.db."""
    override = os.environ.get("NORMDEV_DB")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / APP_DIR_NAME / DB_FILE_NAME


def db_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def create_db_engine(path: Path | None = None) -> Engine:
    path = path or default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(db_url(path))

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def migrate(path: Path) -> None:
    """Приводит схему БД к последней версии миграций Alembic."""
    from alembic import command
    from alembic.config import Config

    config = Config()
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parent.parent / "migrations")
    )
    config.set_main_option("sqlalchemy.url", db_url(path))
    command.upgrade(config, "head")


def init_db(path: Path | None = None) -> sessionmaker:
    """Обновляет схему и возвращает фабрику сессий SQLAlchemy."""
    path = path or default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    migrate(path)
    return sessionmaker(create_db_engine(path), expire_on_commit=False)
