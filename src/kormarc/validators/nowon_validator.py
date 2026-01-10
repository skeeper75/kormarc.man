"""
Nowon Validator - 노원구 KORMARC 규칙 검증

Tier 3 검증: 노원구 도서관 특화 규칙 검증
"""

from kormarc.models.record import Record
from kormarc.validators.structure_validator import (
    SEVERITY_ERROR,
    ValidationError,
    ValidationResult,
    ValidationWarning,
)

# 노원구 도서관 기관코드 목록
NOWON_LIBRARY_CODES = {
    "211032": "노원정보도서관",
    "211033": "노원어린이도서관",
    "211034": "노원청소년도서관",
}

# 040 필드 필수 서브필드
FIELD_040_REQUIRED_SUBFIELDS = ["a", "c", "d"]


class NowonValidator:
    """
    노원구 KORMARC 규칙 검증기 (Tier 3)

    노원구 도서관 특화 규칙을 검증합니다.
    """

    def __init__(self) -> None:
        """노원구 검증기 초기화"""
        self.tier = 3
        self.validator_name = "NowonValidator"

    def validate_040_field(self, record: Record) -> ValidationResult:
        """
        040 필드 검증 (목록작성기관)

        노원구 규칙:
        - 040 필드 필수
        - $a, $c, $d 서브필드 필수
        - 기관코드는 노원구 도서관 코드 권장

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # 040 필드 존재 확인
        field_040 = next((df for df in record.data_fields if df.tag == "040"), None)

        if not field_040:
            errors.append(
                ValidationError(
                    severity=SEVERITY_ERROR,
                    field_tag="040",
                    message="040 필드(목록작성기관)는 필수입니다",
                    suggestion="040 필드를 추가하세요",
                )
            )
            # 필드가 없으면 더 이상 검증 불가
            return ValidationResult(
                tier=self.tier,
                validator_name=self.validator_name,
                passed=False,
                errors=errors,
                warnings=warnings,
            )

        # 필수 서브필드 확인
        subfield_codes = [sf.code for sf in field_040.subfields]

        for required_code in FIELD_040_REQUIRED_SUBFIELDS:
            if required_code not in subfield_codes:
                errors.append(
                    ValidationError(
                        severity=SEVERITY_ERROR,
                        field_tag="040",
                        message=f"040 필드에 서브필드 ${required_code}가 필요합니다",
                        suggestion=f"서브필드 ${required_code}를 추가하세요",
                    )
                )

        # 기관코드 확인 (경고)
        subfield_a = next((sf for sf in field_040.subfields if sf.code == "a"), None)
        if subfield_a:
            if subfield_a.data not in NOWON_LIBRARY_CODES:
                warnings.append(
                    ValidationWarning(
                        field_tag="040",
                        message=f"노원구 도서관 기관코드가 아닙니다: {subfield_a.data}",
                        suggestion=f"노원구 기관코드 사용을 권장합니다: {', '.join(NOWON_LIBRARY_CODES.keys())}",
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
        전체 레코드 노원구 규칙 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # 040 필드 검증
        result_040 = self.validate_040_field(record)
        errors.extend(result_040.errors)
        warnings.extend(result_040.warnings)

        # 모든 검증 통과 여부
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )
