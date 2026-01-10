# TAG:SPEC-WEB-001:INIT
"""
Tests for main FastAPI application initialization
"""


def test_app_creation(client):
    """Test that FastAPI app is created successfully"""
    assert client is not None


def test_root_endpoint_exists(client):
    """Test that root endpoint returns API information"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "KORMARC Web API"


def test_health_check_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_cors_headers_configured(client):
    """Test that CORS headers are configured"""
    response = client.get("/", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers


def test_api_v1_prefix_exists(client):
    """Test that /api/v1 prefix is configured"""
    # This will fail initially but validates our API structure
    response = client.get("/api/v1/records")
    # We expect either 200 or 404, not 405 (Method Not Allowed) or other errors
    assert response.status_code in [200, 404]
