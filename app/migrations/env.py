"""Окружение Alembic.

Адрес БД берется из параметра sqlalchemy.url, если он задан (так делает app.core.db.migrate),
иначе используется файл БД приложения по умолчанию.
"""

from logging.config import fileConfig

from alembic import context

import app.core.models  # noqa: F401  регистрация таблиц в метаданных
import app.focus.domain.models  # noqa: F401
from app.core.db import Base, create_db_engine, default_db_path

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = config.get_main_option("sqlalchemy.url")
    if url:
        from sqlalchemy import create_engine

        engine = create_engine(url)
    else:
        engine = create_db_engine(default_db_path())

    with engine.connect() as connection:
        # batch-режим нужен для изменения существующих таблиц в SQLite
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
