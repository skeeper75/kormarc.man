# TOON Specification (v1.0)

**Timestamp-Ordered Object Notation** - KORMARC 레코드를 위한 타임스탬프 기반 정렬 가능 식별자

## 목차

- [개요](#개요)
- [표준 기반](#표준-기반)
- [구조](#구조)
- [인코딩](#인코딩)
- [타입 시스템](#타입-시스템)
- [생성 알고리즘](#생성-알고리즘)
- [데이터 스키마](#데이터-스키마)
- [구현 요구사항](#구현-요구사항)
- [보안 고려사항](#보안-고려사항)
- [부록](#부록)

---

## 개요

TOON (Timestamp-Ordered Object Notation)은 KORMARC 레코드를 식별하기 위한 26자리 영숫자 식별자입니다. TypeID와 ULID 표준을 기반으로 설계되어 다음과 같은 특성을 제공합니다:

- **시간순 정렬 가능**: 생성 시간 기준 lexicographic 정렬
- **URL 안전**: URL, 파일명, JSON 키로 사용 가능
- **타입 안전**: 접두사로 레코드 타입 포함
- **고유성 보장**: 타임스탬프와 난수 조합
- **대소문자 무관**: Crockford's Base32 사용

### 예제

```
kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y
kormarc_serial_01HZR9SYXR9VQJXJ9X8Y8Y8Y90
```

---

## 표준 기반

TOON은 다음 오픈 소스 표준을 기반으로 설계되었습니다:

### 1. ULID (Universally Unique Lexicographically Sortable Identifier)

- **공식 명세**: [github.com/ulid/spec](https://github.com/ulid/spec)
- **특징**:
  - 128-bit 식별자
  - 밀리초 단위 UNIX 타임스탬프
  - Lexicographically 정렬 가능
  - 26자 Base32 문자열
  - 1.21×10²⁴ unique ULIDs/ms

### 2. TypeID

- **특징**:
  - UUIDv7 기반
  - 타입 접두사 포함
  - RFC 9562 준수 (2024년 5월 게시)
  - Crockford's Base32 인코딩

### 3. Crockford's Base32

- **알파벳**: `0123456789ABCDEFGHJKMNPQRSTVWXYZ`
- **제외 문자**: `I, L, O, U` (모호함 방지)
- **대소문자 무관**: URL 안전성 향상

---

## 구조

### 바이트 표현 (128-bit)

```
+-----------------------+-----------------------+
| Timestamp (48-bit)    | Randomness (80-bit)   |
| Milliseconds since    | Cryptographically     |
| UNIX epoch            | secure random         |
+-----------------------+-----------------------+
| 0                   47 | 48                  127|
```

### 문자열 표현 (26 characters)

```
+----------+------------------------+
| Prefix   | Encoded ULID           |
| (15 char)| (26 char)              |
+----------+------------------------+
```

**형식**: `{type}_{subtype}_{ulid}`

### 구성 요소

#### 1. 접두사 (Prefix)

타입 정보를 포함하는 15자 이하 문자열:

```
kormarc_book    - 일반 도서
kormarc_serial  - 연속 간행물
kormarc_academic- 학술지
kormarc_comic   - 만화
```

#### 2. ULID (26 characters)

- **Timestamp** (10 characters): 48-bit timestamp
- **Randomness** (16 characters): 80-bit random data

### 예제 분해

```
kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y
│            ││ │ │ │ │ └─ Randomness (80-bit)
│            ││ │ │ │ │    (16 characters)
│            ││ │ │ │ └──── Base32 encoded
│            ││ │ │ └────── Type identifier
│            ││ │ └───────── Timestamp (48-bit)
│            ││ └─────────── Milliseconds since epoch
│            │└────────────── Base32 encoded
│            └─────────────── ULID (26 characters)
└──────────────────────────── Prefix (type_subtype)
```

---

## 인코딩

### Crockford's Base32 알파벳

```
Value: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
Char:  0 1 2 3 4 5 6 7 8 9  A  B  C  D  E  F  G  H  J  K  M  N  P  Q  R  S  T  V  W  X  Y  Z
```

### 특성

- **모호성 제거**: `I` ↔ `1`, `L` ↔ `1`, `O` ↔ `0` 혼동 방지
- **모음 제외**: `U` 제외로 욕설 방지
- **대소문자 무관**: 입력/출력 유연성
- **정렬 보존**: 시간순 정렬 유지

### 인코딩 예제

```python
# 48-bit timestamp = 0x0123456789AB
timestamp_bytes = b'\x01\x23\x45\x67\x89\xAB'
# Base32 encoded = "01HZR9SYXR"

# 80-bit randomness = 0xCDEF0123456789ABCDEF
random_bytes = b'\xCD\xEF\x01\x23\x45\x67\x89\xAB\xCD\xEF'
# Base32 encoded = "9VQJXJ9X8Y8Y8Y8Y"
```

---

## 타입 시스템

### KORMARC 레코드 타입

| 타입 접두사 | 설명 | 용도 |
|------------|------|------|
| `kormarc_book` | 일반 도서 | 단행본, 교육용 도서 |
| `kormarc_serial` | 연속 간행물 | 잡지, 학술지 |
| `kormarc_academic` | 학술지 | 피어 리뷰 논문 |
| `kormarc_comic` | 만화 | 웹툰, 출판 만화 |
| `kormarc_unknown` | 알 수 없음 | 분류 불가 레코드 |

### 타입 결정 규칙

```python
def determine_toon_type(record: KORMARCRecord) -> str:
    """KORMARC 레코드에서 TOON 타입 결정"""

    # 필드 008 (고정길이 데이터)의 위치 06-07 확인
    leader = record.leader
    field_008 = record.get_control_field("008")

    if not field_008:
        return "kormarc_unknown"

    # 위치 21 (bibliographic level)
    bib_level = leader.bibliographic_level

    # 위치 06 (record type)
    record_type = field_008.data[6]

    if record_type == "a":
        return "kormarc_book"
    elif record_type == "m":
        return "kormarc_serial"
    elif record_type == "s":
        return "kormarc_academic"
    elif bib_level == "c" or bib_level == "d":
        return "kormarc_comic"
    else:
        return "kormarc_unknown"
```

---

## 생성 알고리즈므

### 1. 타임스탬프 생성

```python
import time

def get_timestamp_ms() -> int:
    """현재 시간을 밀리초 단위 UNIX 타임스탬프로 반환"""
    return int(time.time() * 1000)
```

### 2. 난수 생성

```python
import os

def get_random_bytes() -> bytes:
    """암호학적으로 안전한 10바이트 난수 생성"""
    return os.urandom(10)
```

### 3. Base32 인코딩

```python
def encode_base32(data: bytes) -> str:
    """Crockford's Base32로 인코딩"""
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

    # 5-bit 단위로 변환
    result = []
    buffer = 0
    bits_left = 0

    for byte in data:
        buffer = (buffer << 8) | byte
        bits_left += 8

        while bits_left >= 5:
            bits_left -= 5
            index = (buffer >> bits_left) & 0x1F
            result.append(alphabet[index])

    if bits_left > 0:
        index = (buffer << (5 - bits_left)) & 0x1F
        result.append(alphabet[index])

    return "".join(result)
```

### 4. 전체 TOON 생성

```python
def generate_toon(record_type: str) -> str:
    """TOON 식별자 생성"""

    # 1. 타임스탬프 (48-bit)
    timestamp = get_timestamp_ms() & 0xFFFFFFFFFFFF

    # 2. 난수 (80-bit)
    random_bytes = get_random_bytes()

    # 3. 결합
    data = timestamp.to_bytes(6, byteorder='big') + random_bytes

    # 4. Base32 인코딩
    ulid = encode_base32(data).upper()

    # 5. 패딩 제거 (26자리)
    ulid = ulid[:26]

    # 6. 접두사 추가
    return f"{record_type}_{ulid}"
```

---

## 데이터 스키마

### JSON 스키마

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TOON KORMARC Record",
  "type": "object",
  "required": [
    "toon_id",
    "timestamp",
    "type",
    "isbn",
    "raw_kormarc",
    "parsed"
  ],
  "properties": {
    "toon_id": {
      "type": "string",
      "pattern": "^[a-z_]+_[0-9A-HJ-KM-NP-TV-Z]{26}$",
      "description": "TOON 식별자 (접두사_26자리ULID)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "생성 시간 (ISO 8601)"
    },
    "type": {
      "type": "string",
      "enum": [
        "kormarc_book",
        "kormarc_serial",
        "kormarc_academic",
        "kormarc_comic",
        "kormarc_unknown"
      ],
      "description": "KORMARC 레코드 타입"
    },
    "isbn": {
      "type": "string",
      "pattern": "^[0-9]{10,17}$",
      "description": "ISBN (10 또는 13자리)"
    },
    "raw_kormarc": {
      "type": "string",
      "description": "원본 KORMARC 레코드 데이터"
    },
    "parsed": {
      "type": "object",
      "description": "파싱된 KORMARC 레코드",
      "properties": {
        "leader": {
          "type": "object",
          "description": "리더 필드"
        },
        "control_fields": {
          "type": "array",
          "items": {
            "type": "object"
          },
          "description": "제어 필드 목록"
        },
        "data_fields": {
          "type": "array",
          "items": {
            "type": "object"
          },
          "description": "데이터 필드 목록"
        }
      }
    }
  }
}
```

### SQLite 스키마

```sql
CREATE TABLE kormarc_records (
    -- TOON 식별자
    toon_id TEXT PRIMARY KEY,

    -- 타임스탬프 (정렬용)
    timestamp_ms INTEGER NOT NULL,
    created_at TEXT NOT NULL,

    -- 타입 정보
    record_type TEXT NOT NULL,
    isbn TEXT NOT NULL,

    -- 원본 데이터
    raw_kormarc TEXT NOT NULL,

    -- 파싱된 데이터 (JSON)
    parsed_data JSON NOT NULL,

    -- 메타데이터
    scraped_at TEXT NOT NULL,
    data_source TEXT NOT NULL,

    -- 인덱스
    INDEX idx_timestamp (timestamp_ms),
    INDEX idx_type (record_type),
    INDEX idx_isbn (isbn),
    INDEX idx_scraped (scraped_at)
);

-- 타입별 분할 테이블 (선택적)
CREATE TABLE kormarc_books AS SELECT * FROM kormarc_records WHERE record_type = 'kormarc_book';
CREATE TABLE kormarc_serials AS SELECT * FROM kormarc_records WHERE record_type = 'kormarc_serial';
```

---

## 구현 요구사항

### 필수 기능

#### 1. TOON 생성기

```python
class TOONGenerator:
    def generate(self, record_type: str) -> str:
        """TOON 식별자 생성"""
        pass

    def parse(self, toon_id: str) -> dict:
        """TOON 식별자 파싱"""
        pass

    def validate(self, toon_id: str) -> bool:
        """TOON 식별자 검증"""
        pass

    def extract_timestamp(self, toon_id: str) -> datetime:
        """TOON에서 타임스탬프 추출"""
        pass
```

#### 2. 타입 결정

```python
def determine_record_type(record: KORMARCRecord) -> str:
    """KORMARC 레코드에서 TOON 타입 결정"""
    pass
```

#### 3. 데이터 변환

```python
def toon_to_json(record: KORMARCRecord, toon_id: str) -> dict:
    """TOON과 레코드를 JSON으로 변환"""
    pass

def json_to_sqlite(data: dict) -> str:
    """JSON 데이터를 SQLite INSERT 문으로 변환"""
    pass
```

### 테스트 요구사항

#### 단위 테스트

```python
def test_toon_generation():
    """TOON 생성 테스트"""
    generator = TOONGenerator()
    toon_id = generator.generate("kormarc_book")

    assert len(toon_id) == 42  # "kormarc_book_" (13) + 26
    assert toon_id.startswith("kormarc_book_")
    assert toon_id.isupper() or toon_id.islower()

def test_toon_parsing():
    """TOON 파싱 테스트"""
    generator = TOONGenerator()
    toon_id = "kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y"

    parsed = generator.parse(toon_id)
    assert parsed["type"] == "kormarc_book"
    assert parsed["ulid"] == "01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y"

def test_toon_sorting():
    """TOON 정렬 가능성 테스트"""
    generator = TOONGenerator()

    toon1 = generator.generate("kormarc_book")
    time.sleep(0.001)  # 1ms 대기
    toon2 = generator.generate("kormarc_book")

    assert toon1 < toon2  # 시간순 정렬

def test_toon_uniqueness():
    """TOON 고유성 테스트"""
    generator = TOONGenerator()
    toons = {generator.generate("kormarc_book") for _ in range(10000)}

    assert len(toons) == 10000  # 중복 없음
```

#### 통합 테스트

```python
def test_kormarc_to_toon_pipeline():
    """KORMARC → TOON 파이프라인 테스트"""
    parser = KORMARCParser()
    generator = TOONGenerator()

    raw_kormarc = "..."  # 실제 KORMARC 데이터
    record = parser.parse(raw_kormarc)

    record_type = determine_record_type(record)
    toon_id = generator.generate(record_type)

    json_data = toon_to_json(record, toon_id)

    assert "toon_id" in json_data
    assert "timestamp" in json_data
    assert "type" in json_data
```

---

## 보안 고려사항

### 1. 난수 생성

- **요구사항**: 암호학적으로 안전한 난수 생성기 (CSPRNG)
- **구현**: `os.urandom()` 또는 `secrets` 모듈
- **금지**: `random` 모듈 (예측 가능)

### 2. 타임스탬프 노출

- **위험**: 생성 시간 정보 노출
- **완화**: 정밀도 제한 (초 단위로 반올림)
- **대안**: UUIDv4 사용 (시간 정보 제거)

### 3. 식별자 추적

- **위험**: 사용자 활동 추적 가능
- **완화**: 주기적 키 로테이션
- **대안**: 별도 내부 식별자 사용

### 4. 충돌 공격

- **위험**: 고의적 충돌 시도
- **완화**: 80-bit 난수 (충돌 확률 1/2^80)
- **검증**: 데이터베이스 UNIQUE 제약조건

---

## 부록

### A. 용어 사전

| 용어 | 정의 |
|------|------|
| TOON | Timestamp-Ordered Object Notation |
| ULID | Universally Unique Lexicographically Sortable Identifier |
| TypeID | 타입 접두사가 포함된 UUID |
| Crockford's Base32 | 모호성을 제거한 Base32 인코딩 |
| KORMARC | 한국 도서관 자동화 데이터 형식 |
| ISBN | 국제 표준 도서 번호 |

### B. 참조 표준

- **ULID Specification**: [github.com/ulid/spec](https://github.com/ulid/spec)
- **UUID RFC 9562**: [rfc-editor.org/rfc/rfc9562](https://www.ietf.org/rfc/rfc9562.html)
- **Crockford's Base32**: [crockford.com/wrmg/base32.html](https://www.crockford.com/wrmg/base32.html)
- **KORMARC 표준**: 국립중앙도서관

### C. 예제 구현

```python
# 완전한 예제는 src/kormarc/toon_generator.py 참조
# 테스트는 tests/test_toon_generator.py 참조
```

### D. 변경 로그

| 버전 | 날짜 | 변경사항 |
|------|------|----------|
| 1.0 | 2025-01-10 | 초기 명세 게시 |

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-10
**작성**: 지니 (MoAI-ADK)
**라이선스**: MIT
