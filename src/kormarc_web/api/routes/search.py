# TAG:SPEC-WEB-001:API:SEARCH
"""
Search API endpoints
"""

from fastapi import APIRouter, Query

from kormarc_web.data.repositories import SearchRepository
from kormarc_web.schemas.pagination import PaginatedResponse
from kormarc_web.schemas.record import RecordResponse

router = APIRouter(prefix="/api/v1/search", tags=["search"])


@router.get("", response_model=PaginatedResponse[RecordResponse])
async def search_records(
    q: str = Query(default="", description="Search query"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
):
    """Search KORMARC records using FTS5 full-text search"""
    repo = SearchRepository()

    # Calculate offset
    offset = (page - 1) * size

    # Search records
    records, total = repo.search_records(query=q, offset=offset, limit=size)

    return PaginatedResponse(
        items=[RecordResponse(**record) for record in records],
        total=total,
        page=page,
        size=size,
    )
