# KORMARC Builder 사용 가이드

도서 정보(BookInfo)를 KORMARC 레코드로 변환하고 TOON 식별자를 생성하는 방법을 안내합니다.

## 설치

```bash
# 가상 환경 활성화
source .venv/bin/activate

# 패키지 설치
pip install -e .
```

## 빠른 시작

### 기본 사용법

```python
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder

# 1. BookInfo 생성
book = BookInfo(
    isbn="9788960777330",
    title="이것이 우다다",
    author="박응용",
    publisher="한빛미디어",
    pub_year="2025",
    pages=500,
    kdc="005",  # 기술과학
)

# 2. 빌더 초기화
builder = KORMARCBuilder()

# 3. KORMARC Record 생성
record = builder.build(book)

# 4. XML로 변환
print(record.to_xml())
```

### TOON 식별자와 함께 생성

```python
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder

book = BookInfo(isbn="9788960777330", title="테스트 도서")
builder = KORMARCBuilder()

# Record + TOON ID 생성
record, toon_id = builder.build_with_toon(book)

print(f"TOON ID: {toon_id}")
print(f"XML:\n{record.to_xml()}")
```

출력 예:
```
TOON ID: kormarc_book_06DTEFMFXPJC70YJV15HP0C70C
XML:
<?xml version='1.0' encoding='utf-8'?>
<ns0:record xmlns:ns0="http://www.loc.gov/MARC21/slim">
  <ns0:leader>00714aamma2200205   4500</ns0:leader>
  <ns0:controlfield tag="001">000000100000</ns0:controlfield>
  ...
</ns0:record>
```

### JSON 형식으로 변환

```python
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
import json

book = BookInfo(isbn="9788960777330", title="테스트 도서", kdc="005")
builder = KORMARCBuilder()

# TOON JSON 생성
toon_dict = builder.build_toon_dict(book)

print(json.dumps(toon_dict, indent=2, ensure_ascii=False))
```

출력 예:
```json
{
  "toon_id": "kormarc_book_06DTEFMFXPJC70YJV15HP0C70C",
  "timestamp": "2026-01-10T09:30:53.807000+00:00",
  "type": "kormarc_book",
  "isbn": "9788960777330",
  "raw_kormarc": "<?xml version='1.0' ...",
  "parsed": {
    "leader": {...},
    "control_fields": [...],
    "data_fields": [...]
  }
}
```

## BookInfo 필드

| 필드 | 타입 | 필수여부 | 설명 |
|------|------|----------|------|
| isbn | str | 필수 | ISBN (10 또는 13자리) |
| title | str | 필수 | 도서 제목 |
| author | str \| None | 선택 | 저자명 |
| publisher | str \| None | 선택 | 발행처 |
| pub_year | str \| None | 선택 | 발행년 (YYYY 또는 YYYYMM) |
| pages | int \| None | 선택 | 페이지수 |
| kdc | str \| None | 선택 | KDC 분류코드 (0-9로 시작, 최대 3자리) |
| category | str | 선택 | 도서 유형 (book, serial, academic, comic) |
| price | int \| None | 선택 | 가격 (원) |
| description | str \| None | 선택 | 내용 요약 |

## 도서 유형 (Category)

| 카테고리 | 설명 | TOON 접두사 |
|----------|------|-------------|
| book | 일반 도서 (단행본) | kormarc_book |
| serial | 연속 간행물 (잡지) | kormarc_serial |
| academic | 학술지 | kormarc_academic |
| comic | 만화 | kormarc_comic |

## KDC 분류

```python
from kormarc.validators import KDCValidator

# KDC 검증
result = KDCValidator.validate("005")  # 기술과학
print(result.is_valid)  # True

# 주제명 확인
category = KDCValidator.get_category_name("005")
print(category)  # "총류" (0번 첫째 자리)
```

### KDC 주 분류

| 코드 | 주제 |
|------|------|
| 0 | 총류 |
| 1 | 철학 |
| 2 | 종교 |
| 3 | 사회과학 |
| 4 | 자연과학 |
| 5 | 기술과학 |
| 6 | 예술 |
| 7 | 언어 |
| 8 | 문학 |
| 9 | 역사 |

## ISBN 검증

```python
from kormarc.validators import ISBNValidator

# ISBN 검증
result = ISBNValidator.validate("9788960777330")
print(result.is_valid)  # True/False
print(result.errors)    # 오류 목록
print(result.warnings)  # 경고 목록

# ISBN 정규화 (하이픈 제거)
normalized = ISBNValidator.normalize("978-89-6077-733-0")
print(normalized)  # "9788960777330"
```

## 고급 사용법

### 커스텀 TOON 생성기 사용

```python
from kormarc.kormarc_builder import KORMARCBuilder
from kormarc.toon_generator import TOONGenerator

# 커스텀 TOON 생성기
custom_gen = TOONGenerator()
builder = KORMARCBuilder(toon_generator=custom_gen)
```

### 여러 도서 일괄 처리

```python
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
import json

books_data = [
    {"isbn": "9788960777330", "title": "도서 1", "kdc": "005"},
    {"isbn": "9788960777331", "title": "도서 2", "kdc": "813"},
]

builder = KORMARCBuilder()
results = []

for book_data in books_data:
    book = BookInfo(**book_data)
    toon_dict = builder.build_toon_dict(book)
    results.append(toon_dict)

# JSON 파일로 저장
with open("books.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

### Pydantic Record 직접 사용

```python
from kormarc.models.record import Record
from kormarc.models.fields import ControlField, DataField, Subfield
from kormarc.models.leader import Leader

# Record 직접 생성
record = Record(
    leader=Leader.from_string("00714cam  2200205 a 4500"),
    control_fields=[
        ControlField(tag="001", data="000000100000"),
        ControlField(tag="003", data="NLK"),
    ],
    data_fields=[
        DataField(
            tag="040",
            indicator1=" ",
            indicator2=" ",
            subfields=[
                Subfield(code="a", data="NLK"),
                Subfield(code="b", data="kor"),
            ],
        ),
    ],
)

# XML 변환
xml = record.to_xml()
```

## KORMARC 필드 매핑

### 제어 필드 (Control Fields)

| 태그 | 필드명 | 필수여부 | 생성 방식 |
|------|--------|----------|-----------|
| 001 | 제어번호 | 필수 | 자동 생성 |
| 003 | 제어번호 식별기호 | 필수 | NLK (고정) |
| 005 | 최종 처리일시 | 필수 | 현재 시간 |
| 008 | 부호화정보필드 | 필수 | 자동 생성 |

### 데이터 필드 (Data Fields)

| 태그 | 필드명 | 필수여부 | BookInfo 필드 |
|------|--------|----------|----------------|
| 020 | ISBN | 권장 | isbn |
| 040 | 목록작성기관 | 필수 | (자동 생성) |
| 100 | 주요 저자-개인명 | 조건 | author |
| 245 | 표제와 책임표시사항 | 필수 | title |
| 260 | 발행, 배포, 간사 사항 | 필수 | publisher, pub_year |
| 300 | 형태사항 | 조건 | pages |
| 082 | 듀이십진분류기호 | 선택 | kdc |
| 650 | 주제명부출표목 | 선택 | kdc (자동 매핑) |

## 테스트

```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 파일
pytest tests/test_kormarc_builder.py -v

# 커버리지 확인
pytest --cov=kormarc tests/
```

## 예제 프로그램

```python
# example.py
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
import json

def main():
    # 도서 정보 입력
    book = BookInfo(
        isbn="9788960777330",
        title="파이썬 프로그래밍 정복",
        author="박응용",
        publisher="한빛미디어",
        pub_year="2025",
        pages=880,
        kdc="005",
        category="book",
    )

    # 빌더 실행
    builder = KORMARCBuilder()
    record, toon_id = builder.build_with_toon(book)

    # 결과 출력
    print(f"=== TOON ID ===\n{toon_id}\n")
    print(f"=== KORMARC XML ===\n{record.to_xml()}\n")

    # JSON 저장
    toon_dict = builder.build_toon_dict(book)
    with open(f"{toon_id}.json", "w", encoding="utf-8") as f:
        json.dump(toon_dict, f, indent=2, ensure_ascii=False)

    print(f"JSON 저장 완료: {toon_id}.json")

if __name__ == "__main__":
    main()
```

실행:
```bash
python example.py
```

## 참고 문헌

- [KORMARC 표준](https://librarian.nl.go.kr/kormarc/) - 국립중앙도서관
- [MARC21 스키마](http://www.loc.gov/standards/marcxml/) - 미의회도서관
- [TOON 명세](./TOON_SPEC.md) - 프로젝트 내부 문서
- [노원구 KORMARC 규칙](./NOWON_KORMARC_RULES.md) - 프로젝트 내부 문서
