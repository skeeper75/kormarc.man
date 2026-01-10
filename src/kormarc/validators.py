"""
KORMARC 데이터 검증 모듈

ISBN, 필수 필드, KDC 분류코드 검증 기능 제공
"""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from kormarc.kormarc_builder import BookInfo

# ISBN 검증 패턴
ISBN10_PATTERN = re.compile(r"^(\d{9}[\dXx])$")
ISBN13_PATTERN = re.compile(r"^(\d{13})$")

# KDC 분류코드 패턴 (0-9로 시작, 최대 3자리)
KDC_PATTERN = re.compile(r"^([0-9])(\d{0,2})$")


@dataclass
class ValidationResult:
    """검증 결과"""

    is_valid: bool
    """유효성 여부"""

    errors: list[str]
    """오류 메시지 리스트"""

    warnings: list[str]
    """경고 메시지 리스트"""

    @property
    def has_errors(self) -> bool:
        """오류 존재 여부"""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """경고 존재 여부"""
        return len(self.warnings) > 0


class ISBNValidator:
    """ISBN 검증기"""

    @staticmethod
    def normalize(isbn: str) -> str:
        """
        ISBN 정규화 (하이픈, 공백 제거)

        Args:
            isbn: 원본 ISBN

        Returns:
            정규화된 ISBN
        """
        return isbn.replace("-", "").replace(" ", "")

    @staticmethod
    def validate(isbn: str) -> ValidationResult:
        """
        ISBN 검증

        Args:
            isbn: ISBN 문자열

        Returns:
            ValidationResult 객체
        """
        errors = []
        warnings = []

        # 정규화
        normalized = ISBNValidator.normalize(isbn)

        # 길이 검증
        if len(normalized) not in (10, 13):
            errors.append(f"ISBN 길이 오류: {len(normalized)}자리 (10 또는 13자리 필요)")

        # ISBN-10 검증
        if len(normalized) == 10:
            if not ISBN10_PATTERN.match(normalized):
                errors.append("ISBN-10 형식 오류")
            else:
                # 체크섬 검증
                if not ISBNValidator._validate_isbn10_checksum(normalized):
                    errors.append("ISBN-10 체크섬 오류")

        # ISBN-13 검증
        elif len(normalized) == 13:
            if not ISBN13_PATTERN.match(normalized):
                errors.append("ISBN-13 형식 오류")
            else:
                # 체크섬 검증
                if not ISBNValidator._validate_isbn13_checksum(normalized):
                    errors.append("ISBN-13 체크섬 오류")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def _validate_isbn10_checksum(isbn: str) -> bool:
        """
        ISBN-10 체크섬 검증

        Args:
            isbn: ISBN-10 문자열

        Returns:
            체크섬 유효성
        """
        total = 0
        for i, char in enumerate(isbn[:9]):
            total += int(char) * (10 - i)

        check_digit = isbn[9].upper()
        checksum = (11 - (total % 11)) % 11

        if checksum == 10:
            return check_digit == "X"
        return check_digit == str(checksum)

    @staticmethod
    def _validate_isbn13_checksum(isbn: str) -> bool:
        """
        ISBN-13 체크섬 검증

        ISBN-13 체크섬 알고리즘:
        1. 홀수번째 자리에 1, 짝수번째 자리에 3을 곱합니다
        2. 모두 더합니다
        3. 10으로 나눈 나머지를 구합니다
        4. 10에서 나머지를 뺍니다 (나머지가 0이면 0)

        Args:
            isbn: ISBN-13 문자열

        Returns:
            체크섬 유효성
        """
        total = 0
        for i, char in enumerate(isbn[:12]):
            digit = int(char)
            # 0-based index: 짝수 인덱스 = 1번째 자리, 홀수 인덱스 = 2번째 자리
            weight = 1 if i % 2 == 0 else 3
            total += digit * weight

        remainder = total % 10
        checksum = 10 - remainder if remainder != 0 else 0
        return checksum == int(isbn[12])


class KDCValidator:
    """KDC (한국십진분류표) 검증기"""

    # KDC 주 분류
    KDC_CATEGORIES = {
        "0": "총류",
        "1": "철학",
        "2": "종교",
        "3": "사회과학",
        "4": "자연과학",
        "5": "기술과학",
        "6": "예술",
        "7": "언어",
        "8": "문학",
        "9": "역사",
    }

    @staticmethod
    def validate(kdc: str) -> ValidationResult:
        """
        KDC 분류코드 검증

        Args:
            kdc: KDC 분류코드

        Returns:
            ValidationResult 객체
        """
        errors = []
        warnings = []

        if not kdc:
            errors.append("KDC 분류코드가 비어있습니다")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 형식 검증
        if not KDC_PATTERN.match(kdc):
            errors.append(f"KDC 형식 오류: {kdc} (0-9로 시작, 최대 3자리 숫자)")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # 주 분류 검증
        main_category = kdc[0]
        if main_category not in KDCValidator.KDC_CATEGORIES:
            warnings.append(
                f"알 수 없는 주 분류: {main_category} "
                f"(유효한 분류: {', '.join(KDCValidator.KDC_CATEGORIES.keys())})"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    @staticmethod
    def get_category_name(kdc: str) -> str:
        """
        KDC 코드에서 주제명 반환

        Args:
            kdc: KDC 분류코드

        Returns:
            주제명 (알 수 없으면 "알 수 없음")
        """
        if not kdc:
            return "알 수 없음"
        return KDCValidator.KDC_CATEGORIES.get(kdc[0], "알 수 없음")


class BookInfoValidator(BaseModel):
    """
    BookInfo 검증기

    Pydantic 기반 자동 검증
    """

    isbn: str = Field(..., min_length=10, max_length=17)
    title: str = Field(..., min_length=1)
    author: str | None = None
    publisher: str | None = None
    pub_year: str | None = None
    pages: int | None = Field(None, ge=1)
    kdc: str | None = None
    category: str = "book"
    price: int | None = Field(None, ge=0)
    description: str | None = None

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        """ISBN 검증"""
        normalized = ISBNValidator.normalize(v)
        result = ISBNValidator.validate(normalized)
        if not result.is_valid:
            raise ValueError(f"ISBN 검증 실패: {', '.join(result.errors)}")
        return normalized

    @field_validator("kdc")
    @classmethod
    def validate_kdc(cls, v: str | None) -> str | None:
        """KDC 검증"""
        if v is None:
            return None
        result = KDCValidator.validate(v)
        if not result.is_valid:
            raise ValueError(f"KDC 검증 실패: {', '.join(result.errors)}")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """카테고리 검증"""
        valid_categories = ["book", "serial", "academic", "comic"]
        if v not in valid_categories:
            raise ValueError(
                f"유효하지 않은 카테고리: {v} (유효한 카테고리: {', '.join(valid_categories)})"
            )
        return v

    @field_validator("pub_year")
    @classmethod
    def validate_pub_year(cls, v: str | None) -> str | None:
        """발행년 검증"""
        if v is None:
            return None

        # YYYY 또는 YYYYMM 형식
        year_pattern = re.compile(r"^(\d{4})(\d{2})?$")
        if not year_pattern.match(v):
            raise ValueError(f"발행년 형식 오류: {v} (YYYY 또는 YYYYMM 형식 필요)")

        # 연도 범위 검증 (1900-현재년도+5)
        year = int(v[:4])
        current_year = 2026  # TODO: 동적 연도
        if year < 1900 or year > current_year + 5:
            raise ValueError(f"발행년 범위 오류: {year} (1900-{current_year + 5} 범위 필요)")

        return v


class RequiredFieldsValidator:
    """
    필수 필드 검증기

    KORMARC 필수 필드 확인
    """

    # 노원구 필수 필드 목록
    REQUIRED_FIELDS = {
        "001": "제어번호",
        "040": "목록작성기관",
        "245": "표제",
    }

    # 조건부 필수 필드
    CONDITIONAL_FIELDS = {
        "020": "ISBN (권장)",
        "100": "주요 저자 (저자 있는 경우)",
        "260": "발행사항",
        "300": "형태사항 (페이지수 있는 경우)",
        "650": "주제명 (KDC 있는 경우)",
    }

    @staticmethod
    def validate_fields_present(
        has_isbn: bool,
        has_author: bool,
        has_publisher: bool,
        has_pages: bool,
        has_kdc: bool,
    ) -> ValidationResult:
        """
        필수 필드 존재 여부 검증

        Args:
            has_isbn: ISBN 존재 여부
            has_author: 저자 존재 여부
            has_publisher: 발행처 존재 여부
            has_pages: 페이지수 존재 여부
            has_kdc: KDC 존재 여부

        Returns:
            ValidationResult 객체
        """
        errors = []
        warnings = []

        # 001, 040, 245는 빌더에서 자동 생성하므로 항상 유효

        # 조건부 필드 검증
        if not has_isbn:
            warnings.append("ISBN이 없습니다 (권장)")

        if has_author and not has_author:
            # 저자가 있는데 100 필드가 없으면 경고
            pass

        if not has_publisher:
            warnings.append("발행처 정보가 없습니다")

        if not has_kdc:
            warnings.append("KDC 분류코드가 없습니다")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )


def validate_book_info(book_info: "BookInfo") -> ValidationResult:
    """
    BookInfo 종합 검증

    Args:
        book_info: BookInfo 객체

    Returns:
        ValidationResult 객체
    """
    all_errors = []
    all_warnings = []

    # ISBN 검증
    isbn_result = ISBNValidator.validate(book_info.isbn)
    all_errors.extend(isbn_result.errors)
    all_warnings.extend(isbn_result.warnings)

    # KDC 검증
    if book_info.kdc:
        kdc_result = KDCValidator.validate(book_info.kdc)
        all_errors.extend(kdc_result.errors)
        all_warnings.extend(kdc_result.warnings)

    # 필수 필드 검증
    required_result = RequiredFieldsValidator.validate_fields_present(
        has_isbn=bool(book_info.isbn),
        has_author=bool(book_info.author),
        has_publisher=bool(book_info.publisher),
        has_pages=bool(book_info.pages),
        has_kdc=bool(book_info.kdc),
    )
    all_errors.extend(required_result.errors)
    all_warnings.extend(required_result.warnings)

    return ValidationResult(
        is_valid=len(all_errors) == 0,
        errors=all_errors,
        warnings=all_warnings,
    )


# 모듈 레벨 테스트
if __name__ == "__main__":
    # ISBN 검증 테스트
    print("=== ISBN 검증 테스트 ===")

    test_isbns = [
        "9788968481607",  # 유효한 ISBN-13 (파이썬 코딩의 기술)
        "9788960777330",  # 유효한 ISBN-13 (이것이 우다다)
        "8956744217",  # 유효한 ISBN-10 (나의 라임 오렌지 나무)
        "156881111X",  # 유효한 ISBN-10
        "1234567890",  # 체크섬 오류
        "invalid",  # 형식 오류
    ]

    for isbn in test_isbns:
        result = ISBNValidator.validate(isbn)
        print(f"{isbn}: {'VALID' if result.is_valid else 'INVALID'}")
        if result.errors:
            print(f"  Errors: {result.errors}")

    # KDC 검증 테스트
    print("\n=== KDC 검증 테스트 ===")

    test_kdcs = ["005", "813", "123", "invalid", ""]

    for kdc in test_kdcs:
        result = KDCValidator.validate(kdc)
        category = KDCValidator.get_category_name(kdc)
        print(f"{kdc} ({category}): {'VALID' if result.is_valid else 'INVALID'}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
