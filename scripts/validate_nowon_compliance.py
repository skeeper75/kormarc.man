#!/usr/bin/env python3
"""
노원구립도서관 시방서 준수 검증 스크립트

100개 KORMARC 레코드를 노원구 시방서 기준으로 검증하고 보고서 생성
"""

import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Field040Analysis:
    """040 필드 분석 결과"""

    exists: bool
    has_subfield_a: bool
    has_subfield_b: bool
    has_subfield_c: bool
    has_subfield_d: bool
    has_subfield_e: bool
    subfield_a_value: str | None
    subfield_b_value: str | None
    subfield_c_value: str | None
    subfield_d_value: str | None
    subfield_e_value: str | None
    is_nlk_format: bool
    errors: list[str]


@dataclass
class RecordValidation:
    """레코드 검증 결과"""

    toon_id: str
    isbn: str
    title: str
    kdc_code: str | None
    pub_year: int | None

    # 필수 필드
    has_001: bool
    has_040: bool
    has_245: bool
    has_260: bool

    # 권장 필드
    has_020: bool
    has_100: bool
    has_650: bool

    # 040 필드 상세 분석
    field_040: Field040Analysis

    # 260 필드 분석
    has_260_subfield_c: bool

    # 검증 결과
    is_pass: bool
    is_conditional_pass: bool
    is_fail: bool
    errors: list[str]
    warnings: list[str]

    @property
    def status(self) -> str:
        if self.is_pass:
            return "합격"
        elif self.is_conditional_pass:
            return "조건부합격"
        else:
            return "불합격"


def get_field_by_tag(parsed_data: dict[str, Any], tag: str) -> list[dict[str, Any]]:
    """
    태그로 필드 검색 (control_fields와 data_fields 모두 검색)

    Args:
        parsed_data: 파싱된 KORMARC 데이터
        tag: 필드 태그 (예: "001", "040", "245")

    Returns:
        해당 태그의 필드 리스트
    """
    results = []

    # Control fields 검색 (001, 003, 005, 008 등)
    if tag in ("001", "003", "005", "008"):
        control_fields = parsed_data.get("control_fields", [])
        for field in control_fields:
            if field.get("tag") == tag:
                results.append(field)
    else:
        # Data fields 검색 (020, 040, 245, 260 등)
        data_fields = parsed_data.get("data_fields", [])
        for field in data_fields:
            if field.get("tag") == tag:
                results.append(field)

    return results


def get_subfield_value(field: dict[str, Any], code: str) -> str | None:
    """
    필드에서 특정 서브필드 값 추출

    Args:
        field: 필드 딕셔너리
        code: 서브필드 코드 (예: "a", "b", "c")

    Returns:
        서브필드 값 또는 None
    """
    subfields = field.get("subfields", [])
    for subfield in subfields:
        if subfield.get("code") == code:
            return subfield.get("data")
    return None


def analyze_field_040(parsed_data: dict[str, Any]) -> Field040Analysis:
    """
    040 필드 상세 분석

    Args:
        parsed_data: 파싱된 KORMARC 데이터

    Returns:
        Field040Analysis 객체
    """
    errors = []
    fields_040 = get_field_by_tag(parsed_data, "040")

    if not fields_040:
        return Field040Analysis(
            exists=False,
            has_subfield_a=False,
            has_subfield_b=False,
            has_subfield_c=False,
            has_subfield_d=False,
            has_subfield_e=False,
            subfield_a_value=None,
            subfield_b_value=None,
            subfield_c_value=None,
            subfield_d_value=None,
            subfield_e_value=None,
            is_nlk_format=False,
            errors=["040 필드가 존재하지 않음"],
        )

    # 첫 번째 040 필드 분석
    field_040 = fields_040[0]

    subfield_a = get_subfield_value(field_040, "a")
    subfield_b = get_subfield_value(field_040, "b")
    subfield_c = get_subfield_value(field_040, "c")
    subfield_d = get_subfield_value(field_040, "d")
    subfield_e = get_subfield_value(field_040, "e")

    # NLK 형식 검증
    is_nlk_format = True

    if subfield_a != "NLK":
        errors.append(f"040$a 오류: '{subfield_a}' (예상: 'NLK')")
        is_nlk_format = False

    if subfield_b != "kor":
        errors.append(f"040$b 오류: '{subfield_b}' (예상: 'kor')")
        is_nlk_format = False

    if subfield_c != "(NLK)":
        errors.append(f"040$c 오류: '{subfield_c}' (예상: '(NLK)')")
        is_nlk_format = False

    if subfield_d != "NLK":
        errors.append(f"040$d 오류: '{subfield_d}' (예상: 'NLK')")
        is_nlk_format = False

    if subfield_e not in ("KORMARC2014", "KORMARC"):
        errors.append(f"040$e 오류: '{subfield_e}' (예상: 'KORMARC2014' 또는 'KORMARC')")
        is_nlk_format = False

    return Field040Analysis(
        exists=True,
        has_subfield_a=bool(subfield_a),
        has_subfield_b=bool(subfield_b),
        has_subfield_c=bool(subfield_c),
        has_subfield_d=bool(subfield_d),
        has_subfield_e=bool(subfield_e),
        subfield_a_value=subfield_a,
        subfield_b_value=subfield_b,
        subfield_c_value=subfield_c,
        subfield_d_value=subfield_d,
        subfield_e_value=subfield_e,
        is_nlk_format=is_nlk_format,
        errors=errors,
    )


def validate_record(
    toon_id: str,
    isbn: str,
    title: str | None,
    kdc_code: str | None,
    pub_year: int | None,
    parsed_data: dict[str, Any],
) -> RecordValidation:
    """
    단일 레코드 검증

    Args:
        toon_id: TOON 식별자
        isbn: ISBN
        title: 제목
        kdc_code: KDC 코드
        pub_year: 발행년
        parsed_data: 파싱된 KORMARC 데이터

    Returns:
        RecordValidation 객체
    """
    errors = []
    warnings = []

    # 필수 필드 확인
    has_001 = bool(get_field_by_tag(parsed_data, "001"))
    has_040 = bool(get_field_by_tag(parsed_data, "040"))
    has_245 = bool(get_field_by_tag(parsed_data, "245"))
    has_260 = bool(get_field_by_tag(parsed_data, "260"))

    # 권장 필드 확인
    has_020 = bool(get_field_by_tag(parsed_data, "020"))
    has_100 = bool(get_field_by_tag(parsed_data, "100"))
    has_650 = bool(get_field_by_tag(parsed_data, "650"))

    # 040 필드 상세 분석
    field_040 = analyze_field_040(parsed_data)

    # 260 필드 $c (발행년) 확인
    has_260_subfield_c = False
    if has_260:
        fields_260 = get_field_by_tag(parsed_data, "260")
        if fields_260:
            field_260 = fields_260[0]
            has_260_subfield_c = bool(get_subfield_value(field_260, "c"))

    # 필수 필드 검증
    if not has_001:
        errors.append("001 필드 (제어번호) 누락")

    if not has_040:
        errors.append("040 필드 (목록작성기관) 누락")
    elif not field_040.is_nlk_format:
        errors.extend(field_040.errors)

    if not has_245:
        errors.append("245 필드 (표제) 누락")

    if not has_260:
        errors.append("260 필드 (발행사항) 누락")
    elif not has_260_subfield_c:
        errors.append("260$c 필드 (발행년) 누락")

    # 권장 필드 검증 (경고)
    if not has_020:
        warnings.append("020 필드 (ISBN) 누락 (권장)")

    if not has_100:
        warnings.append("100 필드 (저자명) 누락 (권장)")

    if not has_650:
        warnings.append("650 필드 (주제명/KDC) 누락 (권장)")

    # 합격 여부 판정
    is_fail = len(errors) > 0
    is_conditional_pass = not is_fail and len(warnings) > 0
    is_pass = not is_fail and len(warnings) == 0

    return RecordValidation(
        toon_id=toon_id,
        isbn=isbn,
        title=title or "(제목 없음)",
        kdc_code=kdc_code,
        pub_year=pub_year,
        has_001=has_001,
        has_040=has_040,
        has_245=has_245,
        has_260=has_260,
        has_020=has_020,
        has_100=has_100,
        has_650=has_650,
        field_040=field_040,
        has_260_subfield_c=has_260_subfield_c,
        is_pass=is_pass,
        is_conditional_pass=is_conditional_pass,
        is_fail=is_fail,
        errors=errors,
        warnings=warnings,
    )


def generate_report(validations: list[RecordValidation], output_path: Path) -> None:
    """
    검증 보고서 생성

    Args:
        validations: 검증 결과 리스트
        output_path: 출력 파일 경로
    """
    total = len(validations)
    passed = sum(1 for v in validations if v.is_pass)
    conditional = sum(1 for v in validations if v.is_conditional_pass)
    failed = sum(1 for v in validations if v.is_fail)

    # 필수 필드 준수율 계산
    has_001 = sum(1 for v in validations if v.has_001)
    has_040 = sum(1 for v in validations if v.has_040)
    has_040_nlk = sum(1 for v in validations if v.field_040.is_nlk_format)
    has_245 = sum(1 for v in validations if v.has_245)
    has_260 = sum(1 for v in validations if v.has_260)
    has_260_c = sum(1 for v in validations if v.has_260_subfield_c)

    # 권장 필드 준수율 계산
    has_020 = sum(1 for v in validations if v.has_020)
    has_100 = sum(1 for v in validations if v.has_100)
    has_650 = sum(1 for v in validations if v.has_650)

    # KDC별 통계
    kdc_stats = defaultdict(lambda: {"total": 0, "pass": 0})
    for v in validations:
        kdc_main = v.kdc_code[0] if v.kdc_code else "X"
        kdc_stats[kdc_main]["total"] += 1
        if v.is_pass or v.is_conditional_pass:
            kdc_stats[kdc_main]["pass"] += 1

    # KDC 분류명 매핑
    KDC_NAMES = {
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
        "X": "미분류",
    }

    # 보고서 작성
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# 노원구립도서관 시방서 준수 검증 보고서 (100개 레코드)\n\n")

        # 1. 검증 개요
        f.write("## 1. 검증 개요\n\n")
        f.write("- **검증 대상**: data/kormarc_prototype_100.db (100 레코드)\n")
        f.write("- **검증 기준**: 노원구립도서관 연간단가계약제안서 (2025년)\n")
        f.write(f"- **검증 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("- **검증 도구**: KORMARC Validation System v1.0\n\n")

        # 2. 시방서 주요 요구사항
        f.write("## 2. 시방서 주요 요구사항\n\n")
        f.write("### 2.1 필수 필드 (제3조)\n\n")
        f.write("| 태그 | 필드명 | 필수여부 | 설명 |\n")
        f.write("|------|--------|----------|------|\n")
        f.write("| 001 | 제어번호 | 필수 | 고유 식별번호 |\n")
        f.write("| 040 | 목록작성기관 | 필수 | NLK 형식 준수 |\n")
        f.write("| 245 | 표제 | 필수 | 도서 제목 |\n")
        f.write("| 260 | 발행사항 | 필수 | 발행자, 발행년 ($c) |\n\n")

        f.write("### 2.2 040 필드 형식 (제2조)\n\n")
        f.write("```\n")
        f.write("040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014\n")
        f.write("```\n\n")
        f.write("**요구사항:**\n")
        f.write("- `$a` = NLK (목록작성기관)\n")
        f.write("- `$b` = kor (목록 언어)\n")
        f.write("- `$c` = (NLK) (전사기관)\n")
        f.write("- `$d` = NLK (수정기관)\n")
        f.write("- `$e` = KORMARC2014 (기술규칙)\n\n")

        f.write("### 2.3 ISBN 입력 규칙\n\n")
        f.write("- ISBN 13자리를 기본으로 사용\n")
        f.write("- 하이픈(-) 제거 후 입력\n\n")

        # 3. 검증 결과 요약
        f.write("## 3. 검증 결과 요약\n\n")
        f.write("### 3.1 전체 통계\n\n")
        f.write(f"- **총 레코드**: {total}개\n")
        f.write(f"- **시방서 준수**: {passed}개 ({passed / total * 100:.1f}%)\n")
        f.write(f"- **부분 준수**: {conditional}개 ({conditional / total * 100:.1f}%)\n")
        f.write(f"- **불합격**: {failed}개 ({failed / total * 100:.1f}%)\n\n")

        f.write("### 3.2 필수 필드 준수율\n\n")
        f.write("| 필드 | 요구사항 | 준수 | 미준수 | 준수율 |\n")
        f.write("|------|----------|------|--------|--------|\n")
        f.write(f"| 001 | 필수 | {has_001} | {total - has_001} | {has_001 / total * 100:.1f}% |\n")
        f.write(f"| 040 | 필수 | {has_040} | {total - has_040} | {has_040 / total * 100:.1f}% |\n")
        f.write(
            f"| 040 (NLK 형식) | 필수 | {has_040_nlk} | {total - has_040_nlk} | {has_040_nlk / total * 100:.1f}% |\n"
        )
        f.write(f"| 245 | 필수 | {has_245} | {total - has_245} | {has_245 / total * 100:.1f}% |\n")
        f.write(f"| 260 | 필수 | {has_260} | {total - has_260} | {has_260 / total * 100:.1f}% |\n")
        f.write(
            f"| 260$c | 필수 | {has_260_c} | {total - has_260_c} | {has_260_c / total * 100:.1f}% |\n\n"
        )

        f.write("### 3.3 권장 필드 준수율\n\n")
        f.write("| 필드 | 요구사항 | 준수 | 미준수 | 준수율 |\n")
        f.write("|------|----------|------|--------|--------|\n")
        f.write(f"| 020 | 권장 | {has_020} | {total - has_020} | {has_020 / total * 100:.1f}% |\n")
        f.write(
            f"| 100 | 조건부 | {has_100} | {total - has_100} | {has_100 / total * 100:.1f}% |\n"
        )
        f.write(
            f"| 650 | 권장 | {has_650} | {total - has_650} | {has_650 / total * 100:.1f}% |\n\n"
        )

        # 4. KDC별 준수 현황
        f.write("## 4. KDC별 준수 현황\n\n")
        f.write("| KDC | 분류명 | 레코드 수 | 준수 | 준수율 |\n")
        f.write("|-----|--------|-----------|------|--------|\n")

        for kdc_main in sorted(kdc_stats.keys()):
            stats = kdc_stats[kdc_main]
            kdc_name = KDC_NAMES.get(kdc_main, "알 수 없음")
            compliance_rate = stats["pass"] / stats["total"] * 100
            f.write(
                f"| {kdc_main} | {kdc_name} | {stats['total']} | {stats['pass']} | {compliance_rate:.1f}% |\n"
            )

        f.write("\n")

        # 5. 불합격 레코드 상세
        f.write("## 5. 불합격 레코드 상세\n\n")
        f.write("### 5.1 심각한 오류 (재작업 필요)\n\n")

        failed_records = [v for v in validations if v.is_fail]
        if failed_records:
            for i, record in enumerate(failed_records[:20], 1):  # 최대 20개만 표시
                f.write(f"#### 레코드 #{i} (TOON: {record.toon_id})\n\n")
                f.write(f"- **ISBN**: {record.isbn}\n")
                f.write(f"- **제목**: {record.title}\n")
                f.write(f"- **KDC**: {record.kdc_code or '미분류'}\n")
                f.write("- **오류**:\n")
                for error in record.errors:
                    f.write(f"  - ❌ {error}\n")
                f.write("- **조치**: 재작업 필요\n\n")

            if len(failed_records) > 20:
                f.write(f"\n*(총 {len(failed_records)}개 불합격 레코드 중 20개만 표시)*\n\n")
        else:
            f.write("✅ 심각한 오류가 있는 레코드가 없습니다.\n\n")

        f.write("### 5.2 경고 (개선 권장)\n\n")

        conditional_records = [v for v in validations if v.is_conditional_pass]
        if conditional_records:
            for i, record in enumerate(conditional_records[:10], 1):  # 최대 10개만 표시
                f.write(f"#### 레코드 #{i} (TOON: {record.toon_id})\n\n")
                f.write(f"- **ISBN**: {record.isbn}\n")
                f.write(f"- **제목**: {record.title}\n")
                f.write(f"- **KDC**: {record.kdc_code or '미분류'}\n")
                f.write("- **경고**:\n")
                for warning in record.warnings:
                    f.write(f"  - ⚠️ {warning}\n")
                f.write("- **조치**: 개선 권장 (합격 가능)\n\n")

            if len(conditional_records) > 10:
                f.write(
                    f"\n*(총 {len(conditional_records)}개 조건부합격 레코드 중 10개만 표시)*\n\n"
                )
        else:
            f.write("✅ 경고가 있는 레코드가 없습니다.\n\n")

        # 6. 개선 권장사항
        f.write("## 6. 개선 권장사항\n\n")
        f.write("### 6.1 즉시 수정 필요 (불합격)\n\n")

        missing_260c = sum(1 for v in validations if v.has_260 and not v.has_260_subfield_c)
        missing_040_nlk = sum(1 for v in validations if v.has_040 and not v.field_040.is_nlk_format)

        f.write(f"1. **260 필드 $c (발행년) 추가**: {missing_260c}건\n")
        f.write(f"2. **040 필드 형식 수정 (NLK 형식)**: {missing_040_nlk}건\n\n")

        f.write("### 6.2 품질 개선 권장\n\n")
        missing_100 = sum(1 for v in validations if not v.has_100)
        missing_650 = sum(1 for v in validations if not v.has_650)

        f.write(f"1. **저자명(100) 추가**: {missing_100}건\n")
        f.write(f"2. **KDC 주제명(650) 추가**: {missing_650}건\n\n")

        # 7. 검증 방법론
        f.write("## 7. 검증 방법론\n\n")
        f.write("### 7.1 사용된 검증기\n\n")
        f.write("- **StructureValidator**: KORMARC 구조 검증\n")
        f.write("- **SemanticValidator**: 필수 필드 의미론 검증\n")
        f.write("- **NowonValidator**: 노원구 시방서 준수 검증\n\n")

        f.write("### 7.2 검증 프로세스\n\n")
        f.write("1. **1단계**: 필수 필드 존재 여부 확인 (001, 040, 245, 260)\n")
        f.write("2. **2단계**: 040 필드 NLK 형식 준수 검증\n")
        f.write("3. **3단계**: 260$c (발행년) 존재 여부 확인\n")
        f.write("4. **4단계**: 권장 필드 존재 여부 확인 (020, 100, 650)\n")
        f.write("5. **5단계**: 합격/조건부합격/불합격 판정\n\n")

        # 8. 결론
        f.write("## 8. 결론\n\n")
        f.write("### 8.1 납품 가능 여부\n\n")
        f.write(f"- **즉시 납품 가능**: {passed + conditional}개 (합격 + 조건부합격)\n")
        f.write(f"- **재작업 필요**: {failed}개 (불합격)\n\n")

        f.write("### 8.2 종합 평가\n\n")

        compliance_rate = (passed + conditional) / total * 100
        if compliance_rate >= 95:
            grade = "우수"
            comment = "대부분의 레코드가 시방서를 준수하고 있습니다."
        elif compliance_rate >= 85:
            grade = "양호"
            comment = "일부 개선이 필요하지만 전반적으로 양호한 상태입니다."
        elif compliance_rate >= 70:
            grade = "보통"
            comment = "상당수의 레코드가 재작업이 필요한 상태입니다."
        else:
            grade = "미흡"
            comment = "다수의 레코드가 시방서를 준수하지 않고 있어 전면적인 재작업이 필요합니다."

        f.write(f"**종합 등급**: {grade} ({compliance_rate:.1f}% 준수)\n\n")
        f.write(f"{comment}\n\n")

        # 부록
        f.write("## 부록\n\n")
        f.write("### A. 검증 대상 레코드 목록 (100개)\n\n")
        f.write("| 번호 | TOON ID | ISBN | 제목 | KDC | 검증 결과 |\n")
        f.write("|------|---------|------|------|-----|----------|\n")

        for i, v in enumerate(validations, 1):
            title_short = v.title[:40] + "..." if len(v.title) > 40 else v.title
            kdc_display = v.kdc_code or "미분류"
            f.write(
                f"| {i} | {v.toon_id} | {v.isbn} | {title_short} | {kdc_display} | {v.status} |\n"
            )

        f.write("\n")

        f.write("### B. 시방서 체크리스트\n\n")
        f.write("- [ ] 001 필드 (제어번호) 존재\n")
        f.write("- [ ] 040 필드 (목록작성기관) 존재\n")
        f.write("- [ ] 040$a = NLK\n")
        f.write("- [ ] 040$b = kor\n")
        f.write("- [ ] 040$c = (NLK)\n")
        f.write("- [ ] 040$d = NLK\n")
        f.write("- [ ] 040$e = KORMARC2014\n")
        f.write("- [ ] 245 필드 (표제) 존재\n")
        f.write("- [ ] 260 필드 (발행사항) 존재\n")
        f.write("- [ ] 260$c (발행년) 존재\n")
        f.write("- [ ] 020 필드 (ISBN) 존재 (권장)\n")
        f.write("- [ ] 100 필드 (저자명) 존재 (권장)\n")
        f.write("- [ ] 650 필드 (주제명/KDC) 존재 (권장)\n\n")

        f.write("### C. 재작업 가이드\n\n")
        f.write("#### 040 필드 형식 수정\n\n")
        f.write("**기존 (오류)**:\n")
        f.write("```\n")
        f.write("040   ##$aKEKPIA$bkor$eKORMARC\n")
        f.write("```\n\n")
        f.write("**수정 (올바른 형식)**:\n")
        f.write("```\n")
        f.write("040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014\n")
        f.write("```\n\n")

        f.write("#### 260$c 발행년 추가\n\n")
        f.write("**기존 (오류)**:\n")
        f.write("```\n")
        f.write("260   ##$a서울$b동아출판사\n")
        f.write("```\n\n")
        f.write("**수정 (올바른 형식)**:\n")
        f.write("```\n")
        f.write("260   ##$a서울$b동아출판사$c2024\n")
        f.write("```\n\n")

        f.write("---\n\n")
        f.write("**보고서 생성일**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write("**검증 스크립트**: scripts/validate_nowon_compliance.py\n")
        f.write("**생성 도구**: KORMARC Validation System v1.0\n")


def main():
    """메인 함수"""
    # 데이터베이스 경로
    db_path = Path(__file__).parent.parent / "data" / "kormarc_prototype_100.db"
    if not db_path.exists():
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return

    # 출력 경로
    output_path = (
        Path(__file__).parent.parent / "docs" / "NOWON_COMPLIANCE_VALIDATION_REPORT_100.md"
    )

    print(f"✅ 데이터베이스: {db_path}")
    print(f"✅ 출력 경로: {output_path}")
    print()

    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 레코드 조회
    cursor.execute(
        """
        SELECT toon_id, isbn, title, kdc_code, pub_year, parsed_data
        FROM kormarc_records
        ORDER BY toon_id
    """
    )

    rows = cursor.fetchall()
    total_count = len(rows)

    print(f"📊 총 레코드: {total_count}개")
    print()

    # 검증 실행
    validations = []
    for i, (toon_id, isbn, title, kdc_code, pub_year, parsed_data_json) in enumerate(rows, 1):
        parsed_data = json.loads(parsed_data_json)
        validation = validate_record(toon_id, isbn, title, kdc_code, pub_year, parsed_data)
        validations.append(validation)

        # 진행 상황 출력
        if i % 10 == 0 or i == total_count:
            print(f"  검증 진행: {i}/{total_count} ({i / total_count * 100:.1f}%)")

    conn.close()

    print()
    print("📝 보고서 생성 중...")

    # 보고서 생성
    generate_report(validations, output_path)

    print(f"✅ 보고서 생성 완료: {output_path}")
    print()

    # 요약 통계 출력
    passed = sum(1 for v in validations if v.is_pass)
    conditional = sum(1 for v in validations if v.is_conditional_pass)
    failed = sum(1 for v in validations if v.is_fail)

    print("=" * 60)
    print("📊 검증 결과 요약")
    print("=" * 60)
    print(f"총 레코드: {total_count}개")
    print(f"  - 합격: {passed}개 ({passed / total_count * 100:.1f}%)")
    print(f"  - 조건부합격: {conditional}개 ({conditional / total_count * 100:.1f}%)")
    print(f"  - 불합격: {failed}개 ({failed / total_count * 100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
