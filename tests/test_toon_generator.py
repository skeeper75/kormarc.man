"""
TOON 생성기 테스트

TDD 접근법에 따른 TOON 생성기 테스트 스위트:
- RED: 실패하는 테스트 먼저 작성
- GREEN: 최소한의 코드로 테스트 통과
- REFACTOR: 코드 개선 및 테스트 유지
"""

import time
from datetime import UTC, datetime

import pytest

from kormarc.toon_generator import (
    TOONGenerator,
    TOONValidationError,
    decode_base32,
    determine_record_type,
    encode_base32,
)


class TestTOONGeneration:
    """TOON 생성 기능 테스트"""

    def test_generate_basic_toon(self):
        """기본 TOON 생성 테스트"""
        generator = TOONGenerator()
        toon_id = generator.generate("kormarc_book")

        # 형식 검증: prefix_26자리ULID
        assert isinstance(toon_id, str)
        assert toon_id.startswith("kormarc_book_")
        assert len(toon_id) == len("kormarc_book_") + 26

        # ULID 부분만 추출
        ulid_part = toon_id.split("_")[-1]
        assert len(ulid_part) == 26
        assert all(c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for c in ulid_part)

    def test_generate_different_types(self):
        """다양한 레코드 타입으로 TOON 생성 테스트"""
        generator = TOONGenerator()

        types = [
            "kormarc_book",
            "kormarc_serial",
            "kormarc_academic",
            "kormarc_comic",
            "kormarc_unknown",
        ]

        for record_type in types:
            toon_id = generator.generate(record_type)
            assert toon_id.startswith(f"{record_type}_")
            ulid_part = toon_id.split("_")[-1]
            assert len(ulid_part) == 26

    def test_generate_with_custom_timestamp(self):
        """커스텀 타임스탬프로 TOON 생성 테스트"""
        generator = TOONGenerator()
        custom_time = int(datetime(2025, 1, 10, 12, 0, 0, tzinfo=UTC).timestamp() * 1000)

        toon_id = generator.generate("kormarc_book", timestamp_ms=custom_time)
        parsed = generator.parse(toon_id)

        assert parsed["timestamp_ms"] == custom_time

    def test_toon_uniqueness(self):
        """TOON 고유성 테스트 (10,000 개)"""
        generator = TOONGenerator()

        toons = set()
        for _ in range(10000):
            toon_id = generator.generate("kormarc_book")
            toons.add(toon_id)

        # 중복 없음
        assert len(toons) == 10000

    def test_toon_sortable_by_time(self):
        """시간순 정렬 가능성 테스트"""
        generator = TOONGenerator()

        toon1 = generator.generate("kormarc_book")
        time.sleep(0.001)  # 1ms 대기
        toon2 = generator.generate("kormarc_book")

        # 같은 타입: 시간순 정렬
        assert toon1 < toon2

    def test_toon_sortable_with_different_types(self):
        """다른 타입 간 정렬 테스트"""
        generator = TOONGenerator()

        book_toon = generator.generate("kormarc_book")
        serial_toon = generator.generate("kormarc_serial")

        # 타입이 다르면 사전순 정렬
        assert book_toon < serial_toon


class TestTOONParsing:
    """TOON 파싱 기능 테스트"""

    def test_parse_toon(self):
        """TOON 파싱 테스트"""
        generator = TOONGenerator()
        toon_id = "kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y"

        parsed = generator.parse(toon_id)

        assert parsed["type"] == "kormarc_book"
        assert parsed["subtype"] == "book"
        assert parsed["ulid"] == "01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y"
        assert "timestamp_ms" in parsed
        assert "created_at" in parsed

    def test_parse_toon_timestamp_extraction(self):
        """TOON에서 타임스탬프 추출 테스트"""
        generator = TOONGenerator()
        custom_time = int(datetime(2025, 1, 10, 12, 0, 0, tzinfo=UTC).timestamp() * 1000)

        toon_id = generator.generate("kormarc_book", timestamp_ms=custom_time)
        extracted_time = generator.extract_timestamp(toon_id)

        assert extracted_time == datetime(2025, 1, 10, 12, 0, 0, tzinfo=UTC)

    def test_parse_invalid_toon(self):
        """잘못된 TOON 파싱 테스트"""
        generator = TOONGenerator()

        with pytest.raises(TOONValidationError):
            generator.parse("invalid_toon")

        with pytest.raises(TOONValidationError):
            generator.parse("kormarc_book_short")

    def test_parse_toon_case_insensitive(self):
        """대소문자 무관 파싱 테스트"""
        generator = TOONGenerator()
        toon_id = "kormarc_book_01hzr9syxr9vqjxj9x8y8y8y8y"  # 소문자

        parsed = generator.parse(toon_id)

        assert parsed["type"] == "kormarc_book"
        assert parsed["ulid"].isupper()  # 내부적으로 대문자로 변환


class TestTOONValidation:
    """TOON 검증 기능 테스트"""

    def test_validate_valid_toon(self):
        """유효한 TOON 검증 테스트"""
        generator = TOONGenerator()
        toon_id = generator.generate("kormarc_book")

        assert generator.validate(toon_id) is True

    def test_validate_invalid_toon(self):
        """잘못된 TOON 검증 테스트"""
        generator = TOONGenerator()

        assert generator.validate("invalid") is False
        assert generator.validate("kormarc_book_short") is False
        assert generator.validate("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y_EXTRA") is False

    def test_validate_invalid_characters(self):
        """잘못된 문자 포함 TOON 검증 테스트"""
        generator = TOONGenerator()

        # I, L, O, U는 Crockford's Base32에서 제외
        assert generator.validate("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8I") is False
        assert generator.validate("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8L") is False
        assert generator.validate("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8O") is False
        assert generator.validate("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8U") is False


class TestBase32Encoding:
    """Crockford's Base32 인코딩/디코딩 테스트"""

    def test_encode_base32(self):
        """Base32 인코딩 테스트"""
        data = b"\x01\x23\x45\x67\x89\xab"  # 6 bytes
        encoded = encode_base32(data)

        assert isinstance(encoded, str)
        assert len(encoded) == 10  # 6 bytes = 48 bits → 10 base32 chars
        assert all(c in "0123456789ABCDEFGHJKMNPQRSTVWXYZ" for c in encoded)

    def test_decode_base32(self):
        """Base32 디코딩 테스트"""
        # 먼저 인코딩한 후 디코딩하여 검증
        original = b"\x01\x23\x45\x67\x89\xab"
        encoded = encode_base32(original)
        decoded = decode_base32(encoded)

        assert decoded == original

    def test_encode_decode_roundtrip(self):
        """인코딩/디코딩 왕복 테스트"""
        original = b"\x01\x23\x45\x67\x89\xab\xcd\xef"

        encoded = encode_base32(original)
        decoded = decode_base32(encoded)

        assert decoded == original

    def test_encode_case_insensitive(self):
        """대소문자 무관 인코딩 테스트"""
        data = b"\x01\x23\x45\x67\x89\xab"

        encoded_upper = encode_base32(data).upper()
        encoded_lower = encode_base32(data).lower()

        decoded_upper = decode_base32(encoded_upper)
        decoded_lower = decode_base32(encoded_lower)

        assert decoded_upper == data
        assert decoded_lower == data


class TestRecordTypeDetermination:
    """KORMARC 레코드 타입 결정 테스트"""

    def test_determine_book_type(self):
        """도서 타입 결정 테스트"""
        from kormarc.models import ControlField, Leader

        leader = Leader(
            record_length=714,
            record_status="a",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=23,
        )

        control_fields = [ControlField(tag="008", data="720101s2025    ko  a")]

        record = type(
            "Record",
            (),
            {
                "leader": leader,
                "control_fields": control_fields,
                "get_control_field": lambda tag: next(
                    (f for f in control_fields if f.tag == tag), None
                ),
            },
        )

        record_type = determine_record_type(record)
        assert record_type == "kormarc_book"

    def test_determine_serial_type(self):
        """연속 간행물 타입 결정 테스트"""
        from kormarc.models import ControlField, Leader

        leader = Leader(
            record_length=714,
            record_status="a",
            type_of_record="a",
            bibliographic_level="s",
            character_encoding="a",
            base_address=23,
        )

        control_fields = [ControlField(tag="008", data="720101s2025    ko  a")]

        record = type(
            "Record",
            (),
            {
                "leader": leader,
                "control_fields": control_fields,
                "get_control_field": lambda tag: next(
                    (f for f in control_fields if f.tag == tag), None
                ),
            },
        )

        record_type = determine_record_type(record)
        assert record_type == "kormarc_serial"

    def test_determine_unknown_type(self):
        """알 수 없는 타입 결정 테스트"""
        from kormarc.models import Leader

        # 유효하지만 정의되지 않은 bibliographic_level 사용
        leader = Leader(
            record_length=714,
            record_status="a",
            type_of_record="a",
            bibliographic_level="i",  # Integrating resource
            character_encoding="a",
            base_address=23,
        )

        record = type(
            "Record",
            (),
            {
                "leader": leader,
                "control_fields": [],
                "get_control_field": lambda tag: None,
            },
        )

        record_type = determine_record_type(record)
        # 'i'는 정의되지 않은 타입이므로 unknown으로 처리
        assert record_type == "kormarc_unknown"


class TestTOONIntegration:
    """TOON 통합 테스트"""

    def test_kormarc_to_toon_pipeline(self):
        """KORMARC → TOON 파이프라인 테스트"""
        from kormarc.parser.kormarc_parser import KORMARCParser

        parser = KORMARCParser()
        generator = TOONGenerator()

        # 샘플 KORMARC 데이터
        sample_kormarc = """00714cam  2200205 a 4500
001 12345
008 720101s2025    ko  a
245 10 |aPython 프로그래밍
"""

        record = parser.parse(sample_kormarc)
        record_type = determine_record_type(record)
        toon_id = generator.generate(record_type)

        assert generator.validate(toon_id) is True
        assert toon_id.startswith(f"{record_type}_")

    def test_toon_json_conversion(self):
        """TOON JSON 변환 테스트"""
        from kormarc.parser.kormarc_parser import KORMARCParser
        from kormarc.toon_generator import toon_to_json

        parser = KORMARCParser()
        generator = TOONGenerator()

        sample_kormarc = """00714cam  2200205 a 4500
001 12345
008 720101s2025    ko  a
245 10 |aPython 프로그래밍
"""

        record = parser.parse(sample_kormarc)
        record_type = determine_record_type(record)
        toon_id = generator.generate(record_type)

        json_data = toon_to_json(record, toon_id)

        assert json_data["toon_id"] == toon_id
        assert json_data["type"] == record_type
        assert "timestamp" in json_data
        assert "raw_kormarc" in json_data
        assert "parsed" in json_data


class TestTOONPerformance:
    """TOON 성능 테스트"""

    def test_generation_performance(self, benchmark):
        """TOON 생성 성능 벤치마크"""
        generator = TOONGenerator()

        benchmark(generator.generate, "kormarc_book")

        # 성능 기준: < 1ms per generation
        assert benchmark.stats.stats.mean < 0.001

    def test_parsing_performance(self, benchmark):
        """TOON 파싱 성능 벤치마크"""
        generator = TOONGenerator()
        toon_id = generator.generate("kormarc_book")

        benchmark(generator.parse, toon_id)

        # 성능 기준: < 0.1ms per parse
        assert benchmark.stats.stats.mean < 0.0001

    def test_validation_performance(self, benchmark):
        """TOON 검증 성능 벤치마크"""
        generator = TOONGenerator()
        toon_id = generator.generate("kormarc_book")

        benchmark(generator.validate, toon_id)

        # 성능 기준: < 0.01ms per validation
        assert benchmark.stats.stats.mean < 0.00001
