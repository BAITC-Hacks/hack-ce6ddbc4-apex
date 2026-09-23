import atexit
import os
import shutil
import tempfile
from contextlib import closing
from pathlib import Path

# Before any app import: settings reads DATABASE_PATH once, when app.config is imported,
# so overriding it inside a fixture would be too late. Tests only ever write to a temporary database.
TEST_DIR = Path(tempfile.mkdtemp(prefix="tandau-tests-"))
atexit.register(shutil.rmtree, TEST_DIR, ignore_errors=True)
os.environ["DATABASE_PATH"] = str(TEST_DIR / "test.db")  # plain assignment: neither .env nor the shell can override it
os.environ.setdefault("SECRET_KEY", "tests-only-secret-key")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import db  # noqa: E402
from app.config import settings  # noqa: E402
from app.main import create_app  # noqa: E402
from matcher.data import load_catalog  # noqa: E402

assert settings.database_path.parent == TEST_DIR, "tests must not touch var/tandau.db"


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def catalog():
    return load_catalog(settings.data_path)


@pytest.fixture
def fresh_db():
    """Empty tables plus the demo user before the test. Safe: every call opens its own connection."""
    with closing(db.connect()) as conn:
        conn.executescript("DROP TABLE IF EXISTS shortlist; DROP TABLE IF EXISTS searches; DROP TABLE IF EXISTS users;")
    db.init_db()
    db.seed_demo_user()
    yield


@pytest.fixture
def guest(client, fresh_db):
    """Signed-out client on a clean database."""
    client.cookies.clear()
    yield client
    client.cookies.clear()
