# Acceptance Criteria: SPEC-KORMARC-PARSER-001

## SPEC Reference

- **SPEC ID**: SPEC-KORMARC-PARSER-001
- **Title**: KORMARC Parser Library
- **Priority**: High

---

## Test Scenarios

### Feature: KORMARC Record Parsing

#### Scenario: Parse Valid KORMARC Record

```gherkin
Given 유효한 KORMARC 형식의 레코드 문자열이 존재할 때
When KORMARCParser.parse() 메서드를 호출하면
Then Record 객체가 반환되어야 한다
And Record.leader는 24자리 Leader 정보를 포함해야 한다
And Record.control_fields는 제어 필드 목록을 포함해야 한다
And Record.data_fields는 데이터 필드 목록을 포함해야 한다
```

#### Scenario: Parse Record with Multiple Subfields

```gherkin
Given 서브필드가 포함된 데이터 필드를 가진 레코드가 존재할 때
When 해당 레코드를 파싱하면
Then DataField.subfields에 모든 서브필드가 추출되어야 한다
And 각 Subfield는 code와 data 속성을 가져야 한다
And 서브필드 순서가 원본과 동일해야 한다
```

#### Scenario: Handle Invalid Record Format

```gherkin
Given 잘못된 형식의 레코드 문자열이 존재할 때
When KORMARCParser.parse() 메서드를 호출하면
Then ParseError 예외가 발생해야 한다
And 예외 메시지에 오류 위치 정보가 포함되어야 한다
And 예외 메시지에 예상된 형식 정보가 포함되어야 한다
```

---

### Feature: Leader Parsing

#### Scenario: Parse Complete Leader

```gherkin
Given 24자리 Leader 문자열이 존재할 때
When Leader.model_validate()를 호출하면
Then 모든 위치값이 정확히 파싱되어야 한다
And record_length는 정수로 변환되어야 한다
And base_address는 정수로 변환되어야 한다
And 나머지 필드는 문자열로 저장되어야 한다
```

#### Scenario: Validate Leader Length

```gherkin
Given 24자리가 아닌 Leader 문자열이 존재할 때
When Leader 파싱을 시도하면
Then LeaderValidationError가 발생해야 한다
And 오류 메시지에 "Leader must be exactly 24 characters"가 포함되어야 한다
```

---

### Feature: Field Validation

#### Scenario: Validate Control Field Tag

```gherkin
Given 태그가 "001"~"009" 범위인 필드가 존재할 때
When ControlField로 파싱하면
Then 파싱이 성공해야 한다
And tag 속성이 3자리 문자열이어야 한다
```

#### Scenario: Validate Data Field Indicators

```gherkin
Given 인디케이터가 포함된 데이터 필드가 존재할 때
When DataField로 파싱하면
Then indicator1은 1자리 문자열이어야 한다
And indicator2는 1자리 문자열이어야 한다
And 빈 인디케이터는 공백 문자(' ')로 표현되어야 한다
```

---

### Feature: JSON Conversion

#### Scenario: Convert Record to JSON

```gherkin
Given 파싱된 Record 객체가 존재할 때
When record.to_json() 메서드를 호출하면
Then 유효한 JSON 문자열이 반환되어야 한다
And JSON에 "leader" 키가 존재해야 한다
And JSON에 "fields" 키가 존재해야 한다
And 모든 필드 데이터가 보존되어야 한다
```

#### Scenario: Parse JSON to Record

```gherkin
Given 유효한 KORMARC JSON 문자열이 존재할 때
When MARCConverter.from_json() 메서드를 호출하면
Then Record 객체가 반환되어야 한다
And 원본 JSON의 모든 데이터가 보존되어야 한다
```

#### Scenario: JSON Round-trip Integrity

```gherkin
Given 원본 Record 객체가 존재할 때
When to_json()으로 변환 후 from_json()으로 복원하면
Then 복원된 Record는 원본과 동일해야 한다
And 모든 필드 값이 일치해야 한다
And 필드 순서가 보존되어야 한다
```

---

### Feature: XML Conversion

#### Scenario: Convert Record to MARCXML

```gherkin
Given 파싱된 Record 객체가 존재할 때
When record.to_xml() 메서드를 호출하면
Then MARCXML 형식의 문자열이 반환되어야 한다
And XML이 well-formed 해야 한다
And <record> 루트 요소를 가져야 한다
And <leader> 요소가 존재해야 한다
And <controlfield>와 <datafield> 요소가 존재해야 한다
```

#### Scenario: MARCXML Namespace Compliance

```gherkin
Given Record를 XML로 변환할 때
When MARCXML 네임스페이스가 요청되면
Then xmlns="http://www.loc.gov/MARC21/slim" 속성이 포함되어야 한다
```

---

### Feature: MARC21 Compatibility

#### Scenario: Parse MARC21 Record

```gherkin
Given MARC21 형식의 바이너리 레코드가 존재할 때
When MARCConverter.from_marc21() 메서드를 호출하면
Then KORMARC Record 객체로 변환되어야 한다
And 모든 필드가 올바르게 매핑되어야 한다
```

#### Scenario: Export to MARC21

```gherkin
Given KORMARC Record 객체가 존재할 때
When MARCConverter.to_marc21() 메서드를 호출하면
Then ISO 2709 형식의 바이트 데이터가 반환되어야 한다
And 다른 MARC21 호환 시스템에서 읽을 수 있어야 한다
```

---

### Feature: Pydantic Validation

#### Scenario: Automatic Type Validation

```gherkin
Given 잘못된 타입의 데이터로 모델 생성을 시도할 때
When Pydantic 모델 인스턴스화가 실행되면
Then ValidationError가 발생해야 한다
And 오류 메시지에 예상 타입과 실제 타입이 포함되어야 한다
```

#### Scenario: Extra Fields Forbidden

```gherkin
Given 모델에 정의되지 않은 추가 필드가 포함된 데이터가 존재할 때
When 모델 생성을 시도하면
Then ValidationError가 발생해야 한다
And 오류 메시지에 허용되지 않는 필드 이름이 포함되어야 한다
```

---

### Feature: Error Handling

#### Scenario: Detailed Parse Error

```gherkin
Given 파싱 오류가 발생하는 레코드가 존재할 때
When 파싱을 시도하면
Then ParseError가 발생해야 한다
And error.line에 오류 발생 라인 번호가 포함되어야 한다
And error.column에 오류 발생 열 위치가 포함되어야 한다
And error.context에 주변 데이터가 포함되어야 한다
```

#### Scenario: Encoding Error Handling

```gherkin
Given 잘못된 인코딩의 레코드 데이터가 존재할 때
When 파싱을 시도하면
Then EncodingError가 발생해야 한다
And 오류 메시지에 감지된 인코딩과 예상 인코딩이 포함되어야 한다
```

---

## Quality Gate Criteria

### Test Coverage

- [ ] 전체 테스트 커버리지 85% 이상
- [ ] models/ 모듈 커버리지 95% 이상
- [ ] parser/ 모듈 커버리지 90% 이상
- [ ] converter/ 모듈 커버리지 90% 이상

### Performance Criteria

- [ ] 단일 레코드 파싱 시간 < 10ms
- [ ] 1,000 레코드 파싱 시간 < 5초
- [ ] 메모리 사용량: 레코드당 < 1MB

### Code Quality

- [ ] ruff 린터 경고 0개
- [ ] mypy 타입 체크 통과
- [ ] 모든 public API docstring 작성

---

## Verification Methods

### Unit Tests

| Component | Test File | Coverage Target |
|-----------|-----------|-----------------|
| Leader | test_leader.py | 95% |
| ControlField | test_fields.py | 95% |
| DataField | test_fields.py | 95% |
| Record | test_record.py | 90% |
| KORMARCParser | test_kormarc_parser.py | 90% |
| JSONConverter | test_json_converter.py | 90% |
| XMLConverter | test_xml_converter.py | 90% |

### Integration Tests

| Scenario | Test File |
|----------|-----------|
| 파일 파싱 → JSON 변환 | test_integration.py::test_file_to_json |
| JSON → Record → XML | test_integration.py::test_json_to_xml |
| MARC21 → KORMARC → MARC21 | test_integration.py::test_marc21_roundtrip |

### Sample Test Data

```
fixtures/
├── valid/
│   ├── simple_record.mrc      # 기본 레코드
│   ├── complex_record.mrc     # 다중 서브필드 레코드
│   └── unicode_record.mrc     # 유니코드 데이터 포함
├── invalid/
│   ├── short_leader.mrc       # 짧은 리더
│   ├── missing_fields.mrc     # 필수 필드 누락
│   └── bad_encoding.mrc       # 잘못된 인코딩
└── marc21/
    └── sample_marc21.mrc      # MARC21 형식 샘플
```

---

## Definition of Done

### Functional Completeness

- [ ] 모든 EARS 요구사항 구현 완료
- [ ] 모든 Gherkin 시나리오 테스트 통과
- [ ] API 문서화 완료

### Non-Functional Completeness

- [ ] 성능 기준 충족
- [ ] 보안 검토 완료 (민감 데이터 로깅 방지)
- [ ] 호환성 테스트 완료 (Python 3.12+)

### Documentation Completeness

- [ ] README.md 작성
- [ ] API Reference 문서 생성
- [ ] 사용 예제 코드 제공
- [ ] CHANGELOG 업데이트

---

## Traceability

- **Source SPEC**: `/mnt/d/dev/kormarc.man/.moai/specs/SPEC-KORMARC-PARSER-001/spec.md`
- **Implementation Plan**: `/mnt/d/dev/kormarc.man/.moai/specs/SPEC-KORMARC-PARSER-001/plan.md`
