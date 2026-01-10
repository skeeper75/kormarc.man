# TAG:SPEC-WEB-001:INIT
"""
Pytest configuration and fixtures for KORMARC Web API tests
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create FastAPI test client"""
    from kormarc_web.main import app

    return TestClient(app)


@pytest.fixture
def db_path():
    """Database path for testing"""
    return "data/kormarc_prototype_100.db"
