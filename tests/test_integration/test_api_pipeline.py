"""
API Pipeline Integration Tests

API → MARCXML → KORMARC → TOON 변환 파이프라인 통합 테스트
"""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from kormarc.api_client import NationalLibraryClient
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
from kormarc.toon_generator import TOONGenerator
from tests.test_integration.fixtures.mock_api_responses import (
    SAMPLE_EMPTY_MARCXML_RESPONSE,
    SAMPLE_ISBN,
    SAMPLE_MARCXML_RESPONSE,
    create_mock_marcxml,
)


@pytest.mark.integration
class TestAPISearchToKORMARCConversion:
    """API 검색 → KORMARC 변환 테스트"""

    @pytest.mark.asyncio
    async def test_api_search_to_kormarc_conversion(self):
        """
        API 검색 결과를 KORMARC Record로 변환

        전체 파이프라인: API 호출 → MARCXML 파싱 → KORMARC 생성 → TOON 생성
        """
        # Mock httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client_class:
            # Mock response 설정
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            # API 클라이언트로 ISBN 검색
            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn(SAMPLE_ISBN)

            # API 검색 결과 검증
            assert result is not None
            assert result["isbn"] == SAMPLE_ISBN
            assert "title" in result
            assert "author" in result

            # BookInfo 생성
            book = BookInfo(
                isbn=result["isbn"],
                title=result["title"],
                author=result.get("author"),
                publisher=result.get("publisher"),
                pub_year=result.get("pub_year"),
                pages=result.get("pages"),
                kdc=result.get("kdc"),
                category="book",
            )

            # KORMARC 레코드 생성
            builder = KORMARCBuilder()
            record = builder.build(book)

            # Record 구조 검증
            assert record is not None
            assert record.leader is not None
            assert len(record.control_fields) > 0
            assert len(record.data_fields) > 0

            # ISBN 필드 검증
            isbn_field = next((f for f in record.data_fields if f.tag == "020"), None)
            assert isbn_field is not None
            assert any(s.data == SAMPLE_ISBN for s in isbn_field.subfields)

            # TOON ID 생성
            _, toon_id = builder.build_with_toon(book)

            # TOON ID 검증
            assert toon_id is not None
            assert toon_id.startswith("kormarc_book_")
            assert len(toon_id) > 20

            # TOON 검증
            generator = TOONGenerator()
            assert generator.validate(toon_id)

    @pytest.mark.asyncio
    async def test_api_marcxml_parsing(self):
        """
        MARCXML 파싱 정확도 테스트

        다양한 MARC 필드가 올바르게 추출되는지 확인
        """
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn(SAMPLE_ISBN)

            # 주요 필드 추출 검증
            assert result is not None
            assert result["isbn"] == "9788960777330"
            assert "파이썬" in result["title"]
            assert result["author"] == "박응용"
            assert result["publisher"] == "한빛미디어"
            assert result["pub_year"] == "2025"
            assert result["pages"] == 500
            assert result["kdc"] == "005.133"

            # Leader 검증
            assert result["leader"] is not None
            assert len(result["leader"]) == 24

            # 제어 필드 검증
            assert "001" in result["control_fields"]
            assert "003" in result["control_fields"]
            assert "008" in result["control_fields"]

    @pytest.mark.asyncio
    async def test_toon_generation_from_api_data(self):
        """
        API 데이터에서 TOON 생성 테스트

        TOON 포맷 검증: prefix_26chars
        """
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn(SAMPLE_ISBN)

            # BookInfo 생성
            book = BookInfo(
                isbn=result["isbn"],
                title=result["title"],
                category="book",
            )

            # TOON 생성
            builder = KORMARCBuilder()
            record, toon_id = builder.build_with_toon(book)

            # TOON 포맷 검증
            assert toon_id.startswith("kormarc_book_")
            parts = toon_id.split("_")
            assert len(parts) == 3  # kormarc, book, ULID
            ulid_part = parts[2]
            assert len(ulid_part) == 26  # ULID는 26자

            # TOON 파싱
            generator = TOONGenerator()
            parsed = generator.parse(toon_id)
            assert parsed["type"] == "kormarc_book"
            assert parsed["subtype"] == "book"

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """
        API 오류 처리 테스트

        네트워크 오류, 타임아웃 등의 예외 상황 처리
        """
        # 네트워크 오류 테스트
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.HTTPError("Network error"))
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPError):
                async with NationalLibraryClient() as client:
                    await client.search_by_isbn(SAMPLE_ISBN)

        # 타임아웃 테스트
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.TimeoutException):
                async with NationalLibraryClient(timeout=1.0) as client:
                    await client.search_by_isbn(SAMPLE_ISBN)

    @pytest.mark.asyncio
    async def test_api_empty_results(self):
        """
        빈 검색 결과 처리 테스트

        검색 결과가 없을 때 graceful하게 처리
        """
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_EMPTY_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn("0000000000000")

            # 빈 결과 검증
            assert result is None


@pytest.mark.integration
class TestAPIDataValidation:
    """API 데이터 검증 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_books_from_api(self):
        """
        여러 도서를 API에서 가져와서 TOON 생성

        각 도서마다 고유한 TOON ID가 생성되는지 확인
        """
        # 3개의 다른 ISBN으로 테스트
        test_isbns = ["9788960777330", "9788968480000", "9788965400000"]
        toon_ids = set()

        for isbn in test_isbns:
            mock_xml = create_mock_marcxml(isbn=isbn, title=f"테스트 도서 {isbn}")

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = AsyncMock()
                mock_response.text = mock_xml
                mock_response.raise_for_status = AsyncMock()

                mock_client = AsyncMock()
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client.aclose = AsyncMock()
                mock_client_class.return_value = mock_client

                async with NationalLibraryClient() as client:
                    result = await client.search_by_isbn(isbn)

                # BookInfo → TOON 생성
                book = BookInfo(isbn=result["isbn"], title=result["title"])
                builder = KORMARCBuilder()
                _, toon_id = builder.build_with_toon(book)

                # TOON ID 고유성 검증
                assert toon_id not in toon_ids
                toon_ids.add(toon_id)

        # 3개 모두 다른 TOON ID
        assert len(toon_ids) == 3

    @pytest.mark.asyncio
    async def test_toon_dict_structure(self):
        """
        build_toon_dict()로 생성된 JSON 구조 검증

        모든 필수 키가 포함되어 있는지 확인
        """
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = SAMPLE_MARCXML_RESPONSE
            mock_response.raise_for_status = AsyncMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.aclose = AsyncMock()
            mock_client_class.return_value = mock_client

            async with NationalLibraryClient() as client:
                result = await client.search_by_isbn(SAMPLE_ISBN)

            book = BookInfo(
                isbn=result["isbn"],
                title=result["title"],
                author=result.get("author"),
                kdc=result.get("kdc"),
            )

            builder = KORMARCBuilder()
            toon_dict = builder.build_toon_dict(book)

            # 필수 키 검증
            required_keys = ["toon_id", "timestamp", "type", "isbn", "raw_kormarc", "parsed"]
            for key in required_keys:
                assert key in toon_dict, f"Missing required key: {key}"

            # 타입 검증
            assert isinstance(toon_dict["toon_id"], str)
            assert isinstance(toon_dict["isbn"], str)
            assert isinstance(toon_dict["parsed"], dict)

            # Parsed 구조 검증
            parsed = toon_dict["parsed"]
            assert "leader" in parsed
            assert "control_fields" in parsed
            assert "data_fields" in parsed
            assert isinstance(parsed["control_fields"], list)
            assert isinstance(parsed["data_fields"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
