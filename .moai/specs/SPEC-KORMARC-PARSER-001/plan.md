# Implementation Plan: SPEC-KORMARC-PARSER-001

## SPEC Reference

- **SPEC ID**: SPEC-KORMARC-PARSER-001
- **Title**: KORMARC Parser Library
- **Priority**: High

---

## Implementation Strategy

### Technical Approach

KORMARC 파서 라이브러리는 다음 원칙에 따라 구현됩니다:

1. **Pydantic v2 중심 설계**: 모든 데이터 모델은 Pydantic BaseModel을 상속하여 자동 유효성 검증 및 직렬화를 지원합니다.

2. **레이어드 아키텍처**: Parser, Validator, Converter를 분리하여 단일 책임 원칙을 준수합니다.

3. **TDD 기반 개발**: 모든 기능은 테스트를 먼저 작성한 후 구현합니다.

4. **점진적 기능 추가**: Core 파싱 기능부터 시작하여 변환, 검증, 스트리밍 순으로 확장합니다.

### Architecture Design

```
kormarc/
├── __init__.py           # Public API exports
├── models/
│   ├── __init__.py
│   ├── leader.py         # Leader 모델
│   ├── fields.py         # Field 모델들
│   └── record.py         # Record 모델
├── parser/
│   ├── __init__.py
│   ├── kormarc_parser.py # KORMARC 파서
│   └── marc21_parser.py  # MARC21 파서
├── converter/
│   ├── __init__.py
│   ├── json_converter.py # JSON 변환
│   └── xml_converter.py  # XML 변환
├── validator/
│   ├── __init__.py
│   └── validators.py     # 유효성 검증 로직
├── exceptions.py         # 커스텀 예외
└── constants.py          # 상수 정의

tests/
├── conftest.py           # pytest fixtures
├── test_models/
│   ├── test_leader.py
│   ├── test_fields.py
│   └── test_record.py
├── test_parser/
│   ├── test_kormarc_parser.py
│   └── test_marc21_parser.py
├── test_converter/
│   ├── test_json_converter.py
│   └── test_xml_converter.py
└── fixtures/
    └── sample_records/   # 테스트용 KORMARC 샘플
```

---

## Milestones

### Primary Goal: Core Parsing Infrastructure

**Focus**: 기본 KORMARC 레코드 파싱 및 데이터 모델 구현

**Deliverables**:
- Leader 파싱 및 모델 구현
- ControlField, DataField, Subfield 모델 구현
- Record 모델 구현
- 기본 KORMARCParser 클래스 구현
- 단위 테스트 작성 (목표: 90% 커버리지)

**Requirements Covered**:
- REQ-U-001, REQ-U-002, REQ-U-003
- REQ-E-001, REQ-E-005
- REQ-S-001, REQ-S-002
- REQ-N-002

**Success Criteria**:
- 샘플 KORMARC 레코드 파싱 성공
- 모든 필드 타입 정확한 추출
- Pydantic 유효성 검증 동작 확인

---

### Secondary Goal: Format Conversion

**Focus**: JSON/XML 변환 기능 구현

**Deliverables**:
- JSON 직렬화/역직렬화 구현
- MARCXML 형식 변환 구현
- MARC21 호환 변환 구현
- 변환 테스트 작성

**Requirements Covered**:
- REQ-E-002, REQ-E-003, REQ-E-004
- REQ-N-001

**Dependencies**:
- Primary Goal 완료 필요

**Success Criteria**:
- Record to JSON 양방향 변환 성공
- MARCXML 형식 출력 표준 준수
- MARC21 형식과의 호환성 검증

---

### Tertiary Goal: Validation & Error Handling

**Focus**: 강화된 유효성 검증 및 오류 처리

**Deliverables**:
- 커스텀 예외 클래스 체계 구현
- 상세 오류 메시지 및 위치 정보 제공
- 필드별 유효성 검증 규칙 구현
- 검증 결과 리포트 기능

**Requirements Covered**:
- REQ-U-002
- REQ-E-005
- REQ-N-001, REQ-N-003

**Dependencies**:
- Primary Goal 완료 필요

**Success Criteria**:
- 모든 오류 케이스에 대한 명확한 예외 발생
- 오류 위치(행, 열) 정보 제공
- 유효성 검증 리포트 생성

---

### Optional Goal: Advanced Features

**Focus**: 성능 최적화 및 부가 기능

**Deliverables**:
- 스트리밍 파싱 지원 (대용량 파일)
- 비동기 파일 읽기 지원
- CLI 도구 구현
- 레코드 비교/병합 기능

**Requirements Covered**:
- REQ-S-003
- REQ-O-001, REQ-O-002, REQ-O-003

**Dependencies**:
- Secondary Goal 완료 필요

**Success Criteria**:
- 1GB 이상 파일 메모리 효율적 처리
- CLI로 기본 변환 작업 수행 가능

---

## Technical Decisions

### Pydantic v2 Configuration

```python
from pydantic import BaseModel, ConfigDict

class BaseKORMARCModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )
```

**Rationale**:
- `strict=True`: 타입 강제로 안정성 확보
- `frozen=True`: 불변 객체로 데이터 무결성 보장
- `extra="forbid"`: 예상치 못한 필드 방지

### Parser Design Pattern

**Strategy Pattern** 적용:
- `ParserStrategy` 추상 클래스 정의
- `KORMARCParserStrategy`, `MARC21ParserStrategy` 구현
- 런타임에 파서 전략 선택 가능

**Rationale**:
- MARC21 등 다른 형식 지원 확장성
- 테스트 용이성 (Mock 파서 주입 가능)

### Error Handling Strategy

**Exception Hierarchy**:
```
KORMARCError
├── ParseError
│   ├── LeaderParseError
│   ├── FieldParseError
│   └── SubfieldParseError
├── ValidationError
│   ├── LeaderValidationError
│   └── FieldValidationError
├── ConversionError
│   ├── JSONConversionError
│   └── XMLConversionError
└── EncodingError
```

**Rationale**:
- 세분화된 예외로 정확한 오류 위치 파악
- 사용자가 특정 오류 유형만 catch 가능

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| KORMARC 표준 문서 불완전성 | Medium | High | 실제 레코드 샘플 확보 및 역공학 |
| 레거시 인코딩(EUC-KR) 처리 | Medium | Medium | chardet 라이브러리로 인코딩 자동 감지 |
| 대용량 파일 메모리 이슈 | Low | High | 스트리밍 파서 구현 (Optional Goal) |

### Dependency Risks

| Dependency | Risk | Mitigation |
|------------|------|------------|
| Pydantic v2 | Low | 안정 버전 사용, 버전 고정 |
| lxml | Low | 표준 라이브러리 xml.etree로 폴백 가능 |

---

## Quality Gates

### Pre-Implementation Checklist

- [ ] 프로젝트 구조 생성
- [ ] pyproject.toml 설정 완료
- [ ] 개발 환경 구성 (poetry/uv)
- [ ] pre-commit hooks 설정
- [ ] CI/CD 파이프라인 구성

### Post-Implementation Checklist

- [ ] 테스트 커버리지 85% 이상
- [ ] 모든 린터 경고 해결 (ruff)
- [ ] 타입 체크 통과 (mypy)
- [ ] API 문서화 완료
- [ ] CHANGELOG 업데이트

---

## Traceability

- **Source SPEC**: `/mnt/d/dev/kormarc.man/.moai/specs/SPEC-KORMARC-PARSER-001/spec.md`
- **Acceptance Criteria**: `/mnt/d/dev/kormarc.man/.moai/specs/SPEC-KORMARC-PARSER-001/acceptance.md`
