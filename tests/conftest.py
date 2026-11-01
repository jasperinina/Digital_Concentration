import pytest

from app.core.db import init_db


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def session_factory(db_path):
    return init_db(db_path)


@pytest.fixture
def session(session_factory):
    with session_factory() as s:
        yield s
