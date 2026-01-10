"""
KORMARC SQLite 데이터베이스 모듈

TOON 식별자와 KORMARC 레코드를 SQLite에 저장/조회하는 기능 제공
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite


class KORMARCDatabase:
    """
    KORMARC 레코드 데이터베이스

    TOON 식별자와 KORMARC 레코드를 SQLite에 저장합니다.

    Example:
        >>> db = KORMARCDatabase("kormarc.db")
        >>> await db.initialize()
        >>> await db.save_record(toon_id, record_data)
        >>> record = await db.get_record(toon_id)
    """

    def __init__(self, db_path: str | Path = "kormarc.db"):
        """
        데이터베이스 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """
        데이터베이스 초기화 및 테이블 생성

        테이블 스키마:
        - kormarc_records: TOON 레코드 저장 테이블
        """
        self._conn = await aiosqlite.connect(self.db_path)

        # WAL 모드 활성화 (성능 향상)
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA synchronous=NORMAL")

        # 테이블 생성
        await self._create_tables()

    async def _create_tables(self) -> None:
        """데이터베이스 테이블 생성 (v2 스키마)"""
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # kormarc_records 테이블 (v2)
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kormarc_records (
                -- TOON 식별자
                toon_id TEXT PRIMARY KEY,

                -- 타임스탬프 정보
                timestamp_ms INTEGER NOT NULL,
                created_at TEXT NOT NULL,

                -- 레코드 타입 및 ISBN
                record_type TEXT NOT NULL,
                isbn TEXT NOT NULL,

                -- 정규화된 필드 (v2 추가)
                title TEXT,
                author TEXT,
                publisher TEXT,
                pub_year INTEGER CHECK(pub_year IS NULL OR (pub_year >= 1000 AND pub_year <= 9999)),
                kdc_code TEXT,

                -- Leader 필드 (v2 추가)
                record_length INTEGER,
                record_status TEXT,
                impl_defined1 TEXT,
                impl_defined2 TEXT,
                indicator_count INTEGER,
                subfield_code_count INTEGER,
                base_address INTEGER,
                impl_defined3 TEXT,
                entry_map TEXT,

                -- 원본 및 파싱 데이터
                raw_kormarc TEXT NOT NULL,
                parsed_data JSON NOT NULL,

                -- 메타데이터
                scraped_at TEXT NOT NULL,
                data_source TEXT NOT NULL DEFAULT 'manual'
            )
            """
        )

        # 기본 인덱스
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON kormarc_records(timestamp_ms)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_type ON kormarc_records(record_type)"
        )
        await self._conn.execute("CREATE INDEX IF NOT EXISTS idx_isbn ON kormarc_records(isbn)")
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_scraped ON kormarc_records(scraped_at)"
        )

        # v2 복합 인덱스 (성능 최적화)
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_kdc_year ON kormarc_records(kdc_code, pub_year DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_publisher_year ON kormarc_records(publisher, pub_year DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_type_year ON kormarc_records(record_type, pub_year DESC)"
        )
        await self._conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON kormarc_records(title)")
        await self._conn.execute("CREATE INDEX IF NOT EXISTS idx_author ON kormarc_records(author)")

        # FTS5 전문 검색 테이블 (v2 추가)
        await self._conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS kormarc_fts USING fts5(
                title,
                author,
                publisher,
                content=kormarc_records,
                content_rowid=rowid,
                tokenize='unicode61 remove_diacritics 2'
            )
            """
        )

        # FTS5 자동 동기화 트리거
        await self._conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS kormarc_fts_insert AFTER INSERT ON kormarc_records BEGIN
                INSERT INTO kormarc_fts(rowid, title, author, publisher)
                VALUES (new.rowid, new.title, new.author, new.publisher);
            END
            """
        )

        await self._conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS kormarc_fts_delete AFTER DELETE ON kormarc_records BEGIN
                DELETE FROM kormarc_fts WHERE rowid = old.rowid;
            END
            """
        )

        await self._conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS kormarc_fts_update AFTER UPDATE ON kormarc_records BEGIN
                DELETE FROM kormarc_fts WHERE rowid = old.rowid;
                INSERT INTO kormarc_fts(rowid, title, author, publisher)
                VALUES (new.rowid, new.title, new.author, new.publisher);
            END
            """
        )

        await self._conn.commit()

    def _extract_field(self, parsed: dict, tag: str, subfield_code: str) -> str | None:
        """
        파싱된 MARC 데이터에서 특정 필드 추출

        Args:
            parsed: 파싱된 KORMARC 데이터
            tag: MARC 필드 태그 (예: "245", "100")
            subfield_code: 서브필드 코드 (예: "a", "b")

        Returns:
            추출된 필드 값 또는 None
        """
        data_fields = parsed.get("data_fields", [])
        for field in data_fields:
            if field.get("tag") == tag:
                for subfield in field.get("subfields", []):
                    if subfield.get("code") == subfield_code:
                        return subfield.get("data")
        return None

    def _extract_pub_year(self, parsed: dict) -> int | None:
        """
        출판년도 추출 및 정규화

        Args:
            parsed: 파싱된 KORMARC 데이터

        Returns:
            4자리 출판년도 또는 None
        """
        # 260$c 또는 264$c에서 추출
        pub_year_str = self._extract_field(parsed, "260", "c") or self._extract_field(
            parsed, "264", "c"
        )

        if not pub_year_str:
            return None

        # 숫자만 추출 (예: "2024." → 2024)
        import re

        match = re.search(r"\d{4}", pub_year_str)
        if match:
            year = int(match.group())
            # 유효한 범위 검증
            if 1000 <= year <= 9999:
                return year

        return None

    async def save_record(
        self,
        toon_id: str,
        record_data: dict[str, Any],
        scraped_at: str | None = None,
        data_source: str = "manual",
    ) -> None:
        """
        KORMARC 레코드 저장 (v2 스키마)

        Args:
            toon_id: TOON 식별자
            record_data: TOON JSON 형식 레코드 데이터
            scraped_at: 수집 시간 (ISO 8601, 없으면 현재 시간)
            data_source: 데이터 소스 (manual, api, etc.)
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # scraped_at 기본값
        if scraped_at is None:
            scraped_at = datetime.now().isoformat()

        # 타임스탬프 추출 (record_data에서)
        timestamp_str = record_data.get("timestamp", "")
        created_at = timestamp_str
        timestamp_ms = 0

        if timestamp_str:
            try:
                dt = datetime.fromisoformat(timestamp_str)
                timestamp_ms = int(dt.timestamp() * 1000)
            except (ValueError, TypeError):
                timestamp_ms = 0

        # 파싱된 데이터 추출
        parsed = record_data.get("parsed", {})

        # 정규화된 필드 추출 (v2)
        title = self._extract_field(parsed, "245", "a")
        author = self._extract_field(parsed, "100", "a") or self._extract_field(parsed, "700", "a")
        publisher = self._extract_field(parsed, "260", "b") or self._extract_field(
            parsed, "264", "b"
        )
        pub_year = self._extract_pub_year(parsed)
        kdc_code = self._extract_field(parsed, "082", "a") or self._extract_field(
            parsed, "080", "a"
        )

        # Leader 필드 추출 (v2)
        leader = parsed.get("leader", {})
        record_length = leader.get("record_length")
        record_status = leader.get("record_status")
        impl_defined1 = leader.get("impl_defined1")
        impl_defined2 = leader.get("impl_defined2")
        indicator_count = leader.get("indicator_count")
        subfield_code_count = leader.get("subfield_code_count")
        base_address = leader.get("base_address")
        impl_defined3 = leader.get("impl_defined3")
        entry_map = leader.get("entry_map")

        # 파싱된 데이터를 JSON으로 변환
        parsed_json = json.dumps(parsed, ensure_ascii=False)

        # 레코드 저장 (v2 스키마)
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO kormarc_records
            (toon_id, timestamp_ms, created_at, record_type, isbn,
             title, author, publisher, pub_year, kdc_code,
             record_length, record_status, impl_defined1, impl_defined2,
             indicator_count, subfield_code_count, base_address, impl_defined3, entry_map,
             raw_kormarc, parsed_data, scraped_at, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                toon_id,
                timestamp_ms,
                created_at,
                record_data.get("type", ""),
                record_data.get("isbn", ""),
                title,
                author,
                publisher,
                pub_year,
                kdc_code,
                record_length,
                record_status,
                impl_defined1,
                impl_defined2,
                indicator_count,
                subfield_code_count,
                base_address,
                impl_defined3,
                entry_map,
                record_data.get("raw_kormarc", ""),
                parsed_json,
                scraped_at,
                data_source,
            ),
        )

        await self._conn.commit()

    async def get_record(self, toon_id: str) -> dict[str, Any] | None:
        """
        TOON ID로 레코드 조회 (v2 스키마)

        Args:
            toon_id: TOON 식별자

        Returns:
            레코드 데이터 또는 None
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            "SELECT * FROM kormarc_records WHERE toon_id = ?",
            (toon_id,),
        )
        row = await cursor.fetchone()

        if row is None:
            return None

        # _rows_to_dicts 사용
        results = self._rows_to_dicts([row])
        return results[0] if results else None

    async def get_by_isbn(self, isbn: str) -> list[dict[str, Any]]:
        """
        ISBN으로 레코드 조회 (v2 스키마)

        Args:
            isbn: ISBN (정규화됨)

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            "SELECT * FROM kormarc_records WHERE isbn = ? ORDER BY timestamp_ms DESC",
            (isbn,),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def get_by_type(
        self, record_type: str, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        레코드 타입별 조회 (v2 스키마)

        Args:
            record_type: 레코드 타입 (kormarc_book, kormarc_serial, etc.)
            limit: 최대 반환 개수
            offset: 시작 오프셋

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            """
            SELECT * FROM kormarc_records
            WHERE record_type = ?
            ORDER BY timestamp_ms DESC
            LIMIT ? OFFSET ?
            """,
            (record_type, limit, offset),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def get_all_records(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """
        모든 레코드 조회 (페이지네이션, v2 스키마)

        Args:
            limit: 최대 반환 개수
            offset: 시작 오프셋

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            """
            SELECT * FROM kormarc_records
            ORDER BY timestamp_ms DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def count_records(self, record_type: str | None = None) -> int:
        """
        레코드 수 조회

        Args:
            record_type: 레코드 타입 (None이면 전체)

        Returns:
            레코드 수
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        if record_type is None:
            cursor = await self._conn.execute("SELECT COUNT(*) FROM kormarc_records")
        else:
            cursor = await self._conn.execute(
                "SELECT COUNT(*) FROM kormarc_records WHERE record_type = ?",
                (record_type,),
            )

        row = await cursor.fetchone()
        return row[0] if row else 0

    async def search_records(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        제목으로 레코드 검색 (레거시 호환성)

        Args:
            query: 검색어 (제목 포함)
            limit: 최대 반환 개수

        Returns:
            레코드 리스트
        """
        # FTS5 검색으로 위임
        return await self.search_by_title(query, limit)

    async def search_by_title(self, title: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        제목으로 검색 (FTS5 전문 검색 사용)

        Args:
            title: 검색 제목
            limit: 최대 반환 개수

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # FTS5 전문 검색
        cursor = await self._conn.execute(
            """
            SELECT r.* FROM kormarc_records r
            JOIN kormarc_fts f ON r.rowid = f.rowid
            WHERE kormarc_fts MATCH ?
            ORDER BY r.timestamp_ms DESC
            LIMIT ?
            """,
            (title, limit),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def search_by_author(self, author: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        저자로 검색

        Args:
            author: 검색 저자명
            limit: 최대 반환 개수

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            """
            SELECT * FROM kormarc_records
            WHERE author LIKE ?
            ORDER BY pub_year DESC
            LIMIT ?
            """,
            (f"%{author}%", limit),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def search_by_kdc(self, kdc_code: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        KDC 분류로 검색 (인덱스 사용)

        Args:
            kdc_code: KDC 분류 코드 (예: "005", "810")
            limit: 최대 반환 개수

        Returns:
            레코드 리스트 (출판년도 내림차순)
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # KDC 코드로 시작하는 레코드 검색 (복합 인덱스 활용)
        cursor = await self._conn.execute(
            """
            SELECT * FROM kormarc_records
            WHERE kdc_code LIKE ?
            ORDER BY pub_year DESC
            LIMIT ?
            """,
            (f"{kdc_code}%", limit),
        )
        rows = await cursor.fetchall()

        return self._rows_to_dicts(rows)

    async def search_by_publisher(
        self,
        publisher: str,
        year_from: int | None = None,
        year_to: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        출판사로 검색 (연도 범위 필터 포함)

        Args:
            publisher: 출판사명
            year_from: 시작 연도 (포함)
            year_to: 종료 연도 (포함)
            limit: 최대 반환 개수

        Returns:
            레코드 리스트 (출판년도 내림차순)
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # 연도 범위 필터
        if year_from and year_to:
            cursor = await self._conn.execute(
                """
                SELECT * FROM kormarc_records
                WHERE publisher LIKE ?
                  AND pub_year >= ?
                  AND pub_year <= ?
                ORDER BY pub_year DESC
                LIMIT ?
                """,
                (f"%{publisher}%", year_from, year_to, limit),
            )
        elif year_from:
            cursor = await self._conn.execute(
                """
                SELECT * FROM kormarc_records
                WHERE publisher LIKE ?
                  AND pub_year >= ?
                ORDER BY pub_year DESC
                LIMIT ?
                """,
                (f"%{publisher}%", year_from, limit),
            )
        else:
            cursor = await self._conn.execute(
                """
                SELECT * FROM kormarc_records
                WHERE publisher LIKE ?
                ORDER BY pub_year DESC
                LIMIT ?
                """,
                (f"%{publisher}%", limit),
            )

        rows = await cursor.fetchall()
        return self._rows_to_dicts(rows)

    async def advanced_search(
        self,
        title: str | None = None,
        author: str | None = None,
        publisher: str | None = None,
        kdc_code: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        record_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        고급 검색 (여러 조건 조합)

        Args:
            title: 제목 검색어
            author: 저자 검색어
            publisher: 출판사 검색어
            kdc_code: KDC 분류 코드
            year_from: 시작 연도
            year_to: 종료 연도
            record_type: 레코드 타입
            limit: 최대 반환 개수

        Returns:
            레코드 리스트
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        # 동적 쿼리 구성
        conditions = []
        params = []

        if title:
            conditions.append("title LIKE ?")
            params.append(f"%{title}%")

        if author:
            conditions.append("author LIKE ?")
            params.append(f"%{author}%")

        if publisher:
            conditions.append("publisher LIKE ?")
            params.append(f"%{publisher}%")

        if kdc_code:
            conditions.append("kdc_code LIKE ?")
            params.append(f"{kdc_code}%")

        if year_from:
            conditions.append("pub_year >= ?")
            params.append(year_from)

        if year_to:
            conditions.append("pub_year <= ?")
            params.append(year_to)

        if record_type:
            conditions.append("record_type = ?")
            params.append(record_type)

        # WHERE 절 구성
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 쿼리 실행
        params.append(limit)
        cursor = await self._conn.execute(
            f"""
            SELECT * FROM kormarc_records
            WHERE {where_clause}
            ORDER BY pub_year DESC, timestamp_ms DESC
            LIMIT ?
            """,
            params,
        )

        rows = await cursor.fetchall()
        return self._rows_to_dicts(rows)

    def _rows_to_dicts(self, rows: list) -> list[dict[str, Any]]:
        """
        SQL 결과 행을 딕셔너리 리스트로 변환

        Args:
            rows: SQL 쿼리 결과 행

        Returns:
            딕셔너리 리스트
        """
        # v2 스키마 컬럼
        columns = [
            "toon_id",
            "timestamp_ms",
            "created_at",
            "record_type",
            "isbn",
            "title",
            "author",
            "publisher",
            "pub_year",
            "kdc_code",
            "record_length",
            "record_status",
            "impl_defined1",
            "impl_defined2",
            "indicator_count",
            "subfield_code_count",
            "base_address",
            "impl_defined3",
            "entry_map",
            "raw_kormarc",
            "parsed_data",
            "scraped_at",
            "data_source",
        ]

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            # parsed_data JSON 파싱
            if result["parsed_data"]:
                result["parsed_data"] = json.loads(result["parsed_data"])
            results.append(result)

        return results

    async def delete_record(self, toon_id: str) -> bool:
        """
        레코드 삭제

        Args:
            toon_id: TOON 식별자

        Returns:
            삭제 성공 여부
        """
        if self._conn is None:
            raise RuntimeError("Database not initialized")

        cursor = await self._conn.execute(
            "DELETE FROM kormarc_records WHERE toon_id = ?",
            (toon_id,),
        )

        await self._conn.commit()

        return cursor.rowcount > 0

    async def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self):
        """Async context manager 진입"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager 퇴출"""
        await self.close()


# 동기 버전 (간편 사용을 위해)
class KORMARCDatabaseSync:
    """
    KORMARC 데이터베이스 동기 버전

    동기 컨텍스트에서 사용하기 위한 래퍼
    """

    def __init__(self, db_path: str | Path = "kormarc.db"):
        """
        데이터베이스 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = Path(db_path)
        self._async_db = KORMARCDatabase(db_path)

    def save_record(
        self,
        toon_id: str,
        record_data: dict[str, Any],
        scraped_at: str | None = None,
        data_source: str = "manual",
    ) -> None:
        """
        KORMARC 레코드 저장 (동기)

        Args:
            toon_id: TOON 식별자
            record_data: TOON JSON 형식 레코드 데이터
            scraped_at: 수집 시간
            data_source: 데이터 소스
        """
        import asyncio

        asyncio.run(self._async_db.save_record(toon_id, record_data, scraped_at, data_source))

    def get_record(self, toon_id: str) -> dict[str, Any] | None:
        """
        TOON ID로 레코드 조회 (동기)

        Args:
            toon_id: TOON 식별자

        Returns:
            레코드 데이터 또는 None
        """
        import asyncio

        return asyncio.run(self._async_db.get_record(toon_id))

    def get_by_isbn(self, isbn: str) -> list[dict[str, Any]]:
        """ISBN으로 레코드 조회 (동기)"""
        import asyncio

        return asyncio.run(self._async_db.get_by_isbn(isbn))

    def get_by_type(
        self, record_type: str, limit: int = 100, offset: int = 0
    ) -> list[dict[str, Any]]:
        """레코드 타입별 조회 (동기)"""
        import asyncio

        return asyncio.run(self._async_db.get_by_type(record_type, limit, offset))

    def count_records(self, record_type: str | None = None) -> int:
        """레코드 수 조회 (동기)"""
        import asyncio

        return asyncio.run(self._async_db.count_records(record_type))


# 모듈 레벨 테스트
if __name__ == "__main__":
    import asyncio

    async def test_database():
        """데이터베이스 테스트"""
        # 테스트 DB
        db = KORMARCDatabase(":memory:")

        await db.initialize()

        # 테스트 데이터
        test_record = {
            "toon_id": "kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y",
            "timestamp": "2025-01-10T00:00:00+00:00",
            "type": "kormarc_book",
            "isbn": "9788960777330",
            "raw_kormarc": "<?xml version='1.0'?><record>...</record>",
            "parsed": {
                "leader": {"record_length": 714},
                "control_fields": [],
                "data_fields": [],
            },
        }

        # 저장
        await db.save_record("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y", test_record)

        # 조회
        retrieved = await db.get_record("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y")
        print("Retrieved record:", retrieved)

        # 카운트
        count = await db.count_records()
        print(f"Total records: {count}")

        await db.close()

    asyncio.run(test_database())
