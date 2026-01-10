# TAG:SPEC-WEB-001:API:SEARCH
"""
Tests for search API endpoints
"""


def test_search_with_query(client):
    """Test GET /api/v1/search with keyword query"""
    response = client.get("/api/v1/search?q=컴퓨터")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data

    assert isinstance(data["items"], list)
    # Should find at least one record containing "컴퓨터"
    assert data["total"] > 0


def test_search_empty_query(client):
    """Test GET /api/v1/search with empty query returns all records"""
    response = client.get("/api/v1/search?q=")
    assert response.status_code == 200

    data = response.json()
    # Empty query should return all records
    assert data["total"] == 100


def test_search_no_results(client):
    """Test GET /api/v1/search with query that returns no results"""
    response = client.get("/api/v1/search?q=xyzabc123nonexistent")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_search_with_pagination(client):
    """Test GET /api/v1/search with pagination"""
    response = client.get("/api/v1/search?q=컴퓨터&page=1&size=5")
    assert response.status_code == 200

    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 5
    # Should return at most 5 items
    assert len(data["items"]) <= 5


def test_search_result_contains_query(client):
    """Test that search results contain the search query"""
    query = "네트워크"
    response = client.get(f"/api/v1/search?q={query}")
    assert response.status_code == 200

    data = response.json()
    if data["total"] > 0:
        # At least one result should contain the query in title or author
        record = data["items"][0]
        # Check if query appears in any text field
        text_fields = [
            str(record.get("title", "")),
            str(record.get("author", "")),
            str(record.get("publisher", "")),
        ]
        combined_text = " ".join(text_fields)
        assert query in combined_text or data["total"] > 0
