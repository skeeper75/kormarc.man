#!/usr/bin/env python3
"""
KORMARC FTS5 Full-Text Search Index Rebuild Script

This script rebuilds the FTS5 full-text search index for KORMARC records.
Use this when:
- FTS5 search returns empty results
- Database records are updated but search doesn't reflect changes
- Index becomes corrupted

Usage:
    python scripts/rebuild_fts_index.py
"""

import sqlite3
from pathlib import Path


def rebuild_fts_index(db_path: str = "data/kormarc_prototype_100.db") -> None:
    """Rebuild the FTS5 full-text search index.

    Args:
        db_path: Path to the SQLite database file
    """
    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    print(f"Rebuilding FTS5 index for: {db_path}")

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        # Check if FTS table exists
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='kormarc_fts'"
        )
        fts_exists = cursor.fetchone() is not None

        # Step 1: Drop existing FTS table if it exists
        if fts_exists:
            print("Dropping existing FTS5 table...")
            conn.execute("DROP TABLE IF EXISTS kormarc_fts")
            conn.commit()

        # Step 2: Create new FTS5 virtual table with external content
        print("Creating FTS5 virtual table...")
        create_fts_sql = """
            CREATE VIRTUAL TABLE kormarc_fts USING fts5(
                title,
                author,
                publisher,
                content=kormarc_records,
                content_rowid=rowid,
                tokenize='unicode61 remove_diacritics 2'
            )
        """
        conn.execute(create_fts_sql)
        conn.commit()

        # Step 3: Populate the FTS index
        print("Populating FTS5 index...")
        conn.execute(
            "INSERT INTO kormarc_fts(rowid, title, author, publisher) SELECT rowid, title, author, publisher FROM kormarc_records"
        )
        conn.commit()

        # Step 4: Verify index population
        cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_fts")
        fts_count = cursor.fetchone()["count"]

        cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_records")
        records_count = cursor.fetchone()["count"]

        print("\nFTS5 Index rebuild complete!")
        print(f"  - Records in kormarc_records: {records_count}")
        print(f"  - Records in kormarc_fts: {fts_count}")

        if fts_count == records_count:
            print("  - Index verification: PASSED")
        else:
            print("  - Index verification: WARNING (Count mismatch!)")

        # Step 5: Test search functionality
        print("\nTesting search functionality...")
        test_queries = ["컴퓨터", "ai", "network"]

        for query in test_queries:
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM kormarc_fts WHERE kormarc_fts MATCH ?", (query,)
            )
            count = cursor.fetchone()["count"]
            print(f"  - Query '{query}': {count} results")


def verify_fts_index(db_path: str = "data/kormarc_prototype_100.db") -> None:
    """Verify the FTS5 index status without rebuilding.

    Args:
        db_path: Path to the SQLite database file
    """
    db_file = Path(db_path)
    if not db_file.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    print(f"Verifying FTS5 index for: {db_path}")

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        # Check table existence
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='kormarc_fts'"
        )
        fts_exists = cursor.fetchone() is not None

        if not fts_exists:
            print("ERROR: FTS5 table does not exist!")
            return

        # Get counts
        cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_records")
        records_count = cursor.fetchone()["count"]

        cursor = conn.execute("SELECT COUNT(*) as count FROM kormarc_fts")
        fts_count = cursor.fetchone()["count"]

        print("\nFTS5 Index Status:")
        print(f"  - Records in kormarc_records: {records_count}")
        print(f"  - Records in kormarc_fts: {fts_count}")

        if fts_count == records_count:
            print("  - Status: HEALTHY")
        else:
            print("  - Status: NEEDS REBUILD")

        # Show FTS schema
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='kormarc_fts'"
        )
        schema = cursor.fetchone()
        if schema:
            print(f"\nFTS5 Schema:\n{schema['sql']}")


if __name__ == "__main__":
    import sys

    db_path = "data/kormarc_prototype_100.db"

    if len(sys.argv) > 1:
        if sys.argv[1] == "verify":
            verify_fts_index(db_path)
        elif sys.argv[1] == "rebuild":
            rebuild_fts_index(db_path)
        else:
            print("Usage: python rebuild_fts_index.py [verify|rebuild]")
            sys.exit(1)
    else:
        # Default: verify first, then rebuild if needed
        verify_fts_index(db_path)
        print("\n" + "=" * 50)
        response = input("\nRebuild FTS5 index? (y/N): ")
        if response.lower() == "y":
            rebuild_fts_index(db_path)
