# KORMARC Parser

Korean Library Automation Data Format Parser Library

KORMARC Parser는 한국 도서관 자동화 데이터 형식(KORMARC)을 파싱하고 변환하는 Python 라이브러리입니다. MARC21 표준을 기반으로 하며 한국 도서관 환경에 최적화되어 있습니다.

## 특징

- **LINE 기반 파싱**: 간단한 텍스트 형식으로 KORMARC 레코드 파싱
- **MARC21 표준 준수**: 표준 MARCXML 형식으로 변환
- **JSON 지원**: 레코드 데이터를 JSON 형식으로 내보내기
- **타입 안전성**: Pydantic 기반 모델로 데이터 검증 보장
- **UTF-8 지원**: 한국어 및 다국어 문자 완벽 지원
- **포괄적인 테스트**: 90% 이상의 테스트 커버리지

## 설치

```bash
pip install kormarc-parser
```

개발 의존성 포함 설치:

```bash
pip install kormarc-parser[dev]
```

## 빠른 시작

### 기본 사용법

```python
from kormarc import KORMARCParser

# KORMARC 레코드 파싱
parser = KORMARCParser()
record = parser.parse("""
00714cam  2200205 a 4500
001 12345
245 10|aPython 프로그래밍|b초보자 가이드
260   |a서울|b출판사|c2026
""")

# JSON으로 변환
json_data = record.to_json()
print(json_data)

# MARCXML로 변환
xml_data = record.to_xml()
print(xml_data)
```

### 파일에서 파싱

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse_file("data.kormarc")
```

### 데이터 접근

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Leader 정보
print(f"Record Length: {record.leader.record_length}")
print(f"Record Status: {record.leader.record_status}")

# 제어 필드 접근 (001-009)
for cf in record.control_fields:
    print(f"{cf.tag}: {cf.data}")

# 데이터 필드 접근 (010-999)
for df in record.data_fields:
    print(f"{df.tag}: {df.indicator1}{df.indicator2}")
    for sf in df.subfields:
        print(f"  ${sf.code} {sf.data}")
```

## API 레퍼런스

### KORMARCParser

메인 파서 클래스입니다.

#### `parse(data: str | bytes) -> Record`

KORMARC 레코드를 문자열 또는 바이트에서 파싱합니다.

**매개변수:**
- `data`: KORMARC 형식의 레코드 데이터

**반환값:**
- `Record`: 파싱된 레코드 객체

**예외:**
- `ParseError`: 파싱 실패 시

**예시:**
```python
parser = KORMARCParser()
record = parser.parse("""
00714cam  2200205 a 4500
001 12345
245 10|a제목
""")
```

#### `parse_file(path: str) -> Record`

파일에서 KORMARC 레코드를 파싱합니다.

**매개변수:**
- `path`: KORMARC 파일 경로

**반환값:**
- `Record`: 파싱된 레코드 객체

### Record

KORMARC 레코드를 나타내는 모델입니다.

#### 속성

- `leader: Leader` - 레코드 리더 (24자 고정 필드)
- `control_fields: list[ControlField]` - 제어 필드 목록 (001-009)
- `data_fields: list[DataField]` - 데이터 필드 목록 (010-999)

#### 메서드

**`to_dict() -> dict`**
- 레코드를 사전 형태로 변환

**`to_json() -> str`**
- 레코드를 JSON 문자열로 변환

**`to_xml() -> str`**
- 레코드를 MARCXML 형식으로 변환
- 표준 MARC21 스키마 준수

**`validate() -> bool`**
- 레코드 구조와 내용 검증

### Leader

레코드의 리더 필드 (24자 고정 길이)입니다.

#### 주요 속성

- `record_length: int` - 레코드 전체 길이
- `record_status: str` - 레코드 상태 (a, c, d, n, p)
- `type_of_record: str` - 레코드 유형 (a, c, d, 등)
- `bibliographic_level: str` - 서지 레벨 (a, b, c, d, 등)
- `encoding_level: str` - 인코딩 레벨

### ControlField

제어 필드 (001-009)를 나타냅니다.

#### 속성

- `tag: str` - 필드 태그 (001-009)
- `data: str` - 필드 데이터

### DataField

데이터 필드 (010-999)를 나타냅니다.

#### 속성

- `tag: str` - 필드 태그 (010-999)
- `indicator1: str` - 지시자 1
- `indicator2: str` - 지시자 2
- `subfields: list[Subfield]` - 하위 필드 목록

### Subfield

하위 필드를 나타냅니다.

#### 속성

- `code: str` - 하위 필드 코드 (a-z, 0-9)
- `data: str` - 하위 필드 데이터

## MARCXML 변환

라이브러리는 표준 MARC21 스키마를 준수하는 MARCXML 출력을 생성합니다:

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)
xml_output = record.to_xml()
```

생성되는 XML 구조:

```xml
<?xml version='1.0' encoding='utf-8'?>
<record xmlns="http://www.loc.gov/MARC21/slim">
  <leader>00714cam  2200205 a 4500</leader>
  <controlfield tag="001">12345</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Python 프로그래밍</subfield>
    <subfield code="b">초보자 가이드</subfield>
  </datafield>
</record>
```

## 예외 처리

라이브러리는 포괄적인 예외 계층 구조를 제공합니다:

- `KORMARCError` - 모든 KORMARC 에러의 기본 클래스
- `ParseError` - 파싱 실패
- `LeaderParseError` - 리더 파싱 실패
- `FieldParseError` - 필드 파싱 실패
- `SubfieldParseError` - 하위 필드 파싱 실패
- `ValidationError` - 데이터 검증 실패
- `ConversionError` - 변환 실패
- `JSONConversionError` - JSON 변환 실패
- `XMLConversionError` - XML 변환 실패

```python
from kormarc import KORMARCParser
from kormarc.exceptions import ParseError

parser = KORMARCParser()
try:
    record = parser.parse(invalid_data)
except ParseError as e:
    print(f"Parsing failed: {e}")
```

## 테스트

테스트 실행:

```bash
pytest
```

커버리지 보고서:

```bash
pytest --cov=src/kormarc --cov-report=html
```

타입 검사:

```bash
mypy src/
```

코드 포맷팅:

```bash
ruff check src/
ruff format src/
```

## 데이터 형식

KORMARC 레코드는 다음 구조를 따릅니다:

```
LEADER (24자 고정)
TAG 필드데이터
TAG 필드데이터
...
```

**제어 필드 (001-009):**
```
001 데이터값
008 210101s2026    ko |a|
```

**데이터 필드 (010-999):**
```
245 10|a주제|b부제목
260   |a발행지|b출판사|c2026
```

## 프로젝트 구조

```
kormarc-parser/
├── src/
│   └── kormarc/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── constants.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── leader.py
│       │   ├── fields.py
│       │   └── record.py
│       └── parser/
│           ├── __init__.py
│           └── kormarc_parser.py
├── tests/
│   ├── test_models/
│   └── test_integration/
├── pyproject.toml
└── README.md
```

## 라이선스

MIT License

## 기여

기여를 환영합니다! Pull Request를 제출해 주세요.

## 버전

현재 버전: 0.1.0

## 연락처

- 이메일: dev@example.com
- 이슈 트래커: GitHub Issues

## 문서

자세한 문서는 [docs/](docs/) 디렉토리를 참조하세요:

### 핵심 문서
- **[TOON 명세서](docs/TOON_SPEC.md)** - TOON(Timestamped Object-Oriented Notation) 규격
- **[사용 가이드](docs/USAGE.md)** - KORMARC 빌더 사용법
- **[노원구 KORMARC 규칙](docs/NOWON_KORMARC_RULES.md)** - 노원구립도서관 KORMARC 적용 규칙

### 검증 보고서
- **[시방서 준수 검증 보고서](docs/NOWON_COMPLIANCE_VALIDATION_REPORT_100.md)** - 100개 레코드 검증 결과 (상세)
- **[검증 요약](docs/NOWON_VALIDATION_SUMMARY.md)** - 검증 결과 한눈에 보기

### 기타
- **[문서 인덱스](docs/INDEX.md)** - 전체 문서 목차 및 빠른 링크
- **[API 레퍼런스](docs/API.md)** - 완전한 API 문서
- **[사용 예제](docs/EXAMPLES.md)** - 실용적인 사용 예제 및 패턴
- **[변경 로그](CHANGELOG.md)** - 버전 기록 및 릴리스 정보

## 관련 자료

- [MARC21 Format](https://www.loc.gov/marc/bibliographic/)
- [KORMARC 표준](https://www.kslib.or.kr/)
- [MARC21 스키마](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd)
