"""Test suite for SQLite database schema and data integrity.

This module tests the database schema for storing KORMARC records
with TOON/ULID conversion support.
"""

import json
from datetime import datetime
from pathlib import Path

import aiosqlite
import pytest

from kormarc.models import Record
from kormarc.parser import KORMARCParser


@pytest.fixture
async def test_db_path(tmp_path: Path) -> Path:
    """Create test database path."""
    return tmp_path / "test_kormarc.db"


@pytest.fixture
async def db_connection(test_db_path: Path):
    """Create and initialize database connection."""
    db_path = test_db_path
    # Import database module
    from scripts.db_schema import create_schema, get_connection

    await create_schema(db_path)
    conn = await get_connection(db_path)
    try:
        yield conn
    finally:
        await conn.close()


@pytest.fixture
def sample_kormarc_data() -> str:
    """Sample KORMARC record for testing."""
    return """00714cam  2200205 a 4500
001 89012345
020  |a8956789012
245 10|aKORMARC 테스트 도서|b온라인 카탈로그 예시
260  |a서울|b출판사|c2025
300  |a300 p.|b삽화|c24 cm
"""


@pytest.fixture
def sample_record(sample_kormarc_data: str) -> Record:
    """Parse sample KORMARC record."""
    parser = KORMARCParser()
    return parser.parse(sample_kormarc_data)


class TestDatabaseSchema:
    """Test database schema creation and structure."""

    @pytest.mark.asyncio
    async def test_schema_creation(self, test_db_path: Path):
        """Test that database schema is created correctly."""
        from scripts.db_schema import create_schema

        await create_schema(test_db_path)

        assert test_db_path.exists(), "Database file should be created"

        async with aiosqlite.connect(test_db_path) as conn:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='kormarc_records'"
            )
            result = await cursor.fetchone()
            assert result is not None, "kormarc_records table should exist"

    @pytest.mark.asyncio
    async def test_table_columns(self, db_connection):
        """Test that all required columns exist."""
        cursor = await db_connection.execute("PRAGMA table_info(kormarc_records)")
        columns = await cursor.fetchall()
        column_names = {col[1] for col in columns}

        required_columns = {
            "id",
            "isbn",
            "category",
            "leader",
            "control_fields",
            "data_fields",
            "toon_format",
            "ulid",
            "raw_kormarc",
            "created_at",
        }

        assert required_columns.issubset(column_names), (
            f"Missing columns: {required_columns - column_names}"
        )

    @pytest.mark.asyncio
    async def test_indexes(self, db_connection):
        """Test that required indexes are created."""
        cursor = await db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='kormarc_records'"
        )
        indexes = await cursor.fetchall()
        index_names = {idx[0] for idx in indexes}

        # Check for ISBN unique index
        assert any("isbn" in idx.lower() for idx in index_names), "ISBN index should exist"


class TestRecordInsertion:
    """Test KORMARC record insertion into database."""

    @pytest.mark.asyncio
    async def test_insert_single_record(
        self, db_connection, sample_record: Record, sample_kormarc_data: str
    ):
        """Test inserting a single KORMARC record."""
        from scripts.db_schema import insert_record

        isbn = "8956789012"
        category = "general"

        record_id = await insert_record(
            db_connection, sample_record, isbn, category, sample_kormarc_data
        )

        assert record_id is not None, "Record ID should be returned"

        # Verify record was inserted
        cursor = await db_connection.execute(
            "SELECT * FROM kormarc_records WHERE id = ?", (record_id,)
        )
        row = await cursor.fetchone()

        assert row is not None, "Record should be retrievable"
        assert row[1] == isbn, "ISBN should match"

    @pytest.mark.asyncio
    async def test_insert_duplicate_isbn(
        self, db_connection, sample_record: Record, sample_kormarc_data: str
    ):
        """Test that duplicate ISBNs are rejected."""
        from scripts.db_schema import insert_record

        isbn = "8956789012"
        category = "general"

        # First insert should succeed
        await insert_record(db_connection, sample_record, isbn, category, sample_kormarc_data)

        # Second insert should fail
        with pytest.raises(Exception):  # IntegrityError for duplicate ISBN
            await insert_record(db_connection, sample_record, isbn, category, sample_kormarc_data)

    @pytest.mark.asyncio
    async def test_json_field_storage(
        self, db_connection, sample_record: Record, sample_kormarc_data: str
    ):
        """Test that control_fields and data_fields are stored as valid JSON."""
        from scripts.db_schema import insert_record

        isbn = "8956789012"
        category = "general"

        record_id = await insert_record(
            db_connection, sample_record, isbn, category, sample_kormarc_data
        )

        cursor = await db_connection.execute(
            "SELECT control_fields, data_fields FROM kormarc_records WHERE id = ?",
            (record_id,),
        )
        row = await cursor.fetchone()

        # Verify JSON is parseable
        control_fields = json.loads(row[0])
        data_fields = json.loads(row[1])

        assert isinstance(control_fields, list), "control_fields should be a list"
        assert isinstance(data_fields, list), "data_fields should be a list"


class TestTOONConversion:
    """Test TOON format conversion from KORMARC records."""

    @pytest.mark.asyncio
    async def test_toon_conversion_fields(self, db_connection, sample_record: Record):
        """Test that TOON conversion extracts required fields."""
        from scripts.db_schema import convert_to_toon

        toon_data = convert_to_toon(sample_record)

        assert "title" in toon_data, "TOON should include title"
        assert "authors" in toon_data, "TOON should include authors"
        assert "publisher" in toon_data, "TOON should include publisher"
        assert "year" in toon_data, "TOON should include year"

    @pytest.mark.asyncio
    async def test_toon_json_serializable(self, db_connection, sample_record: Record):
        """Test that TOON data is JSON serializable."""
        from scripts.db_schema import convert_to_toon

        toon_data = convert_to_toon(sample_record)

        # Should not raise exception
        json_str = json.dumps(toon_data, ensure_ascii=False)
        assert len(json_str) > 0, "TOON data should be JSON serializable"


class TestULIDGeneration:
    """Test ULID generation for records."""

    @pytest.mark.asyncio
    async def test_ulid_uniqueness(self, db_connection, sample_record: Record):
        """Test that ULIDs are unique."""
        from scripts.db_schema import generate_ulid

        ulids = [generate_ulid() for _ in range(100)]

        assert len(set(ulids)) == 100, "All ULIDs should be unique"

    @pytest.mark.asyncio
    async def test_ulid_format(self, db_connection):
        """Test that ULID follows correct format."""
        from scripts.db_schema import generate_ulid

        ulid = generate_ulid()

        assert len(ulid) == 26, "ULID should be 26 characters"
        assert ulid.islower(), "ULID should be lowercase (Crockford's Base32)"


class TestDataIntegrity:
    """Test data integrity constraints."""

    @pytest.mark.asyncio
    async def test_raw_kormarc_preservation(
        self, db_connection, sample_record: Record, sample_kormarc_data: str
    ):
        """Test that raw KORMARC data is preserved."""
        from scripts.db_schema import insert_record

        isbn = "8956789012"
        category = "general"

        record_id = await insert_record(
            db_connection, sample_record, isbn, category, sample_kormarc_data
        )

        cursor = await db_connection.execute(
            "SELECT raw_kormarc FROM kormarc_records WHERE id = ?", (record_id,)
        )
        row = await cursor.fetchone()

        assert row[0] == sample_kormarc_data, "Raw KORMARC data should be preserved"

    @pytest.mark.asyncio
    async def test_timestamp_tracking(
        self, db_connection, sample_record: Record, sample_kormarc_data: str
    ):
        """Test that created_at timestamp is tracked."""
        from scripts.db_schema import insert_record

        isbn = "8956789012"
        category = "general"

        record_id = await insert_record(
            db_connection, sample_record, isbn, category, sample_kormarc_data
        )

        cursor = await db_connection.execute(
            "SELECT created_at FROM kormarc_records WHERE id = ?", (record_id,)
        )
        row = await cursor.fetchone()

        # Parse timestamp
        created_at = datetime.fromisoformat(row[0])
        assert created_at <= datetime.now(), "created_at should be in the past"


class TestBulkOperations:
    """Test bulk database operations for large-scale data processing."""

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, db_connection):
        """Test bulk insert performance."""
        from scripts.db_schema import bulk_insert_records

        # Create 100 sample records
        records = []
        for i in range(100):
            isbn = f"978{8956789012 + i:010d}"  # Generate unique ISBNs
            category = "general"
            kormarc_data = f"00714cam  2200205 a 4500\n001 TEST{i:010d}\n245 10|aTest Book {i}\n"

            records.append((isbn, category, kormarc_data))

        # Bulk insert should complete quickly
        import time

        start = time.time()
        inserted_count = await bulk_insert_records(db_connection, records)
        duration = time.time() - start

        assert inserted_count == 100, "All records should be inserted"
        assert duration < 5.0, f"Bulk insert should be fast (took {duration:.2f}s)"

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, db_connection):
        """Test that transactions roll back on error."""
        from scripts.db_schema import bulk_insert_records

        # Create records with one invalid record
        records = [
            ("1234567890", "general", "00714cam  2200205 a 4500\n001 1234567890\n"),
            ("invalid-isbn", "general", "invalid data"),  # This should fail
        ]

        with pytest.raises(Exception):
            await bulk_insert_records(db_connection, records)

        # Verify no records were inserted
        cursor = await db_connection.execute("SELECT COUNT(*) FROM kormarc_records")
        count = await cursor.fetchone()
        assert count[0] == 0, "Transaction should have rolled back"


class TestQueryPerformance:
    """Test database query performance."""

    @pytest.mark.asyncio
    async def test_query_by_isbn(self, db_connection, sample_record: Record):
        """Test querying records by ISBN."""
        from scripts.db_schema import get_record_by_isbn, insert_record

        isbn = "8956789012"
        category = "general"

        await insert_record(db_connection, sample_record, isbn, category, "test data")

        record = await get_record_by_isbn(db_connection, isbn)

        assert record is not None, "Record should be found"
        assert record["isbn"] == isbn, "ISBN should match"

    @pytest.mark.asyncio
    async def test_query_by_category(self, db_connection):
        """Test querying records by category."""
        from scripts.db_schema import bulk_insert_records, get_records_by_category

        # Insert records with different categories
        records = []
        for i in range(50):
            category = "general" if i % 2 == 0 else "academic"
            isbn = f"978{8956789012 + i:010d}"  # Generate unique ISBNs
            kormarc_data = f"00714cam  2200205 a 4500\n001 TEST{i:010d}\n245 10|aTest Book {i}\n"
            records.append((isbn, category, kormarc_data))

        await bulk_insert_records(db_connection, records)

        general_records = await get_records_by_category(db_connection, "general")

        assert len(general_records) == 25, "Should return 25 general records"
