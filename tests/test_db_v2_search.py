"""
KORMARC Database v2 검색 기능 테스트

v2 스키마의 새로운 검색 기능 테스트:
- FTS5 전문 검색
- KDC 분류 검색
- 출판사 검색
- 고급 검색
"""

import pytest

from kormarc.db import KORMARCDatabase
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder


@pytest.mark.asyncio
class TestDatabaseV2Search:
    """Database v2 검색 기능 테스트"""

    async def test_search_by_title_fts5(self, tmp_path):
        """
        제목 전문 검색 (FTS5) 테스트
        """
        db_path = tmp_path / "search_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        # 테스트 데이터 생성
        builder = KORMARCBuilder()

        books = [
            BookInfo(isbn="9780000000001", title="파이썬 프로그래밍", category="book"),
            BookInfo(isbn="9780000000002", title="자바스크립트 완벽 가이드", category="book"),
            BookInfo(isbn="9780000000003", title="파이썬 데이터 분석", category="book"),
        ]

        # 레코드 저장
        for book in books:
            toon_dict = builder.build_toon_dict(book)
            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="test",
            )

        # FTS5 검색 테스트
        results = await db.search_by_title("파이썬")
        assert len(results) == 2

        # 제목 확인
        titles = {r["title"] for r in results}
        assert "파이썬 프로그래밍" in titles
        assert "파이썬 데이터 분석" in titles

        await db.close()

    async def test_search_by_author(self, tmp_path):
        """
        저자 검색 테스트
        """
        db_path = tmp_path / "author_search.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        books = [
            BookInfo(isbn="9780000000001", title="책1", author="홍길동", category="book"),
            BookInfo(isbn="9780000000002", title="책2", author="김철수", category="book"),
            BookInfo(isbn="9780000000003", title="책3", author="홍길동", category="book"),
        ]

        for book in books:
            toon_dict = builder.build_toon_dict(book)
            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="test",
            )

        # 저자 검색
        results = await db.search_by_author("홍길동")
        assert len(results) == 2

        for result in results:
            assert result["author"] == "홍길동"

        await db.close()

    async def test_search_by_kdc(self, tmp_path):
        """
        KDC 분류 검색 테스트
        """
        db_path = tmp_path / "kdc_search.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        books = [
            BookInfo(isbn="9780000000001", title="컴퓨터 과학", kdc="005", category="book"),
            BookInfo(isbn="9780000000002", title="프로그래밍", kdc="005.1", category="book"),
            BookInfo(isbn="9780000000003", title="문학", kdc="810", category="book"),
        ]

        for book in books:
            toon_dict = builder.build_toon_dict(book)
            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="test",
            )

        # KDC 005로 시작하는 레코드 검색
        results = await db.search_by_kdc("005")
        assert len(results) == 2

        for result in results:
            assert result["kdc_code"].startswith("005")

        await db.close()

    async def test_search_by_publisher(self, tmp_path):
        """
        출판사 검색 테스트
        """
        db_path = tmp_path / "publisher_search.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        books = [
            BookInfo(
                isbn="9780000000001",
                title="책1",
                publisher="한빛미디어",
                pub_year="2023",
                category="book",
            ),
            BookInfo(
                isbn="9780000000002",
                title="책2",
                publisher="한빛미디어",
                pub_year="2024",
                category="book",
            ),
            BookInfo(
                isbn="9780000000003",
                title="책3",
                publisher="위키북스",
                pub_year="2024",
                category="book",
            ),
        ]

        for book in books:
            toon_dict = builder.build_toon_dict(book)
            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="test",
            )

        # 출판사 검색
        results = await db.search_by_publisher("한빛미디어")
        assert len(results) == 2

        # 연도 범위 검색
        results_2024 = await db.search_by_publisher("한빛미디어", year_from=2024)
        assert len(results_2024) == 1
        assert results_2024[0]["pub_year"] == 2024

        await db.close()

    async def test_advanced_search(self, tmp_path):
        """
        고급 검색 (복합 조건) 테스트
        """
        db_path = tmp_path / "advanced_search.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        books = [
            BookInfo(
                isbn="9780000000001",
                title="파이썬 프로그래밍",
                author="홍길동",
                publisher="한빛미디어",
                pub_year="2023",
                kdc="005.1",
                category="book",
            ),
            BookInfo(
                isbn="9780000000002",
                title="자바 프로그래밍",
                author="김철수",
                publisher="한빛미디어",
                pub_year="2024",
                kdc="005.1",
                category="book",
            ),
            BookInfo(
                isbn="9780000000003",
                title="파이썬 데이터 분석",
                author="홍길동",
                publisher="위키북스",
                pub_year="2024",
                kdc="005.7",
                category="book",
            ),
        ]

        for book in books:
            toon_dict = builder.build_toon_dict(book)
            await db.save_record(
                toon_id=toon_dict["toon_id"],
                record_data=toon_dict,
                scraped_at="test",
                data_source="test",
            )

        # 제목 + 저자 검색
        results = await db.advanced_search(title="파이썬", author="홍길동")
        assert len(results) == 2

        # 출판사 + 연도 검색
        results = await db.advanced_search(publisher="한빛미디어", year_from=2024)
        assert len(results) == 1
        assert results[0]["title"] == "자바 프로그래밍"

        # KDC + 연도 범위 검색
        results = await db.advanced_search(kdc_code="005.1", year_from=2023, year_to=2024)
        assert len(results) == 2

        await db.close()

    async def test_normalized_fields_extraction(self, tmp_path):
        """
        정규화된 필드 추출 테스트
        """
        db_path = tmp_path / "normalized_test.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        book = BookInfo(
            isbn="9788960777330",
            title="테스트 도서",
            author="홍길동",
            publisher="한빛미디어",
            pub_year="2024",
            kdc="005.1",
            category="book",
        )

        toon_dict = builder.build_toon_dict(book)

        await db.save_record(
            toon_id=toon_dict["toon_id"],
            record_data=toon_dict,
            scraped_at="test",
            data_source="test",
        )

        # 레코드 조회
        record = await db.get_record(toon_dict["toon_id"])

        # 정규화된 필드 확인
        assert record is not None
        assert record["title"] == "테스트 도서"
        assert record["author"] == "홍길동"
        assert record["publisher"] == "한빛미디어"
        assert record["pub_year"] == 2024
        assert record["kdc_code"] == "005.1"

        # Leader 필드 확인
        assert "record_length" in record
        assert "record_status" in record

        await db.close()

    async def test_pub_year_validation(self, tmp_path):
        """
        출판년도 유효성 검증 테스트
        """
        db_path = tmp_path / "year_validation.db"
        db = KORMARCDatabase(str(db_path))
        await db.initialize()

        builder = KORMARCBuilder()

        # 유효한 출판년도
        book1 = BookInfo(
            isbn="9780000000001",
            title="책1",
            pub_year="2024",
            category="book",
        )

        toon_dict1 = builder.build_toon_dict(book1)
        await db.save_record(
            toon_id=toon_dict1["toon_id"],
            record_data=toon_dict1,
            scraped_at="test",
            data_source="test",
        )

        record1 = await db.get_record(toon_dict1["toon_id"])
        assert record1["pub_year"] == 2024

        # pub_year가 None인 경우도 허용
        book2 = BookInfo(isbn="9780000000002", title="책2", category="book")
        toon_dict2 = builder.build_toon_dict(book2)

        await db.save_record(
            toon_id=toon_dict2["toon_id"],
            record_data=toon_dict2,
            scraped_at="test",
            data_source="test",
        )

        record2 = await db.get_record(toon_dict2["toon_id"])
        assert record2["pub_year"] is None

        await db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
