"""
Semantic Validator 테스트 - Tier 2

의미론적 검증: 필수 필드, 필드 관계, 데이터 일관성 검증
"""

import pytest

from kormarc.models import ControlField, DataField, Leader, Record, Subfield
from kormarc.validators.semantic_validator import SemanticValidator


class TestRequiredFields:
    """필수 필드 검증 테스트"""

    @pytest.fixture
    def validator(self):
        """SemanticValidator 인스턴스 생성"""
        return SemanticValidator()

    @pytest.fixture
    def valid_record(self):
        """유효한 레코드 생성 (모든 필수 필드 포함)"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [
            ControlField(tag="001", data="TEST001"),
        ]

        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="서울"),
                    Subfield(code="b", data="테스트출판사"),
                    Subfield(code="c", data="2024"),
                ],
            ),
        ]

        return Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

    def test_validate_required_fields_present(self, validator, valid_record):
        """모든 필수 필드가 존재할 때 통과"""
        result = validator.validate_required_fields(valid_record)

        assert result.passed is True
        assert len(result.errors) == 0
        assert result.tier == 2
        assert result.validator_name == "SemanticValidator"

    def test_validate_required_fields_missing_001(self, validator):
        """001 필드 누락 시 실패"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        # 001 필드 없음
        control_fields = []

        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_required_fields(record)

        assert result.passed is False
        assert len(result.errors) >= 1

        # 001 필드 누락 오류 확인
        error_001 = next((e for e in result.errors if e.field_tag == "001"), None)
        assert error_001 is not None
        assert "제어번호" in error_001.message or "001" in error_001.message

    def test_validate_required_fields_missing_040(self, validator):
        """040 필드 누락 시 실패"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [
            ControlField(tag="001", data="TEST001"),
        ]

        # 040 필드 없음
        data_fields = [
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_required_fields(record)

        assert result.passed is False

        # 040 필드 누락 오류 확인
        error_040 = next((e for e in result.errors if e.field_tag == "040"), None)
        assert error_040 is not None
        assert "목록작성기관" in error_040.message or "040" in error_040.message

    def test_validate_required_fields_missing_245(self, validator):
        """245 필드 누락 시 실패"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [
            ControlField(tag="001", data="TEST001"),
        ]

        # 245 필드 없음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_required_fields(record)

        assert result.passed is False

        # 245 필드 누락 오류 확인
        error_245 = next((e for e in result.errors if e.field_tag == "245"), None)
        assert error_245 is not None
        assert "표제" in error_245.message or "245" in error_245.message

    def test_validate_required_fields_missing_260(self, validator):
        """260 필드 누락 시 실패"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [
            ControlField(tag="001", data="TEST001"),
        ]

        # 260 필드 없음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_required_fields(record)

        assert result.passed is False

        # 260 필드 누락 오류 확인
        error_260 = next((e for e in result.errors if e.field_tag == "260"), None)
        assert error_260 is not None
        assert "발행사항" in error_260.message or "260" in error_260.message

    def test_validate_conditional_fields_100_with_book(self, validator):
        """도서일 때 100 필드 없으면 경고"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",  # 도서
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [
            ControlField(tag="001", data="TEST001"),
        ]

        # 100 필드 없음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_required_fields(record)

        # 필수 필드는 모두 있으므로 passed=True
        assert result.passed is True

        # 하지만 100 필드 누락 경고가 있어야 함
        assert len(result.warnings) >= 1
        warning_100 = next((w for w in result.warnings if w.field_tag == "100"), None)
        assert warning_100 is not None
        assert "저자" in warning_100.message or "100" in warning_100.message


class TestFieldRelationships:
    """필드 관계 검증 테스트"""

    @pytest.fixture
    def validator(self):
        """SemanticValidator 인스턴스 생성"""
        return SemanticValidator()

    def test_validate_260_has_pub_year(self, validator):
        """260 필드에 발행년($c) 존재 확인"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [ControlField(tag="001", data="TEST001")]

        # 260 필드에 $c (발행년) 있음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="서울"),
                    Subfield(code="b", data="출판사"),
                    Subfield(code="c", data="2024"),
                ],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_field_relationships(record)

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_260_missing_pub_year(self, validator):
        """260 필드에 발행년($c) 누락 시 오류"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [ControlField(tag="001", data="TEST001")]

        # 260 필드에 $c (발행년) 없음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="서울"),
                    Subfield(code="b", data="출판사"),
                ],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_field_relationships(record)

        assert result.passed is False
        assert len(result.errors) >= 1

        # 260$c 누락 오류 확인
        error_260c = next((e for e in result.errors if e.field_tag == "260"), None)
        assert error_260c is not None
        assert "발행년" in error_260c.message or "$c" in error_260c.message

    def test_validate_100_with_245(self, validator):
        """100 필드가 있으면 245도 있어야 함"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [ControlField(tag="001", data="TEST001")]

        # 100 필드 있고 245도 있음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="100",
                indicator1="1",
                indicator2=" ",
                subfields=[Subfield(code="a", data="홍길동")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_field_relationships(record)

        assert result.passed is True

    def test_validate_100_without_245(self, validator):
        """100 필드가 있는데 245가 없으면 오류"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [ControlField(tag="001", data="TEST001")]

        # 100 필드 있지만 245 없음
        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="100",
                indicator1="1",
                indicator2=" ",
                subfields=[Subfield(code="a", data="홍길동")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="c", data="2024")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_field_relationships(record)

        assert result.passed is False

        # 100+245 관계 오류 확인
        error_100 = next((e for e in result.errors if "100" in e.message), None)
        assert error_100 is not None
        assert "245" in error_100.message


class TestRecordValidation:
    """전체 레코드 검증 테스트"""

    @pytest.fixture
    def validator(self):
        """SemanticValidator 인스턴스 생성"""
        return SemanticValidator()

    def test_validate_record_complete(self, validator):
        """완전한 레코드 검증 - 모든 검증 통과"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        control_fields = [ControlField(tag="001", data="TEST001")]

        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="100",
                indicator1="1",
                indicator2=" ",
                subfields=[Subfield(code="a", data="홍길동")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="서울"),
                    Subfield(code="b", data="출판사"),
                    Subfield(code="c", data="2024"),
                ],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_record(record)

        assert result.passed is True
        assert result.tier == 2
        assert result.validator_name == "SemanticValidator"

    def test_validate_record_with_errors(self, validator):
        """오류가 있는 레코드 검증"""
        leader = Leader(
            record_length=0,
            record_status="n",
            type_of_record="a",
            bibliographic_level="m",
            character_encoding="a",
            base_address=0,
        )

        # 001 누락, 260$c 누락
        control_fields = []

        data_fields = [
            DataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="211009")],
            ),
            DataField(
                tag="245",
                indicator1="1",
                indicator2="0",
                subfields=[Subfield(code="a", data="테스트 도서명")],
            ),
            DataField(
                tag="260",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data="서울")],
            ),
        ]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        result = validator.validate_record(record)

        assert result.passed is False
        assert len(result.errors) >= 2  # 001 누락, 260$c 누락
