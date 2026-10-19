from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service


@pytest.fixture
def service():
    fake = MagicMock()
    fake.ping.return_value = True
    return fake


@pytest.fixture
def client(service):
    # Los tests nunca tocan el Docker real: se inyecta un servicio falso.
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
