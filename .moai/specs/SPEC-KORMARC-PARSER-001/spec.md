# SPEC-KORMARC-PARSER-001: KORMARC Parser Library

## Metadata

| Field | Value |
|-------|-------|
| SPEC ID | SPEC-KORMARC-PARSER-001 |
| Title | KORMARC Parser Library |
| Created | 2026-01-10 |
| Status | Planned |
| Priority | High |
| Lifecycle | spec-anchored |

---

## Environment

### Technology Stack

- **Language**: Python 3.12+
- **Data Validation**: Pydantic v2.9+
- **Testing**: pytest 8.0+, pytest-asyncio
- **Code Quality**: ruff, black, mypy
- **Package Management**: poetry 또는 uv

### Dependencies

- pydantic >= 2.9.0: 데이터 모델 및 검증
- lxml >= 5.0.0: XML 파싱 (선택적)
- pytest >= 8.0.0: 테스트 프레임워크
- pytest-cov >= 4.0.0: 테스트 커버리지

### Constraints

- KORMARC 표준 준수 (한국문헌자동화목록형식)
- MARC21 호환성 유지
- 메모리 효율적인 대용량 레코드 처리 지원
- 최소 85% 테스트 커버리지 유지

---

## Assumptions

### Technical Assumptions

| Assumption | Confidence | Evidence | Risk if Wrong | Validation Method |
|------------|------------|----------|---------------|-------------------|
| KORMARC 레코드는 ISO 2709 형식을 기반으로 함 | High | KORMARC 표준 문서 | 파서 로직 전면 수정 필요 | 표준 문서 검토 |
| UTF-8 인코딩이 기본 문자 인코딩임 | Medium | 최신 KORMARC 구현 사례 | EUC-KR 등 레거시 인코딩 지원 추가 필요 | 실제 KORMARC 파일 샘플 분석 |
| 필드 태그는 3자리 숫자 형식임 | High | MARC 표준 | 태그 파싱 로직 수정 필요 | 표준 문서 검토 |

### Business Assumptions

| Assumption | Confidence | Evidence | Risk if Wrong | Validation Method |
|------------|------------|----------|---------------|-------------------|
| 사용자는 Python 개발 경험이 있음 | High | 라이브러리 특성 | API 문서화 강화 필요 | 사용자 피드백 |
| JSON 출력 형식이 가장 많이 사용됨 | Medium | 현대 API 트렌드 | XML 출력 우선순위 조정 필요 | 사용자 조사 |

---

## Requirements

### Ubiquitous Requirements (항상 활성)

- [REQ-U-001] 시스템은 **항상** 모든 입력 데이터에 대해 Pydantic v2를 사용한 유효성 검증을 수행해야 한다
- [REQ-U-002] 시스템은 **항상** 파싱 오류 발생 시 명확한 오류 메시지와 위치 정보를 제공해야 한다
- [REQ-U-003] 시스템은 **항상** 타입 힌트를 포함하여 IDE 자동완성을 지원해야 한다

### Event-Driven Requirements (이벤트 기반)

- [REQ-E-001] **WHEN** KORMARC 레코드 문자열이 입력되면 **THEN** 구조화된 Record 객체를 반환해야 한다
- [REQ-E-002] **WHEN** Record 객체가 JSON 변환 요청을 받으면 **THEN** 표준 JSON 형식으로 직렬화해야 한다
- [REQ-E-003] **WHEN** Record 객체가 XML 변환 요청을 받으면 **THEN** MARCXML 형식으로 직렬화해야 한다
- [REQ-E-004] **WHEN** MARC21 레코드가 입력되면 **THEN** KORMARC 형식으로 변환할 수 있어야 한다
- [REQ-E-005] **WHEN** 잘못된 형식의 레코드가 입력되면 **THEN** ValidationError를 발생시켜야 한다

### State-Driven Requirements (상태 기반)

- [REQ-S-001] **IF** 레코드에 리더(Leader) 필드가 존재하면 **THEN** 리더의 모든 위치값을 파싱하여 제공해야 한다
- [REQ-S-002] **IF** 필드에 서브필드가 포함되어 있으면 **THEN** 각 서브필드를 개별적으로 접근할 수 있어야 한다
- [REQ-S-003] **IF** 스트리밍 모드가 활성화되면 **THEN** 대용량 파일을 청크 단위로 처리해야 한다

### Unwanted Requirements (금지 사항)

- [REQ-N-001] 시스템은 유효하지 않은 KORMARC 레코드를 **생성하지 않아야 한다**
- [REQ-N-002] 시스템은 파싱 과정에서 원본 데이터를 **변형하지 않아야 한다**
- [REQ-N-003] 시스템은 민감한 메타데이터를 로그에 **노출하지 않아야 한다**

### Optional Requirements (선택 사항)

- [REQ-O-001] **가능하면** 비동기 파일 읽기를 지원하여 I/O 성능을 향상시킨다
- [REQ-O-002] **가능하면** CLI 도구를 제공하여 터미널에서 레코드 변환을 지원한다
- [REQ-O-003] **가능하면** 레코드 비교 및 병합 기능을 제공한다

---

## Specifications

### Core Data Models

#### Leader Model

```
Leader
├── record_length: int (위치 0-4)
├── record_status: str (위치 5)
├── type_of_record: str (위치 6)
├── bibliographic_level: str (위치 7)
├── control_type: str (위치 8)
├── character_encoding: str (위치 9)
├── indicator_count: int (위치 10)
├── subfield_code_count: int (위치 11)
├── base_address: int (위치 12-16)
├── encoding_level: str (위치 17)
├── descriptive_cataloging: str (위치 18)
├── multipart_level: str (위치 19)
└── entry_map: str (위치 20-23)
```

#### Field Models

```
ControlField (001-009)
├── tag: str (3자리)
└── data: str

DataField (010-999)
├── tag: str (3자리)
├── indicator1: str (1자리)
├── indicator2: str (1자리)
└── subfields: list[Subfield]

Subfield
├── code: str (1자리)
└── data: str
```

#### Record Model

```
Record
├── leader: Leader
├── control_fields: list[ControlField]
├── data_fields: list[DataField]
├── to_json() -> str
├── to_xml() -> str
├── to_dict() -> dict
└── validate() -> bool
```

### API Interface

#### Parser Class

```
KORMARCParser
├── parse(data: str | bytes) -> Record
├── parse_file(path: Path) -> Record
├── parse_stream(stream: IO) -> Iterator[Record]
└── validate(data: str | bytes) -> ValidationResult
```

#### Converter Class

```
MARCConverter
├── to_json(record: Record) -> str
├── to_xml(record: Record) -> str
├── to_marc21(record: Record) -> bytes
├── from_marc21(data: bytes) -> Record
└── from_json(data: str) -> Record
```

### Error Handling

```
KORMARCError (Base)
├── ParseError: 파싱 실패
├── ValidationError: 유효성 검증 실패
├── ConversionError: 형식 변환 실패
└── EncodingError: 인코딩 문제
```

---

## Traceability

### Requirement to Test Mapping

| Requirement ID | Test File | Test Function |
|---------------|-----------|---------------|
| REQ-U-001 | test_validation.py | test_pydantic_validation_* |
| REQ-E-001 | test_parser.py | test_parse_kormarc_record |
| REQ-E-002 | test_converter.py | test_to_json_* |
| REQ-E-003 | test_converter.py | test_to_xml_* |
| REQ-E-004 | test_converter.py | test_marc21_conversion |
| REQ-S-001 | test_leader.py | test_leader_parsing_* |
| REQ-S-002 | test_fields.py | test_subfield_access_* |
| REQ-N-001 | test_validation.py | test_invalid_record_rejection |

### Related SPECs

- None (Initial SPEC)

---

## References

- KORMARC 표준: 국립중앙도서관 한국문헌자동화목록형식
- MARC21: Library of Congress MARC Standards
- ISO 2709: Information and documentation - Format for information exchange
- Pydantic v2: https://docs.pydantic.dev/latest/
