"""
Semantic Validator - KORMARC 의미론적 검증

Tier 2 검증: 필수 필드, 필드 관계, 데이터 일관성 검증
"""

from kormarc.models.record import Record
from kormarc.validators.structure_validator import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
)

# 필수 필드 상수
REQUIRED_FIELDS = {
    "001": {"description": "제어번호", "always_required": True},
    "040": {"description": "목록작성기관", "always_required": True},
    "245": {"description": "표제", "always_required": True},
    "260": {"description": "발행사항", "always_required": True},
}

# 조건부 필수 필드 상수
CONDITIONAL_FIELDS = {
    "100": {"description": "저자명", "condition": "if_book"},
    "300": {"description": "형태사항", "condition": "if_physical"},
}

# 필드 관계 규칙
FIELD_RELATIONSHIPS = [
    {
        "primary": "260",
        "requires_subfield": "c",
        "message": "발행사항(260) 필드에는 발행년($c)이 필수입니다",
        "suggestion": "260 필드에 $c 서브필드를 추가하세요",
    },
    {
        "primary": "100",
        "requires": ["245"],
        "message": "저자(100) 필드가 있으면 표제(245) 필드도 필수입니다",
        "suggestion": "245 필드를 추가하세요",
    },
]


class SemanticValidator:
    """
    KORMARC 의미론적 검증기 (Tier 2)

    필수 필드, 필드 관계, 데이터 일관성을 검증합니다.
    """

    def __init__(self) -> None:
        """의미론적 검증기 초기화"""
        self.tier = 2
        self.validator_name = "SemanticValidator"

    def validate_required_fields(self, record: Record) -> ValidationResult:
        """
        필수 필드 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # Control Fields 및 Data Fields 태그 추출
        control_field_tags = {cf.tag for cf in record.control_fields}
        data_field_tags = {df.tag for df in record.data_fields}

        # 필수 필드 검증
        self._check_required_fields(control_field_tags, data_field_tags, errors)

        # 조건부 필수 필드 검증 (경고)
        self._check_conditional_fields(record.leader.type_of_record, data_field_tags, warnings)

        # 모든 검증 통과 여부
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )

    def _check_required_fields(
        self,
        control_tags: set[str],
        data_tags: set[str],
        errors: list[ValidationError],
    ) -> None:
        """
        필수 필드 존재 여부 확인

        Args:
            control_tags: Control Field 태그 집합
            data_tags: Data Field 태그 집합
            errors: 오류 리스트 (누락 시 추가)
        """
        for tag, info in REQUIRED_FIELDS.items():
            # 001은 Control Field, 나머지는 Data Field
            tags_to_check = control_tags if tag == "001" else data_tags

            if tag not in tags_to_check:
                errors.append(
                    ValidationError(
                        severity="ERROR",
                        field_tag=tag,
                        message=f"필수 필드 누락: {info['description']}({tag}) 필드가 없습니다",
                        suggestion=f"{tag} 필드를 추가하세요",
                    )
                )

    def _check_conditional_fields(
        self,
        type_of_record: str,
        data_tags: set[str],
        warnings: list[ValidationWarning],
    ) -> None:
        """
        조건부 필수 필드 확인 (경고)

        Args:
            type_of_record: 레코드 유형 (Leader의 type_of_record)
            data_tags: Data Field 태그 집합
            warnings: 경고 리스트 (누락 시 추가)
        """
        # 100 필드: 도서(type_of_record='a')일 때 권장
        if type_of_record == "a" and "100" not in data_tags:
            warnings.append(
                ValidationWarning(
                    field_tag="100",
                    message="권장 필드 누락: 도서 레코드에는 저자명(100) 필드가 권장됩니다",
                    suggestion="100 필드를 추가하는 것을 고려하세요",
                )
            )

    def validate_field_relationships(self, record: Record) -> ValidationResult:
        """
        필드 간 관계 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        data_field_tags = {df.tag for df in record.data_fields}

        # 필드 관계 규칙 적용
        for rule in FIELD_RELATIONSHIPS:
            primary_tag = rule["primary"]

            # 서브필드 요구사항 검증
            if "requires_subfield" in rule:
                primary_field = next(
                    (df for df in record.data_fields if df.tag == primary_tag), None
                )
                if primary_field:
                    required_subfield = rule["requires_subfield"]
                    has_subfield = any(
                        sf.code == required_subfield for sf in primary_field.subfields
                    )
                    if not has_subfield:
                        errors.append(
                            ValidationError(
                                severity="ERROR",
                                field_tag=primary_tag,
                                message=rule["message"],
                                suggestion=rule["suggestion"],
                            )
                        )

            # 다른 필드 요구사항 검증
            if "requires" in rule and primary_tag in data_field_tags:
                for required_tag in rule["requires"]:
                    if required_tag not in data_field_tags:
                        errors.append(
                            ValidationError(
                                severity="ERROR",
                                field_tag=primary_tag,
                                message=rule["message"],
                                suggestion=rule["suggestion"],
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
        전체 레코드 의미론적 검증

        Args:
            record: Record 객체

        Returns:
            ValidationResult: 통합 검증 결과
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # 필수 필드 검증
        required_result = self.validate_required_fields(record)
        errors.extend(required_result.errors)
        warnings.extend(required_result.warnings)

        # 필드 관계 검증
        relationship_result = self.validate_field_relationships(record)
        errors.extend(relationship_result.errors)
        warnings.extend(relationship_result.warnings)

        # 모든 검증 통과 여부
        passed = len(errors) == 0

        return ValidationResult(
            tier=self.tier,
            validator_name=self.validator_name,
            passed=passed,
            errors=errors,
            warnings=warnings,
        )
