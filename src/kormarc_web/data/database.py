# TAG:SPEC-WEB-001:API:RECORDS
"""
SQLite database connection management
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Database:
    """SQLite database connection manager"""

    def __init__(self, db_path: str = "data/kormarc_prototype_100.db"):
        self.db_path = db_path
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a database connection with context manager"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()


# Singleton instance
_db = Database()


def get_db() -> Database:
    """Get database instance"""
    return _db
