"""
Structure Validator 테스트

KORMARC 레코드 구조 검증 기능 테스트
"""

import pytest

from kormarc.models.leader import Leader
from kormarc.validators.structure_validator import (
    StructureValidator,
)


class TestLeaderValidation:
    """Leader 필드 검증 테스트"""

    def test_validate_leader_valid(self) -> None:
        """유효한 Leader 검증 - 정상 케이스"""
        # Arrange: 유효한 24자리 Leader 생성
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        # Act: Leader 검증
        validator = StructureValidator()
        result = validator.validate_leader(leader)

        # Assert: 검증 통과
        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_leader_invalid_length(self) -> None:
        """잘못된 길이의 Leader - 길이 오류"""
        # Arrange: 23자리 Leader (잘못된 길이)
        invalid_leader_str = "00714cam  2200205 a 45"

        # Act & Assert: 길이 오류로 생성 실패
        with pytest.raises(Exception):  # LeaderValidationError
            Leader.from_string(invalid_leader_str)

    def test_validate_leader_invalid_status(self) -> None:
        """잘못된 record_status - 값 오류"""
        # Arrange: 잘못된 record_status (position 5 = 'x')
        invalid_leader_str = "00714xam  2200205 a 4500"

        # Act & Assert: record_status 검증 실패
        with pytest.raises(Exception):  # LeaderValidationError
            Leader.from_string(invalid_leader_str)

    def test_validate_leader_invalid_type_of_record(self) -> None:
        """잘못된 type_of_record - 값 오류"""
        # Arrange: 잘못된 type_of_record (position 6 = 'z')
        invalid_leader_str = "00714czm  2200205 a 4500"

        # Act & Assert: type_of_record 검증 실패
        with pytest.raises(Exception):  # LeaderValidationError
            Leader.from_string(invalid_leader_str)

    def test_validate_leader_invalid_bibliographic_level(self) -> None:
        """잘못된 bibliographic_level - 값 오류"""
        # Arrange: 잘못된 bibliographic_level (position 7 = 'z')
        invalid_leader_str = "00714caz  2200205 a 4500"

        # Act & Assert: bibliographic_level 검증 실패
        with pytest.raises(Exception):  # LeaderValidationError
            Leader.from_string(invalid_leader_str)


class TestControlFieldsValidation:
    """Control Fields 검증 테스트"""

    def test_validate_control_fields_valid(self) -> None:
        """유효한 Control Fields 검증 - 정상 케이스"""
        # Arrange: 001, 005 필드를 포함한 Record
        from kormarc.models.fields import ControlField

        leader = Leader.from_string("00714cam  2200205 a 4500")
        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="005", data="20260111120000.0"),
        ]

        from kormarc.models.record import Record

        record = Record(leader=leader, control_fields=control_fields)

        # Act: Control Fields 검증
        validator = StructureValidator()
        result = validator.validate_control_fields(record)

        # Assert: 검증 통과
        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_001_required(self) -> None:
        """001 필드 필수 검증 - 001 필드 없으면 오류"""
        # Arrange: 001 필드가 없는 Record
        from kormarc.models.record import Record

        leader = Leader.from_string("00714cam  2200205 a 4500")
        record = Record(leader=leader, control_fields=[])

        # Act: Control Fields 검증
        validator = StructureValidator()
        result = validator.validate_control_fields(record)

        # Assert: 001 필드 누락 오류
        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0].field_tag == "001"
        assert "필수" in result.errors[0].message

    def test_validate_005_format(self) -> None:
        """005 필드 형식 검증 - 잘못된 형식이면 오류"""
        # Arrange: 잘못된 005 형식
        from kormarc.models.fields import ControlField
        from kormarc.models.record import Record

        leader = Leader.from_string("00714cam  2200205 a 4500")
        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="005", data="invalid-format"),  # 잘못된 형식
        ]
        record = Record(leader=leader, control_fields=control_fields)

        # Act: Control Fields 검증
        validator = StructureValidator()
        result = validator.validate_control_fields(record)

        # Assert: 005 형식 오류
        assert result.passed is False
        assert len(result.errors) == 1
        assert result.errors[0].field_tag == "005"
        assert "형식" in result.errors[0].message
