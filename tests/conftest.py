import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import create_app
from matcher.data import load_catalog


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def catalog():
    return load_catalog(settings.data_path)
