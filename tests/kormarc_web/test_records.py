# TAG:SPEC-WEB-001:API:RECORDS
"""
Tests for records API endpoints
"""


def test_get_records_list(client):
    """Test GET /api/v1/records returns paginated list"""
    response = client.get("/api/v1/records")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

    assert isinstance(data["items"], list)
    assert data["total"] == 100  # We have 100 records in test DB
    assert data["page"] == 1
    assert data["size"] == 20


def test_get_records_with_pagination(client):
    """Test GET /api/v1/records with pagination parameters"""
    response = client.get("/api/v1/records?page=2&size=10")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 10
    assert len(data["items"]) == 10


def test_get_records_invalid_page(client):
    """Test GET /api/v1/records with invalid page number"""
    response = client.get("/api/v1/records?page=0")
    # FastAPI returns 422 for validation errors
    assert response.status_code in [400, 422]


def test_get_single_record(client):
    """Test GET /api/v1/records/{record_id} returns record details"""
    # First, get a valid record ID from the list
    list_response = client.get("/api/v1/records?size=1")
    first_record = list_response.json()["items"][0]
    record_id = first_record["toon_id"]

    # Now fetch the specific record
    response = client.get(f"/api/v1/records/{record_id}")
    assert response.status_code == 200

    data = response.json()
    assert "toon_id" in data
    assert "title" in data
    assert "author" in data
    assert data["toon_id"] == record_id


def test_get_nonexistent_record(client):
    """Test GET /api/v1/records/{record_id} with non-existent ID"""
    response = client.get("/api/v1/records/nonexistent-id-12345")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_record_response_schema(client):
    """Test that record response contains required fields"""
    response = client.get("/api/v1/records?size=1")
    assert response.status_code == 200

    data = response.json()
    record = data["items"][0]

    # Required fields from database schema
    required_fields = [
        "toon_id",
        "timestamp_ms",
        "created_at",
        "record_type",
        "isbn",
    ]

    for field in required_fields:
        assert field in record

    # Optional but expected fields
    expected_fields = ["title", "author", "publisher", "pub_year"]
    for field in expected_fields:
        assert field in record
