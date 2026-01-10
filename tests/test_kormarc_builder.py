"""
KORMARCBuilder 테스트

BookInfo → Record → TOON 변환 파이프라인 테스트
"""

import pytest

from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
from kormarc.models.record import Record
from kormarc.toon_generator import TOONGenerator


class TestBookInfo:
    """BookInfo 데이터 클래스 테스트"""

    def test_book_info_creation(self):
        """BookInfo 생성 테스트"""
        book = BookInfo(
            isbn="9788960777330",
            title="이것이 우다다",
            author="홍길동",
            publisher="한빛미디어",
            pub_year="2025",
            pages=300,
            kdc="005",
        )

        assert book.isbn == "9788960777330"
        assert book.title == "이것이 우다다"
        assert book.author == "홍길동"

    def test_book_info_to_dict(self):
        """BookInfo to_dict 테스트"""
        book = BookInfo(isbn="9788960777330", title="테스트")

        result = book.to_dict()

        assert isinstance(result, dict)
        assert result["isbn"] == "9788960777330"
        assert result["title"] == "테스트"


class TestKORMARCBuilder:
    """KORMARCBuilder 테스트"""

    def test_builder_init(self):
        """빌더 초기화 테스트"""
        builder = KORMARCBuilder()

        assert builder.toon_generator is not None
        assert isinstance(builder.toon_generator, TOONGenerator)

    def test_builder_init_with_custom_generator(self):
        """커스텀 TOON 생성기로 초기화"""
        custom_gen = TOONGenerator()
        builder = KORMARCBuilder(toon_generator=custom_gen)

        assert builder.toon_generator is custom_gen

    def test_build_returns_record(self):
        """build()가 Record를 반환하는지 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(isbn="9788960777330", title="테스트 도서")

        record = builder.build(book)

        assert isinstance(record, Record)
        assert record.leader is not None
        assert len(record.control_fields) > 0
        assert len(record.data_fields) > 0

    def test_build_creates_required_control_fields(self):
        """필수 제어 필드 생성 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(isbn="9788960777330", title="테스트 도서")

        record = builder.build(book)

        control_tags = {f.tag for f in record.control_fields}

        # 필수 제어 필드 확인
        assert "001" in control_tags  # 제어번호
        assert "003" in control_tags  # 제어번호 식별기호
        assert "005" in control_tags  # 최종 처리일시
        assert "008" in control_tags  # 부호화정보필드

    def test_build_creates_required_data_fields(self):
        """필수 데이터 필드 생성 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(
            isbn="9788960777330",
            title="테스트 도서",
            author="홍길동",
            publisher="테스트 출판사",
        )

        record = builder.build(book)

        data_tags = {f.tag for f in record.data_fields}

        # 필수/권장 데이터 필드 확인
        assert "020" in data_tags  # ISBN
        assert "040" in data_tags  # 목록작성기관
        assert "100" in data_tags  # 주요 저자
        assert "245" in data_tags  # 표제

    def test_build_with_toon(self):
        """build_with_toon() 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(
            isbn="9788960777330",
            title="테스트 도서",
            category="book",
        )

        record, toon_id = builder.build_with_toon(book)

        # Record 확인
        assert isinstance(record, Record)

        # TOON ID 확인
        assert isinstance(toon_id, str)
        assert toon_id.startswith("kormarc_book_")
        assert len(toon_id) > 20

    def test_build_with_toon_different_categories(self):
        """다양한 카테고리에 대한 TOON 생성 테스트"""
        builder = KORMARCBuilder()

        categories = ["book", "serial", "academic", "comic"]

        for category in categories:
            book = BookInfo(
                isbn="9788960777330",
                title="테스트",
                category=category,
            )

            record, toon_id = builder.build_with_toon(book)

            expected_prefix = f"kormarc_{category}"
            assert toon_id.startswith(expected_prefix)

    def test_build_toon_dict(self):
        """build_toon_dict() 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(
            isbn="9788960777330",
            title="테스트 도서",
            author="홍길동",
            kdc="005",
        )

        result = builder.build_toon_dict(book)

        # 필수 키 확인
        assert "toon_id" in result
        assert "timestamp" in result
        assert "type" in result
        assert "isbn" in result
        assert "raw_kormarc" in result
        assert "parsed" in result

        # 타입 확인
        assert isinstance(result["toon_id"], str)
        assert isinstance(result["isbn"], str)
        assert isinstance(result["parsed"], dict)

        # 파싱된 데이터 구조 확인
        parsed = result["parsed"]
        assert "leader" in parsed
        assert "control_fields" in parsed
        assert "data_fields" in parsed


class TestKORMARCBuilderIntegration:
    """통합 테스트"""

    def test_full_pipeline(self):
        """전체 파이프라인 테스트: BookInfo → Record → TOON → JSON"""
        builder = KORMARCBuilder()

        # 1. BookInfo 생성
        book = BookInfo(
            isbn="9788960777330",
            title="파이썬 프로그래밍",
            author="박응용",
            publisher="한빛미디어",
            pub_year="2025",
            pages=500,
            kdc="005",
            category="book",
            price=38000,
        )

        # 2. Record 생성
        record = builder.build(book)
        assert isinstance(record, Record)

        # 3. TOON 생성
        record2, toon_id = builder.build_with_toon(book)
        assert isinstance(record2, Record)
        assert isinstance(toon_id, str)

        # 4. JSON 변환
        toon_dict = builder.build_toon_dict(book)
        assert isinstance(toon_dict, dict)
        assert toon_dict["isbn"] == "9788960777330"

    def test_xml_output(self):
        """XML 출력 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(isbn="9788960777330", title="테스트")

        record = builder.build(book)
        xml_output = record.to_xml()

        assert isinstance(xml_output, str)
        assert "<?xml" in xml_output
        # 네임스페이스 접두사(ns0:)가 있을 수 있음
        assert "record" in xml_output
        assert "leader" in xml_output
        assert "MARC21" in xml_output  # MARCXML 네임스페이스 확인

    def test_json_output(self):
        """JSON 출력 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(isbn="9788960777330", title="테스트")

        toon_dict = builder.build_toon_dict(book)

        import json

        json_str = json.dumps(toon_dict, ensure_ascii=False)

        assert isinstance(json_str, str)
        assert "toon_id" in json_str
        assert "kormarc" in json_str


class TestKORMARCBuilderEdgeCases:
    """엣지 케이스 테스트"""

    def test_minimal_book_info(self):
        """최소 BookInfo로 빌드 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(isbn="9788960777330", title="최소 도서")

        record = builder.build(book)

        assert isinstance(record, Record)
        # 최소 필수 필드만 생성되어야 함
        data_tags = {f.tag for f in record.data_fields}
        assert "020" in data_tags  # ISBN
        assert "040" in data_tags  # 목록작성기관
        assert "245" in data_tags  # 표제

    def test_book_info_without_optional_fields(self):
        """선택적 필드 없는 BookInfo 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(
            isbn="9788960777330",
            title="테스트 도서",
            author=None,
            publisher=None,
            pages=None,
            kdc=None,
        )

        record = builder.build(book)

        # 저자 필드 없어야 함
        data_tags = {f.tag for f in record.data_fields}
        assert "100" not in data_tags  # 주요 저자

    def test_unicode_handling(self):
        """유니코드(한국어) 처리 테스트"""
        builder = KORMARCBuilder()
        book = BookInfo(
            isbn="9788960777330",
            title="한국어 도서 제목 📚",
            author="홍길동",
        )

        record = builder.build(book)
        xml = record.to_xml()

        # XML에 한국어 포함
        assert "한국어" in xml or "홍길동" in xml


@pytest.mark.parametrize(
    "category,expected_prefix",
    [
        ("book", "kormarc_book"),
        ("serial", "kormarc_serial"),
        ("academic", "kormarc_academic"),
        ("comic", "kormarc_comic"),
    ],
)
def test_toon_generation_by_category(category, expected_prefix):
    """카테고리별 TOON 생성 파라미터화 테스트"""
    builder = KORMARCBuilder()
    book = BookInfo(isbn="9788960777330", title="테스트", category=category)

    record, toon_id = builder.build_with_toon(book)

    assert toon_id.startswith(expected_prefix)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
