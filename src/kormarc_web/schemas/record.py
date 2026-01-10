# TAG:SPEC-WEB-001:API:RECORDS
"""
Record schemas for API responses
"""

from typing import Any

from pydantic import BaseModel, Field


class RecordResponse(BaseModel):
    """Response schema for KORMARC record"""

    toon_id: str = Field(description="Unique TOON identifier")
    timestamp_ms: int = Field(description="Timestamp in milliseconds")
    created_at: str = Field(description="Creation timestamp")
    record_type: str = Field(description="Record type (e.g., kormarc_book)")
    isbn: str = Field(description="ISBN number")
    title: str | None = Field(default=None, description="Book title")
    author: str | None = Field(default=None, description="Author name")
    publisher: str | None = Field(default=None, description="Publisher name")
    pub_year: int | None = Field(default=None, description="Publication year")
    kdc_code: str | None = Field(default=None, description="KDC classification code")

    model_config = {"from_attributes": True}


class RecordDetail(RecordResponse):
    """Detailed record response with additional fields"""

    record_length: int | None = Field(default=None, description="Record length")
    record_status: str | None = Field(default=None, description="Record status")
    raw_kormarc: str | None = Field(default=None, description="Raw KORMARC XML")
    parsed_data: Any | None = Field(default=None, description="Parsed KORMARC data")
