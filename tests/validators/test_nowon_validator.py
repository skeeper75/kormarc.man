"""
Nowon Validator 테스트

노원구 KORMARC 규칙 검증 기능 테스트
"""


from kormarc.validators.nowon_validator import NowonValidator

from kormarc.models.fields import DataField, Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record


class TestNowon040Validation:
    """노원구 040 필드 검증 테스트"""

    def test_validate_040_correct_format(self) -> None:
        """유효한 040 필드 검증 - 정상 케이스"""
        # Arrange: 노원구 형식에 맞는 040 필드
        leader = Leader.from_string("00714cam  2200205 a 4500")
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="211032"),  # 노원정보도서관
                    Subfield(code="c", data="211032"),
                    Subfield(code="d", data="211032"),
                ],
            )
        ]
        record = Record(leader=leader, data_fields=data_fields)

        # Act: 040 필드 검증
        validator = NowonValidator()
        result = validator.validate_040_field(record)

        # Assert: 검증 통과
        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_040_missing_field(self) -> None:
        """040 필드 누락 검증 - 필드 없으면 오류"""
        # Arrange: 040 필드가 없는 Record
        leader = Leader.from_string("00714cam  2200205 a 4500")
        record = Record(leader=leader, data_fields=[])

        # Act: 040 필드 검증
        validator = NowonValidator()
        result = validator.validate_040_field(record)

        # Assert: 040 필드 누락 오류
        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0].field_tag == "040"
        assert "필수" in result.errors[0].message

    def test_validate_040_wrong_subfield(self) -> None:
        """040 필드 서브필드 검증 - 잘못된 서브필드 코드"""
        # Arrange: 필수 서브필드 누락
        leader = Leader.from_string("00714cam  2200205 a 4500")
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="211032"),  # $a만 있고 $c, $d 누락
                ],
            )
        ]
        record = Record(leader=leader, data_fields=data_fields)

        # Act: 040 필드 검증
        validator = NowonValidator()
        result = validator.validate_040_field(record)

        # Assert: 필수 서브필드 누락 오류
        assert result.passed is False
        assert len(result.errors) >= 1
        assert "서브필드" in result.errors[0].message

    def test_validate_040_invalid_code(self) -> None:
        """040 필드 기관코드 검증 - 잘못된 기관코드"""
        # Arrange: 노원구가 아닌 기관코드
        leader = Leader.from_string("00714cam  2200205 a 4500")
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="999999"),  # 잘못된 기관코드
                    Subfield(code="c", data="999999"),
                    Subfield(code="d", data="999999"),
                ],
            )
        ]
        record = Record(leader=leader, data_fields=data_fields)

        # Act: 040 필드 검증
        validator = NowonValidator()
        result = validator.validate_040_field(record)

        # Assert: 경고 발생 (다른 기관 코드)
        assert len(result.warnings) >= 1
        assert "노원구" in result.warnings[0].message or "기관" in result.warnings[0].message
