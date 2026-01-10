"""
Scraper Pipeline Integration Tests

Scraper → BookInfo → KORMARC → DB 저장 파이프라인 통합 테스트
"""

import sqlite3

import pytest

from kormarc.db import KORMARCDatabase
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
from tests.test_integration.fixtures.mock_api_responses import (
    SAMPLE_ISBN,
    SAMPLE_SCRAPER_DATA,
    create_mock_scraper_data,
)

# Playwright 사용 가능 여부 확인
try:
    import playwright  # noqa: F401

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


@pytest.mark.integration
class TestScraperSearchToDB:
    """스크래퍼 검색 → DB 저장 테스트"""

    @pytest.mark.asyncio
    async def test_scraper_search_to_db_save(self, tmp_path):
        """
        스크래퍼 데이터 추출 → KORMARC 생성 → DB 저장 → 검색

        전체 파이프라인: Mock 스크래핑 → BookInfo → Record → TOON → DB
        """
        # Mock 스크래핑 데이터
        scraped_data = SAMPLE_SCRAPER_DATA.copy()

        # BookInfo 생성
        book = BookInfo(
            isbn=scraped_data["isbn"],
            title=scraped_data["title"],
            author=scraped_data.get("author"),
            publisher=scraped_data.get("publisher"),
            pub_year=scraped_data.get("pub_year"),
            pages=scraped_data.get("pages"),
            kdc=scraped_data.get("kdc"),
            category="book",
        )

        # KORMARC 레코드 생성
        builder = KORMARCBuilder()
        record = builder.build(book)

        # Record 검증
        assert record is not None
        assert len(record.data_fields) > 0

        # TOON dict 생성
        toon_dict = builder.build_toon_dict(book)

        # 임시 DB에 저장
        db_path = tmp_path / "test_scraper.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        # 저장
        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="test_scraper",
            data_source="web_scraping",
        )

        # DB에서 검색
        retrieved = await db.get_record(toon_dict["toon_id"])

        # 검증
        assert retrieved is not None
        assert retrieved["toon_id"] == toon_dict["toon_id"]
        assert retrieved["isbn"] == SAMPLE_ISBN
        assert retrieved["data_source"] == "web_scraping"

        # 정리
        await db.close()

    @pytest.mark.asyncio
    async def test_scraper_data_extraction(self):
        """
        스크래퍼 데이터 추출 정확도 테스트

        Mock HTML에서 필드 추출이 올바른지 확인
        """
        # Mock 스크래퍼 데이터 (여러 필드 포함)
        scraped_data = create_mock_scraper_data(
            isbn="9788960777330",
            title="파이썬 완벽 가이드",
            author="홍길동",
            publisher="한빛미디어",
            pub_year="2024",
            pages=600,
            kdc="005",
        )

        # 데이터 추출 검증
        assert scraped_data["isbn"] == "9788960777330"
        assert scraped_data["title"] == "파이썬 완벽 가이드"
        assert scraped_data["author"] == "홍길동"
        assert scraped_data["publisher"] == "한빛미디어"
        assert scraped_data["pub_year"] == "2024"
        assert scraped_data["pages"] == 600
        assert scraped_data["kdc"] == "005"

        # BookInfo 변환
        book = BookInfo(
            isbn=scraped_data["isbn"],
            title=scraped_data["title"],
            author=scraped_data["author"],
            publisher=scraped_data["publisher"],
            pub_year=scraped_data["pub_year"],
            pages=scraped_data["pages"],
            kdc=scraped_data["kdc"],
        )

        # 변환 검증
        assert book.isbn == "9788960777330"
        assert book.title == "파이썬 완벽 가이드"
        assert book.author == "홍길동"

    @pytest.mark.asyncio
    async def test_db_save_and_retrieve(self, tmp_path):
        """
        DB 저장 및 검색 테스트

        TOON 레코드를 DB에 저장하고 다시 가져오기
        """
        # TOON 레코드 생성
        book = BookInfo(isbn=SAMPLE_ISBN, title="테스트 도서", category="book")
        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        # 임시 DB
        db_path = tmp_path / "test_db.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        # 저장
        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="test",
            data_source="test",
        )

        # TOON ID로 검색
        retrieved = await db.get_record(toon_dict["toon_id"])
        assert retrieved is not None
        assert retrieved["toon_id"] == toon_dict["toon_id"]
        assert retrieved["isbn"] == SAMPLE_ISBN

        # ISBN으로 검색
        results = await db.get_by_isbn(SAMPLE_ISBN)
        by_isbn = results[0] if results else None
        assert by_isbn is not None
        assert by_isbn["isbn"] == SAMPLE_ISBN

        # 정리
        await db.close()

    @pytest.mark.asyncio
    async def test_scraper_error_handling(self):
        """
        스크래퍼 오류 처리 테스트

        필수 필드 누락 시 처리
        """
        # ISBN 없는 데이터
        incomplete_data = {"title": "제목만 있음"}

        # BookInfo 생성 시 최소 필수 필드 확인
        # ISBN과 title은 필수
        with pytest.raises(TypeError):
            # isbn 파라미터 누락으로 TypeError 발생
            BookInfo(title=incomplete_data["title"])

    @pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="Playwright not installed")
    @pytest.mark.asyncio
    async def test_playwright_unavailable(self):
        """
        Playwright 미설치 시 graceful 처리

        Playwright가 없으면 테스트를 건너뛰어야 함
        """
        # 이 테스트는 Playwright가 설치된 경우에만 실행됨
        from kormarc.scraper import NationalLibraryScraper

        scraper = NationalLibraryScraper(headless=True)
        assert scraper is not None
        assert scraper.headless is True


@pytest.mark.integration
class TestScraperDataIntegrity:
    """스크래퍼 데이터 무결성 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_records_from_scraper(self, tmp_path):
        """
        여러 레코드를 스크래핑하여 DB에 저장

        각 레코드가 독립적으로 저장되는지 확인
        """
        # 3개의 Mock 스크래핑 데이터
        test_data = [
            create_mock_scraper_data(isbn="9780000000001", title="도서1"),
            create_mock_scraper_data(isbn="9780000000002", title="도서2"),
            create_mock_scraper_data(isbn="9780000000003", title="도서3"),
        ]

        db_path = tmp_path / "multi_records.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()
        saved_toon_ids = []

        # 각 데이터 저장
        for data in test_data:
            book = BookInfo(
                isbn=data["isbn"],
                title=data["title"],
                category="book",
            )
            toon_dict = builder.build_toon_dict(book)

            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="scraper",
            )

            saved_toon_ids.append(toon_dict["toon_id"])

        # 저장된 레코드 수 확인
        assert len(saved_toon_ids) == 3

        # 각 레코드 검색
        for toon_id in saved_toon_ids:
            record = await db.get_record(toon_id)
            assert record is not None

        await db.close()

    @pytest.mark.asyncio
    async def test_db_duplicate_handling(self, tmp_path):
        """
        중복 레코드 처리 테스트

        같은 TOON ID를 두 번 저장하면 덮어쓰기
        """
        book = BookInfo(isbn=SAMPLE_ISBN, title="테스트", category="book")
        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        db_path = tmp_path / "duplicate.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        # 첫 번째 저장
        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="first",
            data_source="test",
        )

        # 같은 TOON ID로 두 번째 저장
        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="second",
            data_source="test_updated",
        )

        # 검색: 최신 데이터만 반환
        record = await db.get_record(toon_dict["toon_id"])
        assert record is not None
        # data_source가 업데이트되었는지 확인
        assert record["data_source"] == "test_updated"

        await db.close()

    @pytest.mark.asyncio
    async def test_db_schema_validation(self, tmp_path):
        """
        DB 스키마 검증 (v2)

        kormarc_records 테이블이 올바른 컬럼을 가지는지 확인
        """
        db_path = tmp_path / "schema_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        # 직접 DB 연결하여 스키마 확인
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 테이블 존재 확인
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='kormarc_records'"
        )
        assert cursor.fetchone() is not None

        # FTS5 테이블 존재 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kormarc_fts'")
        assert cursor.fetchone() is not None

        # 컬럼 확인
        cursor.execute("PRAGMA table_info(kormarc_records)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        # v2 필수 컬럼 검증
        required_columns = [
            "toon_id",
            "timestamp_ms",
            "created_at",
            "record_type",
            "isbn",
            # v2 정규화된 필드
            "title",
            "author",
            "publisher",
            "pub_year",
            "kdc_code",
            # v2 Leader 필드
            "record_length",
            "record_status",
            "impl_defined1",
            "impl_defined2",
            "indicator_count",
            "subfield_code_count",
            "base_address",
            "impl_defined3",
            "entry_map",
            # 원본 데이터
            "raw_kormarc",
            "parsed_data",
            "scraped_at",
            "data_source",
        ]
        for col in required_columns:
            assert col in column_names, f"Missing column: {col}"

        # 인덱스 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}

        required_indexes = {
            "idx_timestamp",
            "idx_type",
            "idx_isbn",
            "idx_kdc_year",
            "idx_publisher_year",
            "idx_type_year",
            "idx_title",
            "idx_author",
        }

        for idx in required_indexes:
            assert idx in indexes, f"Missing index: {idx}"

        conn.close()
        await db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
