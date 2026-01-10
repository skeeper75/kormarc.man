"""
Test Fixtures for Integration Tests

Mock API responses and test data
"""

from tests.test_integration.fixtures.mock_api_responses import (
    SAMPLE_EMPTY_MARCXML_RESPONSE,
    SAMPLE_ISBN,
    SAMPLE_KORMARC_DATA,
    SAMPLE_MARCXML_RESPONSE,
    SAMPLE_SCRAPER_DATA,
    create_mock_api_error_response,
    create_mock_marcxml,
    create_mock_scraper_data,
)

__all__ = [
    "SAMPLE_ISBN",
    "SAMPLE_MARCXML_RESPONSE",
    "SAMPLE_EMPTY_MARCXML_RESPONSE",
    "SAMPLE_KORMARC_DATA",
    "SAMPLE_SCRAPER_DATA",
    "create_mock_marcxml",
    "create_mock_scraper_data",
    "create_mock_api_error_response",
]
