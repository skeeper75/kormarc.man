"""
Structure Validator - KORMARC 레코드 구조 검증

Tier 1 검증: Leader, Control Fields, Data Fields 구조 검증
"""

import re
from dataclasses import dataclass, field
from typing import Literal

from kormarc.models.leader import Leader
from kormarc.models.record import Record

# 검증 심각도 상수
SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARNING"

# 005 필드 형식 패턴 (YYYYMMDDHHmmss.f)
FIELD_005_PATTERN = re.compile(r"^\d{14}\.\d$")


@dataclass
class ValidationError:
    """검증 오류"""

    severity: Literal["ERROR", "WARNING"]
    field_tag: str | None
    message: str
    suggestion: str | None = None


@dataclass
class ValidationWarning:
    """검증 경고"""

    field_tag: str | None
    message: str
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """검증 결과"""

    tier: int
    validator_name: str
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)


class StructureValidator:
    """
    KORMARC 레코드 구조 검증기 (Tier 1)

    Leader, Control Fields, Data Fields의 기본 구조를 검증합니다.
    """

    def __init__(self) -> None:
        """구조 검증기 초기화"""
        self.tier = 1
        self.validator_name = "StructureValidator"

    def validate_leader(self, leader: Leader) -> ValidationResult:
        """
        Leader 필드 검증

        Args:
            leader: Leader 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # Leader 객체가 Pydantic 모델이므로 이미 기본 검증은 완료됨
        # 추가 비즈니스 로직 검증이 필요하면 여기에 추가

        # 모든 검증 통과
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )

    def validate_control_fields(self, record: Record) -> ValidationResult:
        """
        Control Fields 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # 001 필드 필수 검증
        has_001 = any(cf.tag == "001" for cf in record.control_fields)
        if not has_001:
            errors.append(
                ValidationError(
                    severity=SEVERITY_ERROR,
                    field_tag="001",
                    message="001 필드는 필수입니다",
                    suggestion="제어번호(001) 필드를 추가하세요",
                )
            )

        # 005 필드 형식 검증
        field_005 = next((cf for cf in record.control_fields if cf.tag == "005"), None)
        if field_005:
            if not FIELD_005_PATTERN.match(field_005.data):
                errors.append(
                    ValidationError(
                        severity=SEVERITY_ERROR,
                        field_tag="005",
                        message="005 필드 형식 오류: YYYYMMDDHHmmss.f 형식이어야 합니다",
                        suggestion=f"현재값: {field_005.data}, 예시: 20260111120000.0",
                    )
                )

        # 모든 검증 통과 여부
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )

    def validate_record(self, record: Record) -> ValidationResult:
        """
        전체 레코드 구조 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # Leader 검증
        leader_result = self.validate_leader(record.leader)
        errors.extend(leader_result.errors)
        warnings.extend(leader_result.warnings)

        # Control Fields 검증
        control_result = self.validate_control_fields(record)
        errors.extend(control_result.errors)
        warnings.extend(control_result.warnings)

        # 모든 검증 통과 여부
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )
