# TAG:SPEC-WEB-001:API:RECORDS
"""
Records API endpoints
"""

from fastapi import APIRouter, HTTPException, Query

from kormarc_web.data.repositories import RecordRepository
from kormarc_web.schemas.pagination import PaginatedResponse
from kormarc_web.schemas.record import RecordDetail, RecordResponse

router = APIRouter(prefix="/api/v1/records", tags=["records"])


@router.get("", response_model=PaginatedResponse[RecordResponse])
async def get_records(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    size: int = Query(default=20, ge=1, le=100, description="Items per page"),
):
    """Get paginated list of KORMARC records"""
    # Validate pagination parameters
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be >= 1")

    repo = RecordRepository()

    # Calculate offset
    offset = (page - 1) * size

    # Get total count and records
    total = repo.get_total_count()
    records = repo.get_records(offset=offset, limit=size)

    return PaginatedResponse(
        items=[RecordResponse(**record) for record in records],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{record_id}", response_model=RecordDetail)
async def get_record(record_id: str):
    """Get a single KORMARC record by ID"""
    repo = RecordRepository()
    record = repo.get_record_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail=f"Record not found: {record_id}")

    return RecordDetail(**record)
