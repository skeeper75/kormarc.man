"""Database schema and operations for KORMARC record storage.

This module provides SQLite database schema and operations for storing
KORMARC records with TOON/ULID conversion support.
"""

import json
from pathlib import Path
from typing import Any

import aiosqlite

from kormarc.models import Record


async def create_schema(db_path: Path) -> None:
    """Create database schema for KORMARC records.

    Args:
        db_path: Path to database file
    """
    async with aiosqlite.connect(db_path) as conn:
        # Create kormarc_records table
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kormarc_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                leader TEXT NOT NULL,
                control_fields TEXT NOT NULL,
                data_fields TEXT NOT NULL,
                toon_format TEXT NOT NULL,
                ulid TEXT NOT NULL,
                raw_kormarc TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create index on ISBN for fast lookups
        await conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_kormarc_isbn
            ON kormarc_records(isbn)
        """
        )

        # Create index on category for filtering
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_kormarc_category
            ON kormarc_records(category)
        """
        )

        # Create index on ULID for ULID-based lookups
        await conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_kormarc_ulid
            ON kormarc_records(ulid)
        """
        )

        await conn.commit()


async def get_connection(db_path: Path) -> aiosqlite.Connection:
    """Get database connection.

    Args:
        db_path: Path to database file

    Returns:
        Database connection
    """
    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA foreign_keys = ON")
    await conn.execute("PRAGMA journal_mode = WAL")
    return conn


async def insert_record(
    conn: aiosqlite.Connection,
    record: Record,
    isbn: str,
    category: str,
    raw_kormarc: str,
    commit: bool = True,
) -> int:
    """Insert a KORMARC record into the database.

    Args:
        conn: Database connection
        record: Parsed KORMARC record
        isbn: ISBN identifier
        category: Record category (general, academic, serial, comic)
        raw_kormarc: Raw KORMARC data
        commit: Whether to commit immediately (default: True)

    Returns:
        Inserted record ID

    Raises:
        IntegrityError: If ISBN already exists
    """
    # Convert record to TOON format
    toon_data = convert_to_toon(record)
    toon_json = json.dumps(toon_data, ensure_ascii=False)

    # Generate ULID
    ulid = generate_ulid()

    # Serialize control fields and data fields
    control_fields_json = json.dumps(
        [cf.model_dump() for cf in record.control_fields], ensure_ascii=False
    )
    data_fields_json = json.dumps(
        [df.model_dump() for df in record.data_fields], ensure_ascii=False
    )

    # Insert record
    cursor = await conn.execute(
        """
        INSERT INTO kormarc_records (
            isbn, category, leader, control_fields, data_fields,
            toon_format, ulid, raw_kormarc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            isbn,
            category,
            str(record.leader),
            control_fields_json,
            data_fields_json,
            toon_json,
            ulid,
            raw_kormarc,
        ),
    )

    if commit:
        await conn.commit()

    return cursor.lastrowid


async def bulk_insert_records(
    conn: aiosqlite.Connection, records: list[tuple[str, str, str]]
) -> int:
    """Bulk insert multiple KORMARC records.

    Args:
        conn: Database connection
        records: List of (isbn, category, raw_kormarc) tuples

    Returns:
        Number of records inserted

    Raises:
        IntegrityError: If any ISBN already exists
    """
    from kormarc.parser import KORMARCParser

    parser = KORMARCParser()
    inserted_count = 0

    try:
        # Begin transaction
        await conn.execute("BEGIN")

        for isbn, category, raw_kormarc in records:
            record = parser.parse(raw_kormarc)
            await insert_record(conn, record, isbn, category, raw_kormarc, commit=False)
            inserted_count += 1

        # Commit if all inserts succeed
        await conn.commit()

    except Exception:
        # Rollback on error
        await conn.rollback()
        raise

    return inserted_count


async def get_record_by_isbn(conn: aiosqlite.Connection, isbn: str) -> dict[str, Any] | None:
    """Get a record by ISBN.

    Args:
        conn: Database connection
        isbn: ISBN to search for

    Returns:
        Record dictionary or None if not found
    """
    cursor = await conn.execute(
        """
        SELECT * FROM kormarc_records WHERE isbn = ?
        """,
        (isbn,),
    )

    row = await cursor.fetchone()
    if row is None:
        return None

    # Convert row to dictionary
    columns = [
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
    ]

    return {col: val for col, val in zip(columns, row)}


async def get_records_by_category(
    conn: aiosqlite.Connection, category: str, limit: int = 100
) -> list[dict[str, Any]]:
    """Get records by category.

    Args:
        conn: Database connection
        category: Category to filter by
        limit: Maximum number of records to return

    Returns:
        List of record dictionaries
    """
    cursor = await conn.execute(
        """
        SELECT * FROM kormarc_records
        WHERE category = ?
        LIMIT ?
        """,
        (category, limit),
    )

    rows = await cursor.fetchall()

    columns = [
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
    ]

    return [{col: val for col, val in zip(columns, row)} for row in rows]


def convert_to_toon(record: Record) -> dict[str, Any]:
    """Convert KORMARC record to TOON format.

    TOON (Tiny Object-Oriented Notation) is a compact JSON format
    for bibliographic data exchange.

    Args:
        record: KORMARC record

    Returns:
        TOON format dictionary
    """
    toon: dict[str, Any] = {
        "title": "",
        "subtitle": "",
        "authors": [],
        "publisher": "",
        "year": "",
        "isbn": "",
        "pages": "",
        "format": "",
    }

    # Extract data from fields
    for field in record.data_fields:
        if field.tag == "245":
            # Title and statement of responsibility
            for subfield in field.subfields:
                if subfield.code == "a":
                    toon["title"] = subfield.data
                elif subfield.code == "b":
                    toon["subtitle"] = subfield.data
                elif subfield.code == "c":
                    toon["authors"] = [subfield.data]

        elif field.tag == "260":
            # Publication information
            for subfield in field.subfields:
                if subfield.code == "b":
                    toon["publisher"] = subfield.data
                elif subfield.code == "c":
                    toon["year"] = subfield.data

        elif field.tag == "300":
            # Physical description
            for subfield in field.subfields:
                if subfield.code == "a":
                    toon["pages"] = subfield.data

    # Extract ISBN from control fields
    for control_field in record.control_fields:
        if control_field.tag == "020":
            # ISBN field
            isbn = control_field.data
            if isbn:
                toon["isbn"] = isbn

    return toon


def generate_ulid() -> str:
    """Generate a ULID (Universally Unique Lexicographically Sortable Identifier).

    ULID format: 26-character Crockford's Base32 encoded string
    Timestamp: 48 bits (10 characters)
    Randomness: 80 bits (16 characters)

    Returns:
        ULID string
    """
    import secrets
    import time

    # Crockford's Base32 alphabet
    alphabet = "0123456789abcdefghjkmnpqrstvwxyz"

    # Get current timestamp in milliseconds
    timestamp = int(time.time() * 1000)

    # Encode timestamp (48 bits)
    timestamp_chars = []
    for _ in range(10):
        timestamp_chars.append(alphabet[timestamp & 0x1F])
        timestamp >>= 5

    # Generate random data (80 bits)
    random_data = secrets.token_bytes(10)
    random_chars = []
    for byte in random_data:
        random_chars.append(alphabet[byte & 0x1F])
        random_chars.append(alphabet[(byte >> 3) & 0x1F])
        random_chars.append(alphabet[(byte >> 6) & 0x1F])

    # Combine timestamp and random data
    ulid = "".join(reversed(timestamp_chars)) + "".join(random_chars[:16])

    return ulid.lower()


async def get_statistics(conn: aiosqlite.Connection) -> dict[str, Any]:
    """Get database statistics.

    Args:
        conn: Database connection

    Returns:
        Statistics dictionary
    """
    # Total records
    cursor = await conn.execute("SELECT COUNT(*) FROM kormarc_records")
    total_count = (await cursor.fetchone())[0]

    # Records by category
    cursor = await conn.execute(
        """
        SELECT category, COUNT(*) as count
        FROM kormarc_records
        GROUP BY category
        ORDER BY count DESC
    """
    )
    category_counts = {row[0]: row[1] for row in await cursor.fetchall()}

    # Database size
    cursor = await conn.execute(
        "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()"
    )
    db_size = (await cursor.fetchone())[0]

    return {
        "total_records": total_count,
        "category_counts": category_counts,
        "database_size_bytes": db_size,
    }
