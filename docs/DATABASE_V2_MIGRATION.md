# KORMARC Database Schema v2 마이그레이션 가이드

## 개요

KORMARC Database 스키마 v2는 성능 최적화와 검색 기능 향상을 위해 설계되었습니다.

**주요 개선사항:**
- ✅ 정규화된 컬럼 추가 (title, author, publisher, pub_year, kdc_code)
- ✅ parsed_data를 TEXT에서 JSON 타입으로 변경
- ✅ Leader 필드 추출 및 저장
- ✅ 복합 인덱스 추가 (성능 최적화)
- ✅ FTS5 전문 검색 테이블 및 트리거
- ✅ 카테고리 분할 테이블 제거 (데이터 중복 해소)

---

## v2 스키마 변경사항

### 1. 새로운 컬럼 추가

#### 정규화된 필드
```sql
title TEXT                  -- 제목 (245$a)
author TEXT                 -- 저자 (100$a 또는 700$a)
publisher TEXT              -- 출판사 (260$b 또는 264$b)
pub_year INTEGER            -- 출판년도 (260$c 또는 264$c, 4자리)
kdc_code TEXT               -- KDC 분류 코드 (082$a 또는 080$a)
```

#### Leader 필드
```sql
record_length INTEGER       -- 레코드 길이
record_status TEXT          -- 레코드 상태
impl_defined1 TEXT          -- 구현 정의 1
impl_defined2 TEXT          -- 구현 정의 2
indicator_count INTEGER     -- 지시기호 개수
subfield_code_count INTEGER -- 서브필드 코드 개수
base_address INTEGER        -- 기본 주소
impl_defined3 TEXT          -- 구현 정의 3
entry_map TEXT              -- 엔트리 맵
```

#### CHECK 제약조건
```sql
CHECK(pub_year IS NULL OR (pub_year >= 1000 AND pub_year <= 9999))
```

### 2. 복합 인덱스

```sql
-- KDC 분류 + 출판년도
CREATE INDEX idx_kdc_year ON kormarc_records(kdc_code, pub_year DESC);

-- 출판사 + 출판년도
CREATE INDEX idx_publisher_year ON kormarc_records(publisher, pub_year DESC);

-- 레코드 타입 + 출판년도
CREATE INDEX idx_type_year ON kormarc_records(record_type, pub_year DESC);

-- 제목 인덱스
CREATE INDEX idx_title ON kormarc_records(title);

-- 저자 인덱스
CREATE INDEX idx_author ON kormarc_records(author);
```

### 3. FTS5 전문 검색

```sql
-- FTS5 가상 테이블
CREATE VIRTUAL TABLE kormarc_fts USING fts5(
    title,
    author,
    publisher,
    content=kormarc_records,
    content_rowid=rowid,
    tokenize='unicode61 remove_diacritics 2'
);

-- 자동 동기화 트리거
CREATE TRIGGER kormarc_fts_insert AFTER INSERT ON kormarc_records ...
CREATE TRIGGER kormarc_fts_delete AFTER DELETE ON kormarc_records ...
CREATE TRIGGER kormarc_fts_update AFTER UPDATE ON kormarc_records ...
```

### 4. 제거된 테이블

카테고리별 분할 테이블 제거 (데이터 중복 방지):
- ❌ kormarc_books
- ❌ kormarc_serials
- ❌ kormarc_academics
- ❌ kormarc_comics

---

## 새로운 검색 기능

### 1. 제목 검색 (FTS5 전문 검색)

```python
# FTS5를 활용한 빠른 전문 검색
results = await db.search_by_title("파이썬")
```

### 2. 저자 검색

```python
results = await db.search_by_author("홍길동")
```

### 3. KDC 분류 검색

```python
# KDC 코드로 시작하는 레코드 검색
results = await db.search_by_kdc("005")  # 컴퓨터 과학
```

### 4. 출판사 검색 (연도 필터)

```python
# 특정 출판사의 최근 출판물
results = await db.search_by_publisher("한빛미디어", year_from=2024)

# 연도 범위 지정
results = await db.search_by_publisher(
    "한빛미디어",
    year_from=2020,
    year_to=2024
)
```

### 5. 고급 검색 (복합 조건)

```python
# 여러 조건을 조합한 검색
results = await db.advanced_search(
    title="파이썬",
    author="홍길동",
    publisher="한빛미디어",
    kdc_code="005",
    year_from=2023,
    year_to=2024,
    record_type="kormarc_book",
    limit=100
)
```

---

## 마이그레이션 방법

### 1. 사전 준비

기존 데이터베이스 백업:
```bash
cp kormarc.db kormarc.db.backup
```

### 2. Dry Run (검증)

마이그레이션 전에 dry-run으로 검증:
```bash
python scripts/migrate_to_v2.py kormarc.db kormarc_v2.db --dry-run
```

### 3. 실제 마이그레이션

```bash
python scripts/migrate_to_v2.py kormarc.db kormarc_v2.db --validate
```

**옵션:**
- `--dry-run`: 실제 저장 없이 검증만 수행
- `--validate`: 마이그레이션 후 검증 수행

### 4. 검증

마이그레이션 완료 후 확인:
```bash
sqlite3 kormarc_v2.db "SELECT COUNT(*) FROM kormarc_records"
sqlite3 kormarc_v2.db "PRAGMA table_info(kormarc_records)"
sqlite3 kormarc_v2.db "SELECT name FROM sqlite_master WHERE type='index'"
```

---

## 성능 비교

### v1 (기존)
- **검색**: `LIKE` 연산자로 parsed_data TEXT 검색
- **인덱스**: 단일 컬럼 인덱스만 존재
- **데이터 중복**: 카테고리별 분할 테이블로 인한 중복 저장

### v2 (개선)
- **검색**: FTS5 전문 검색 + 정규화된 컬럼 인덱스
- **인덱스**: 복합 인덱스로 쿼리 최적화
- **데이터 중복**: 단일 테이블로 중복 제거

**예상 성능 향상:**
- 제목 검색: 10-50배 향상 (FTS5)
- KDC/출판사 검색: 5-10배 향상 (복합 인덱스)
- 저장 공간: 20-30% 절감 (중복 제거)

---

## 코드 마이그레이션

### save_record() 사용법 (동일)

```python
# v1과 동일한 인터페이스
await db.save_record(
    toon_id=toon_dict["toon_id"],
    record_data=toon_dict,
    scraped_at="2025-01-10T12:00:00Z",
    data_source="web_scraping"
)
```

v2에서는 내부적으로 자동으로 정규화된 필드를 추출합니다.

### get_record() 반환 구조 변경

```python
record = await db.get_record(toon_id)

# v2에서 추가된 필드
print(record["title"])       # 정규화된 제목
print(record["author"])      # 정규화된 저자
print(record["publisher"])   # 정규화된 출판사
print(record["pub_year"])    # 출판년도 (정수)
print(record["kdc_code"])    # KDC 분류 코드

# Leader 필드
print(record["record_length"])
print(record["record_status"])
```

---

## 호환성

### 하위 호환성 보장

- ✅ `save_record()` 인터페이스 동일
- ✅ `get_record()` 기존 필드 모두 유지
- ✅ `get_by_isbn()` 동일
- ✅ `get_by_type()` 동일
- ✅ `search_records()` FTS5로 자동 위임 (하위 호환)

### 새로운 메서드

- `search_by_title()` - FTS5 전문 검색
- `search_by_author()` - 저자 검색
- `search_by_kdc()` - KDC 분류 검색
- `search_by_publisher()` - 출판사 검색
- `advanced_search()` - 복합 조건 검색

---

## 테스트

### 스키마 검증 테스트

```bash
uv run pytest tests/test_integration/test_scraper_pipeline.py::TestScraperDataIntegrity::test_db_schema_validation -v
```

### 검색 기능 테스트

```bash
uv run pytest tests/test_db_v2_search.py -v
```

### 전체 테스트

```bash
uv run pytest tests/ -v
```

---

## 문제 해결

### 마이그레이션 실패 시

1. **레코드 수 불일치**
   - 원인: 일부 레코드의 parsed_data 형식 오류
   - 해결: 에러 로그 확인 후 해당 레코드 수동 수정

2. **FTS5 테이블 생성 실패**
   - 원인: SQLite FTS5 확장 미설치
   - 해결: SQLite 3.9.0 이상 버전 확인

3. **인덱스 생성 실패**
   - 원인: 기존 데이터의 무결성 문제
   - 해결: CHECK 제약조건 위반 레코드 수정

### 성능 이슈

1. **FTS5 검색이 느림**
   - 해결: `VACUUM` 명령으로 데이터베이스 최적화
   ```bash
   sqlite3 kormarc_v2.db "VACUUM"
   ```

2. **인덱스 재구성**
   ```sql
   REINDEX;
   ```

---

## 참고 자료

- [SQLite FTS5 문서](https://www.sqlite.org/fts5.html)
- [SQLite 인덱싱 가이드](https://www.sqlite.org/queryplanner.html)
- [KORMARC 필드 가이드](./KORMARC_FIELDS.md)
- [TOON 명세](./TOON_SPEC.md)

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-01-10
**작성자**: 지니 (MoAI-ADK)
