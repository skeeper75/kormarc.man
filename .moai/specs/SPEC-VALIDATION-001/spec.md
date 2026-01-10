# SPEC-VALIDATION-001: KORMARC Parser 종합 검증 시스템

---
spec_id: VALIDATION-001
title: KORMARC Parser 종합 검증 시스템
version: 1.0.0
status: Planned
priority: HIGH
created: 2026-01-10
author: 지니 (skeeper75)
---

## HISTORY

| 버전 | 날짜 | 작성자 | 변경사항 |
|------|------|--------|----------|
| 1.0.0 | 2026-01-10 | 지니 | 초기 SPEC 작성 - 5단계 검증 프레임워크 설계 |

---

## 1. 개요

### 1.1 목적
KORMARC 2014 표준 및 Nowon 사양에 완벽하게 준수하는 종합 검증 시스템을 구축하여, 수집된 100개의 KORMARC 레코드 및 향후 레코드의 품질을 자동으로 검증한다.

### 1.2 범위
- 5단계 검증 계층: 구조 검증, 데이터 무결성, 의미 검증, 표준 준수, 교차 검증
- 100개 수집 레코드 일괄 검증 및 보고서 생성
- Nowon 사양 통합 (`docs/NOWON_KORMARC_RULES.md` 기준)
- 상세한 오류 메시지 및 필드 위치 추적

### 1.3 프로젝트 컨텍스트
- 데이터: `data/kormarc_prototype_100.db`에 100개 KORMARC 레코드 수집 완료
- 기존 검증기: `src/kormarc/validators.py` (ISBN, KDC 검증기 존재)
- Nowon 사양: `docs/NOWON_KORMARC_RULES.md`
- 파서 구현: `src/kormarc/parser/kormarc_parser.py`
- 현재 테스트 커버리지: 46.11%
- 목표: 프로덕션 수준 검증 프레임워크

---

## 2. EARS 요구사항 명세

### 2.1 항상성 요구사항 (Ubiquitous Requirements)

시스템은 **항상** 다음 요구사항을 충족해야 한다:

- **REQ-U-001**: 시스템은 **항상** KORMARC 2014 표준에 대한 모든 레코드 검증을 수행해야 한다
  - 검증 범위: Leader, Directory, Fields (Control/Data)
  - 표준 준거: KORMARC 2014 공식 문서
  - 추적성: TRUST-5 Trackable 원칙

- **REQ-U-002**: 시스템은 **항상** 040 필드 형식을 Nowon 사양에 따라 검증해야 한다
  - 필수 형식: `040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014`
  - 필수 서브필드: $a, $b, $c, $d, $e
  - 고정값 검증: $a=NLK, $b=kor, $c=(NLK), $d=NLK, $e=KORMARC2014

- **REQ-U-003**: 시스템은 **항상** 일괄 검증 모드를 지원해야 한다
  - 입력: 여러 레코드 동시 처리
  - 출력: 통합 검증 보고서
  - 성능: 100개 레코드 5분 이내 처리

- **REQ-U-004**: 시스템은 **항상** 필수 필드 존재 여부를 확인해야 한다
  - 필수 필드: 001 (제어번호), 040 (목록작성기관), 245 (표제), 260 (발행사항)
  - 권장 필드: 020 (ISBN), 650 (주제명)
  - 조건부 필수: 100 (저자명, 단행본인 경우), 300 (형태사항, 물리자료)

### 2.2 이벤트 기반 요구사항 (Event-Driven Requirements)

**WHEN** 특정 이벤트 발생 **THEN** 시스템 동작:

- **REQ-E-001**: **WHEN** 사용자가 KORMARC 레코드 검증 요청 **THEN** 5단계 검증 계층 전체를 순차적으로 실행해야 한다
  - 검증 순서: 구조 → 데이터 무결성 → 의미 → 표준 준수 → 교차 검증
  - 단계별 독립성: 각 단계 실패 시에도 다음 단계 계속 실행
  - 중단 조건: 구조 검증 실패 시 의미 검증 건너뛰기 가능

- **REQ-E-002**: **WHEN** 검증 완료 **THEN** 상세 검증 보고서를 생성해야 한다
  - 포함 내용: 검증 결과 (성공/실패), 오류 목록, 경고 메시지, 통계 요약
  - 출력 형식: Markdown, JSON (구조화된 데이터)
  - 저장 위치: `data/validation_reports/`

- **REQ-E-003**: **WHEN** 검증 실패 **THEN** 특정 필드 위치를 포함한 오류 메시지를 제공해야 한다
  - 오류 메시지 형식: `[필드 태그] [위치] 오류 내용: 상세 설명`
  - 예시: `[040] 서브필드 $e 오류: 'KORMARC2014' 필요, 'KORMARC2' 발견`
  - 수정 제안: 올바른 형식 예시 제공

- **REQ-E-004**: **WHEN** pymarc 파싱 실패 **THEN** 비표준 플래그를 설정하고 호환성 경고를 출력해야 한다
  - 경고 메시지: "pymarc 파싱 실패: 비표준 MARC 형식 감지"
  - 대체 검증: 내부 검증기로 fallback 수행
  - 로그 기록: 파싱 실패 원인 상세 기록

### 2.3 상태 기반 요구사항 (State-Driven Requirements)

**IF** 특정 조건 **THEN** 시스템 동작:

- **REQ-S-001**: **IF** 레코드가 모든 검증 통과 **THEN** "valid" 상태로 표시하고 데이터베이스에 저장해야 한다
  - 검증 상태 필드: `validation_status = "valid"`
  - 타임스탬프: `validated_at = 현재 시각`
  - 메타데이터: 검증 버전 정보 포함

- **REQ-S-002**: **IF** 레코드가 하나 이상의 검증 실패 **THEN** "invalid" 상태로 표시하고 상세 오류 로그를 기록해야 한다
  - 검증 상태 필드: `validation_status = "invalid"`
  - 오류 로그: `validation_errors` JSON 필드에 저장
  - 심각도 분류: ERROR (치명적), WARNING (경고), INFO (정보)

- **REQ-S-003**: **IF** pymarc 파싱 실패 **THEN** "non-standard" 플래그를 설정하고 호환성 경고를 기록해야 한다
  - 검증 상태 필드: `validation_status = "non-standard"`
  - 경고 내용: pymarc 호환성 문제 상세 기록
  - 재검증 추천: 수동 검토 권장

### 2.4 선택적 요구사항 (Optional Requirements)

**가능하면** 다음 기능을 제공한다:

- **REQ-O-001**: **가능하면** 추가 외부 MARC 검증기 통합을 제공한다
  - 후보 검증기: Library of Congress MARC Validator
  - 통합 방식: 플러그인 아키텍처
  - 설정 가능: 사용자가 검증기 선택 가능

- **REQ-O-002**: **가능하면** HTML 형식 검증 보고서 생성을 제공한다
  - 보고서 형식: 시각화된 통계 차트 포함
  - 내보내기: PDF 변환 지원
  - 접근성: WCAG 2.1 AA 준수

- **REQ-O-003**: **가능하면** 사용자 정의 검증 규칙 지원을 제공한다
  - 설정 파일: YAML 형식 규칙 정의
  - 플러그인: 커스텀 검증기 추가 가능
  - 우선순위: 기본 규칙과 사용자 규칙 병합

### 2.5 복합 요구사항 (Complex Requirements - Unwanted Behavior)

시스템은 다음 동작을 **하지 않아야 한다**:

- **REQ-C-001**: 시스템은 필수 필드(001, 040, 245, 260) 누락 레코드를 **허용하지 않아야 한다**
  - 거부 조건: 필수 필드 하나라도 누락 시 즉시 실패
  - 오류 메시지: "필수 필드 [태그] 누락" 명시
  - 처리 방침: 검증 실패로 처리, 데이터베이스 저장 금지

- **REQ-C-002**: 시스템은 검증 실패를 **자동으로 무시하지 않아야 한다**
  - 명시적 기록: 모든 실패 항목 로그 기록
  - 사용자 알림: 검증 실패 시 콘솔 출력
  - 보고서 포함: 실패 건수 통계 제공

- **REQ-C-003**: **UNLESS** 사용자가 명시적으로 검증 비활성화 **THEN** 모든 검증 규칙을 강제 적용해야 한다
  - 기본 설정: 모든 검증 활성화
  - 비활성화 방법: CLI 플래그 `--skip-validation` 또는 설정 파일
  - 경고 메시지: 검증 비활성화 시 위험 경고 출력

---

## 3. 아키텍처 설계

### 3.1 검증 계층 아키텍처

```
┌─────────────────────────────────────────────────────┐
│              Validation Orchestrator                │
│         (validates_100_records.py)                  │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Tier 1      │ │  Tier 2      │ │  Tier 3      │
│  구조 검증    │ │ 데이터 무결성 │ │  의미 검증    │
│              │ │              │ │              │
│ structure_   │ │ data_        │ │ semantic_    │
│ validator.py │ │ validator.py │ │ validator.py │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Tier 4      │ │  Tier 5      │ │  Reporter    │
│  표준 준수    │ │  교차 검증    │ │  보고서 생성  │
│              │ │              │ │              │
│ standard_    │ │ cross_       │ │ report_      │
│ validator.py │ │ validator.py │ │ generator.py │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 3.2 검증 단계 상세

**Tier 1 - 구조 검증 (Structure Validation)**:
- Leader 검증: 24자 고정 길이, 각 위치별 값 범위
- Directory 검증: 12자 단위 엔트리, 필드 태그/길이/시작위치
- Fields 검증: 필드 구분자, 서브필드 구분자, 레코드 종결자

**Tier 2 - 데이터 무결성 (Data Integrity)**:
- 필수 필드 존재 확인 (001, 040, 245, 260)
- 필드 길이 제한 검증
- 반복 불가 필드 중복 검사
- 지시기호 유효성 검증 (0-9, #)

**Tier 3 - 의미 검증 (Semantic Validation)**:
- 필드 간 관계 검증 (예: 100 + 245 조합)
- 040 필드 Nowon 형식 준수 (`$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014`)
- ISBN 체크섬 검증 (020 필드)
- KDC 형식 검증 (082 필드)

**Tier 4 - 표준 준수 (Standard Compliance)**:
- KORMARC 2014 표준 준수 확인
- pymarc 파싱 테스트
- 필드별 서브필드 규칙 검증

**Tier 5 - 교차 검증 (Cross Validation)**:
- Record ↔ XML 라운드트립 변환 테스트
- pymarc 객체 일관성 검증
- 외부 검증기 결과 비교 (선택적)

### 3.3 데이터베이스 스키마 확장

```sql
-- validation_results 테이블 추가
CREATE TABLE validation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    validation_status TEXT CHECK(validation_status IN ('valid', 'invalid', 'non-standard')),
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_version TEXT,  -- 검증기 버전
    errors JSON,              -- 오류 목록 (배열)
    warnings JSON,            -- 경고 목록 (배열)
    tier1_passed BOOLEAN,
    tier2_passed BOOLEAN,
    tier3_passed BOOLEAN,
    tier4_passed BOOLEAN,
    tier5_passed BOOLEAN,
    FOREIGN KEY (record_id) REFERENCES kormarc_records(id)
);
```

---

## 4. 기술 스택

### 4.1 핵심 라이브러리
- **Python 3.12+**: 최신 파이썬 버전
- **Pydantic 2.9+**: 데이터 검증 모델
- **pymarc 5.2+**: MARC21 라이브러리 (교차 검증용)
- **pytest 8.0+**: 테스트 프레임워크
- **SQLite3**: 데이터베이스 (내장)

### 4.2 선택적 라이브러리
- **Rich 13.0+**: 프로그레스 바 및 콘솔 출력 (선택)
- **Jinja2 3.1+**: HTML 보고서 템플릿 (선택)
- **pdfkit**: PDF 변환 (선택)

### 4.3 개발 도구
- **ruff**: 린터 및 포매터
- **mypy**: 타입 체킹
- **coverage.py**: 테스트 커버리지

---

## 5. Nowon 사양 통합

### 5.1 040 필드 검증 규칙

**필수 형식**:
```
040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014
```

**검증 로직**:
```python
def validate_040_field(field_040: str) -> ValidationResult:
    """
    040 필드 Nowon 사양 검증

    필수 서브필드: $a, $b, $c, $d, $e
    고정값:
        $a = NLK
        $b = kor
        $c = (NLK)
        $d = NLK
        $e = KORMARC2014
    """
    required_subfields = {'a': 'NLK', 'b': 'kor', 'c': '(NLK)', 'd': 'NLK', 'e': 'KORMARC2014'}

    for code, expected_value in required_subfields.items():
        actual_value = extract_subfield(field_040, code)
        if actual_value != expected_value:
            return ValidationResult(
                passed=False,
                error=f"040 필드 ${code} 오류: '{expected_value}' 필요, '{actual_value}' 발견"
            )

    return ValidationResult(passed=True)
```

### 5.2 ISBN 검증 규칙

**형식**:
```
020   ##$a9791162233149
```

**검증 규칙**:
- 13자리 선호 (ISBN-13)
- 하이픈 제거 후 검증
- 체크섬 알고리즘 검증

```python
def validate_isbn(isbn: str) -> bool:
    """ISBN-13 체크섬 검증"""
    isbn_clean = isbn.replace('-', '').replace(' ', '')
    if len(isbn_clean) != 13:
        return False

    checksum = sum((3 if i % 2 else 1) * int(d) for i, d in enumerate(isbn_clean[:-1]))
    return (10 - (checksum % 10)) % 10 == int(isbn_clean[-1])
```

### 5.3 필수 필드 체크리스트

| 필드 | 태그 | 필수 여부 | 설명 |
|------|------|-----------|------|
| 제어번호 | 001 | 필수 | 레코드 고유 식별자 |
| 목록작성기관 | 040 | 필수 | Nowon 형식 준수 |
| ISBN | 020 | 권장 | 13자리 체크섬 검증 |
| 저자명 | 100 | 조건부 | 단행본인 경우 필수 |
| 표제 | 245 | 필수 | 본표제 필수 |
| 발행사항 | 260 | 필수 | 발행지, 발행처, 발행년 |
| 형태사항 | 300 | 조건부 | 물리자료인 경우 필수 |
| 주제명 | 650 | 권장 | KDC 또는 NDC |

---

## 6. 리스크 관리

### 6.1 리스크 식별

**리스크 1: pymarc 라이브러리 KORMARC 비호환**
- 확률: 중간
- 영향: 높음
- 완화 방안: 샘플 레코드로 사전 테스트, 내부 검증기로 fallback

**리스크 2: 대량 일괄 처리 성능 저하**
- 확률: 낮음
- 영향: 중간
- 완화 방안: 배치 처리, 프로그레스 바 추적, 병렬 처리 (선택)

**리스크 3: 검증 오탐 (False Positive)**
- 확률: 중간
- 영향: 높음
- 완화 방안: 플래그된 레코드 수동 샘플 검토, 검증 규칙 정밀 조정

### 6.2 품질 게이트

**검증 성공 기준**:
- 구조 검증: 100% 통과율
- 데이터 무결성: 95% 이상 통과율
- Nowon 준수: 100% 통과율 (040 필드)
- pymarc 교차 검증: 95% 이상 파싱 성공률

**테스트 커버리지 목표**:
- 현재: 46.11%
- 목표: 85% 이상
- TRUST-5 Test-first 원칙 준수

---

## 7. 구현 전략

### 7.1 개발 우선순위

**우선순위 1 (High)**:
- Tier 1 구조 검증 구현
- Tier 2 데이터 무결성 검증
- Tier 3 Nowon 040 필드 검증
- 100개 레코드 일괄 검증 스크립트

**우선순위 2 (Medium)**:
- Tier 4 표준 준수 검증 (pymarc 통합)
- Tier 5 교차 검증 (라운드트립 테스트)
- Markdown/JSON 보고서 생성

**우선순위 3 (Low)**:
- HTML 보고서 생성 (선택)
- 외부 검증기 통합 (선택)
- 사용자 정의 규칙 지원 (선택)

### 7.2 개발 단계

**Phase 1: 핵심 검증 구현 (1-2주)**
- `src/kormarc/validators/structure_validator.py` 생성
- `src/kormarc/validators/nowon_validator.py` 생성
- `scripts/validate_100_records.py` 생성
- 20개 샘플 레코드로 테스트

**Phase 2: 의미 검증 (1주)**
- `src/kormarc/validators/semantic_validator.py` 생성
- 040 필드 형식 검증기
- 필수 필드 존재 확인
- 필드 간 관계 검증

**Phase 3: 표준 준수 및 교차 검증 (1주)**
- pymarc 라이브러리 통합
- `src/kormarc/validators/cross_validator.py` 생성
- 라운드트립 변환 테스트 (Record ↔ XML)
- `src/kormarc/validators/standard_validator.py` 생성

**Phase 4: 보고서 및 문서화 (3-5일)**
- 검증 보고서 생성기 생성
- 100개 레코드 전체 검증
- 종합 검증 보고서 생성
- 발견사항 및 권장사항 문서화

---

## 8. 추적성 태그

**TAG**: `[SPEC-VALIDATION-001]`
**TRUST-5 연계**:
- Test-first: pytest 기반 TDD 개발
- Readable: 명확한 검증 오류 메시지
- Unified: 일관된 검증 규칙 적용
- Secured: 데이터 무결성 보장
- Trackable: 검증 결과 데이터베이스 기록

**관련 문서**:
- `docs/NOWON_KORMARC_RULES.md`: Nowon 사양 문서
- `src/kormarc/validators.py`: 기존 검증기
- `tests/test_kormarc_builder.py`: 기존 테스트 사례

---

## 9. 참고 자료

### 9.1 표준 문서
- KORMARC 2014 통합서지용 매뉴얼
- MARC21 Format for Bibliographic Data
- ISO 2709: Information and documentation

### 9.2 라이브러리 문서
- pymarc Documentation: https://pymarc.readthedocs.io/
- Pydantic Validation: https://docs.pydantic.dev/

### 9.3 프로젝트 문서
- Nowon KORMARC 규칙: `docs/NOWON_KORMARC_RULES.md`
- 사용법 가이드: `docs/USAGE.md`
- TOON SPEC: `docs/TOON_SPEC.md`

---

**문서 버전**: 1.0.0
**최종 수정**: 2026-01-10
**승인 상태**: 계획됨 (Planned)
**다음 단계**: `/moai:2-run SPEC-VALIDATION-001` 실행하여 TDD 구현 시작
