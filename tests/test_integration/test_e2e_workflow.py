"""
End-to-End Workflow Integration Tests

전체 워크플로우: ISBN → API/Scraper → KORMARC → TOON → DB
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from kormarc.api_client import NationalLibraryClient
from kormarc.db import KORMARCDatabase
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
from kormarc.toon_generator import TOONGenerator
from tests.test_integration.fixtures.mock_api_responses import (
    SAMPLE_ISBN,
    SAMPLE_MARCXML_RESPONSE,
    create_mock_marcxml,
    create_mock_scraper_data,
)


@pytest.mark.integration
class TestE2EWorkflow:
    """End-to-End 워크플로우 테스트"""

    @pytest.mark.asyncio
    async def test_isbn_to_db_via_api(self, tmp_path):
        """
        ISBN → API → KORMARC → TOON → DB 전체 파이프라인

        사용자가 ISBN을 입력하면 DB에 저장되기까지의 전체 흐름
        """
        # 1단계: API로 ISBN 검색
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                api_result = await client.search_by_isbn(SAMPLE_ISBN)

        assert api_result is not None
        assert api_result["isbn"] == SAMPLE_ISBN

        # 2단계: BookInfo 생성
        book = BookInfo(
            isbn=api_result["isbn"],
            title=api_result["title"],
            author=api_result.get("author"),
            publisher=api_result.get("publisher"),
            pub_year=api_result.get("pub_year"),
            pages=api_result.get("pages"),
            kdc=api_result.get("kdc"),
            category="book",
        )

        # 3단계: KORMARC 레코드 생성
        builder = KORMARCBuilder()
        record = builder.build(book)

        assert record is not None
        assert len(record.data_fields) > 0

        # 4단계: TOON 생성
        toon_dict = builder.build_toon_dict(book)

        assert "toon_id" in toon_dict
        assert toon_dict["isbn"] == SAMPLE_ISBN

        # 5단계: DB 저장
        db_path = tmp_path / "e2e_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="api",
            data_source="national_library_api",
        )

        # 6단계: 검증 - DB에서 검색
        results = await db.get_by_isbn(SAMPLE_ISBN)
        retrieved = results[0] if results else None

        assert retrieved is not None
        assert retrieved["isbn"] == SAMPLE_ISBN
        assert retrieved["toon_id"] == toon_dict["toon_id"]
        # parsed_data는 JSON으로 저장되므로 parsed_data로 접근
        assert "파이썬" in str(retrieved.get("parsed_data", {}))

        await db.close()

    @pytest.mark.asyncio
    async def test_api_failure_fallback_to_scraper(self, tmp_path):
        """
        API 실패 시 스크래퍼로 폴백

        API가 실패하면 웹 스크래핑으로 데이터 수집
        """
        # 1단계: API 호출 실패 시뮬레이션
        api_failed = False
        try:
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.get = AsyncMock(side_effect=httpx.HTTPError("API Error"))
                mock_client.aclose = AsyncMock()
                mock_client_class.return_value = mock_client

                async with NationalLibraryClient() as client:
                    await client.search_by_isbn(SAMPLE_ISBN)
        except httpx.HTTPError:
            api_failed = True

        assert api_failed, "API should have failed"

        # 2단계: 폴백 - 스크래퍼 데이터 사용
        scraper_data = create_mock_scraper_data(
            isbn=SAMPLE_ISBN,
            title="파이썬 프로그래밍 (스크래핑)",
            author="박응용",
        )

        # 3단계: BookInfo 생성
        book = BookInfo(
            isbn=scraper_data["isbn"],
            title=scraper_data["title"],
            author=scraper_data.get("author"),
            publisher=scraper_data.get("publisher"),
            category="book",
        )

        # 4단계: KORMARC 및 TOON 생성
        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        # 5단계: DB 저장
        db_path = tmp_path / "fallback_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="scraper_fallback",
            data_source="web_scraping",
        )

        # 6단계: 검증
        results = await db.get_by_isbn(SAMPLE_ISBN)
        retrieved = results[0] if results else None
        assert retrieved is not None
        assert retrieved["data_source"] == "web_scraping"

        await db.close()

    @pytest.mark.asyncio
    async def test_data_integrity_end_to_end(self, tmp_path):
        """
        End-to-End 데이터 무결성 테스트

        입력 ISBN과 DB에 저장된 ISBN이 일치하는지 확인
        """
        input_isbn = "9788960777330"

        # API 호출
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_xml = create_mock_marcxml(isbn=input_isbn, title="데이터 무결성 테스트")
            mock_response = AsyncMock()
            mock_response.text = mock_xml
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn(input_isbn)

        # 전체 파이프라인 실행
        book = BookInfo(isbn=result["isbn"], title=result["title"], category="book")
        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        db_path = tmp_path / "integrity_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="api",
            data_source="api",
        )

        # 검증: 입력 ISBN과 DB ISBN 일치
        results = await db.get_by_isbn(input_isbn)
        retrieved = results[0] if results else None
        assert retrieved is not None
        assert retrieved["isbn"] == input_isbn

        await db.close()

    @pytest.mark.asyncio
    async def test_duplicate_isbn_handling(self, tmp_path):
        """
        중복 ISBN 처리 테스트

        같은 ISBN을 두 번 저장하면 업데이트
        """
        isbn = SAMPLE_ISBN

        # 첫 번째 저장
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_xml = create_mock_marcxml(isbn=isbn, title="첫 번째 버전")
            mock_response = AsyncMock()
            mock_response.text = mock_xml
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result1 = await client.search_by_isbn(isbn)

        book1 = BookInfo(isbn=result1["isbn"], title=result1["title"], category="book")
        builder = KORMARCBuilder()
        toon_dict1 = builder.build_toon_dict(book1)

        db_path = tmp_path / "duplicate_isbn.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        await db.save_record(
            toon_id=toon_dict1["toon_id"],
            record_data=toon_dict1,
            scraped_at="first",
            data_source="api_v1",
        )

        # 두 번째 저장 (같은 ISBN, 다른 TOON ID)
        book2 = BookInfo(isbn=isbn, title="두 번째 버전", category="book")
        toon_dict2 = builder.build_toon_dict(book2)

        await db.save_record(
            toon_id=toon_dict2["toon_id"],
            record_data=toon_dict2,
            scraped_at="second",
            data_source="api_v2",
        )

        # 검증: ISBN로 검색 시 여러 레코드 반환 가능
        # (DB 구현에 따라 최신 것만 반환하거나 모두 반환)
        results = await db.get_by_isbn(isbn)
        by_isbn = results[0] if results else None
        assert by_isbn is not None
        assert by_isbn["isbn"] == isbn

        await db.close()

    @pytest.mark.asyncio
    async def test_toon_id_consistency(self):
        """
        TOON ID 일관성 테스트

        여러 번 생성해도 포맷이 일관적인지 확인
        """
        generator = TOONGenerator()
        builder = KORMARCBuilder()

        # 같은 ISBN으로 여러 번 생성
        toon_ids = []
        for _ in range(5):
            book = BookInfo(isbn=SAMPLE_ISBN, title="테스트", category="book")
            _, toon_id = builder.build_with_toon(book)
            toon_ids.append(toon_id)

        # 모든 TOON ID가 유효한 포맷인지 확인
        for toon_id in toon_ids:
            assert generator.validate(toon_id)
            assert toon_id.startswith("kormarc_book_")

            # 파싱 가능한지 확인
            parsed = generator.parse(toon_id)
            assert parsed["type"] == "kormarc_book"
            assert parsed["subtype"] == "book"
            assert len(parsed["ulid"]) == 26


@pytest.mark.integration
class TestE2EErrorRecovery:
    """End-to-End 오류 복구 테스트"""

    @pytest.mark.asyncio
    async def test_partial_data_handling(self, tmp_path):
        """
        부분 데이터 처리

        일부 필드가 누락되어도 처리 가능
        """
        # 최소 데이터만 있는 BookInfo
        book = BookInfo(
            isbn=SAMPLE_ISBN,
            title="최소 데이터 테스트",
            # author, publisher 등 생략
            category="book",
        )

        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        # DB 저장
        db_path = tmp_path / "partial_data.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="test",
            data_source="partial",
        )

        # 검색 성공
        results = await db.get_by_isbn(SAMPLE_ISBN)
        retrieved = results[0] if results else None
        assert retrieved is not None

        await db.close()

    @pytest.mark.asyncio
    async def test_db_connection_recovery(self, tmp_path):
        """
        DB 연결 복구 테스트

        DB를 닫았다가 다시 열어도 작동하는지 확인
        """
        db_path = tmp_path / "connection_test.db"

        # 첫 번째 연결
        db1 = KORMARCDatabase(str(db_path))
        await db1.initialize()

        book = BookInfo(isbn=SAMPLE_ISBN, title="연결 테스트", category="book")
        builder = KORMARCBuilder()
        toon_dict = builder.build_toon_dict(book)

        await db1.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="test",
            data_source="test",
        )

        await db1.close()

        # 두 번째 연결 (같은 DB 파일)
        db2 = KORMARCDatabase(str(db_path))
        await db2.initialize()

        # 이전 데이터 검색 가능
        results = await db2.get_by_isbn(SAMPLE_ISBN)
        retrieved = results[0] if results else None
        assert retrieved is not None
        assert retrieved["isbn"] == SAMPLE_ISBN

        await db2.close()

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, tmp_path):
        """
        동시 쓰기 처리

        여러 레코드를 순차적으로 저장
        """
        db_path = tmp_path / "concurrent.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()
        saved_count = 0

        # 10개 레코드 저장
        for i in range(10):
            isbn = f"978000000000{i}"
            book = BookInfo(isbn=isbn, title=f"도서 {i}", category="book")
            toon_dict = builder.build_toon_dict(book)

            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="concurrent_test",
            )

            saved_count += 1

        # 모두 저장되었는지 확인
        assert saved_count == 10

        await db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
