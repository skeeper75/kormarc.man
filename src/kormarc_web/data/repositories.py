# TAG:SPEC-WEB-001:API:RECORDS
"""
Data access repositories for KORMARC records
"""

import json
from typing import Any

from kormarc_web.data.database import get_db


class SearchRepository:
    """Repository for FTS5 search operations"""

    def __init__(self):
        self.db = get_db()

    def search_records(
        self, query: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[dict[str, Any]], int]:
        """Search records using FTS5 full-text search

        Returns:
            Tuple of (records, total_count)
        """
        # If query is empty, return all records
        if not query or query.strip() == "":
            # Get total count
            with self.db.get_connection() as conn:
                count_cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_records")
                total = count_cursor.fetchone()["count"]

            # Get records
            query_sql = """
                SELECT
                    toon_id,
                    timestamp_ms,
                    created_at,
                    record_type,
                    isbn,
                    title,
                    author,
                    publisher,
                    pub_year,
                    kdc_code
                FROM kormarc_records
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """

            with self.db.get_connection() as conn:
                cursor = conn.execute(query_sql, (limit, offset))
                rows = cursor.fetchall()
                records = [dict(row) for row in rows]

            return records, total

        # FTS5 search
        # First get total count
        count_query = """
            SELECT COUNT(*) as count
            FROM kormarc_fts
            WHERE kormarc_fts MATCH ?
        """

        with self.db.get_connection() as conn:
            count_cursor = conn.execute(count_query, (query,))
            total = count_cursor.fetchone()["count"]

        # Get matching records with details from main table
        search_query = """
            SELECT
                r.toon_id,
                r.timestamp_ms,
                r.created_at,
                r.record_type,
                r.isbn,
                r.title,
                r.author,
                r.publisher,
                r.pub_year,
                r.kdc_code
            FROM kormarc_fts
            JOIN kormarc_records r ON r.rowid = kormarc_fts.rowid
            WHERE kormarc_fts MATCH ?
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        """

        with self.db.get_connection() as conn:
            cursor = conn.execute(search_query, (query, limit, offset))
            rows = cursor.fetchall()
            records = [dict(row) for row in rows]

        return records, total


class RecordRepository:
    """Repository for KORMARC record data access"""

    def __init__(self):
        self.db = get_db()

    def get_total_count(self) -> int:
        """Get total number of records"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_records")
            row = cursor.fetchone()
            return row["count"]

    def get_records(self, offset: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """Get paginated list of records"""
        query = """
            SELECT
                toon_id,
                timestamp_ms,
                created_at,
                record_type,
                isbn,
                title,
                author,
                publisher,
                pub_year,
                kdc_code
            FROM kormarc_records
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """

        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_record_by_id(self, toon_id: str) -> dict[str, Any] | None:
        """Get a single record by TOON ID"""
        query = """
            SELECT
                toon_id,
                timestamp_ms,
                created_at,
                record_type,
                isbn,
                title,
                author,
                publisher,
                pub_year,
                kdc_code,
                record_length,
                record_status,
                raw_kormarc,
                parsed_data
            FROM kormarc_records
            WHERE toon_id = ?
        """

        with self.db.get_connection() as conn:
            cursor = conn.execute(query, (toon_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            record = dict(row)

            # Parse JSON field if present
            if record.get("parsed_data"):
                try:
                    record["parsed_data"] = json.loads(record["parsed_data"])
                except (json.JSONDecodeError, TypeError):
                    pass

            return record
