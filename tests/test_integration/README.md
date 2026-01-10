# KORMARC Parser Integration Tests

통합 테스트 스위트: API, Scraper, DB, E2E 워크플로우 테스트

## 📁 파일 구조

```
tests/test_integration/
├── __init__.py                     # 패키지 초기화 및 공통 fixture export
├── README.md                       # 이 문서
├── fixtures/
│   ├── __init__.py                # Fixture 패키지 초기화
│   └── mock_api_responses.py      # Mock API 응답 및 테스트 데이터 (241 lines)
├── test_api_pipeline.py           # API 파이프라인 테스트 (324 lines)
├── test_scraper_pipeline.py       # Scraper 파이프라인 테스트 (333 lines)
└── test_e2e_workflow.py           # End-to-End 워크플로우 테스트 (415 lines)
```

**총 코드**: 1,313 lines

## 🧪 테스트 개요

### 1. test_api_pipeline.py (7개 테스트)

**목적**: API → MARCXML → KORMARC → TOON 변환 파이프라인 검증

**테스트 클래스**:
- `TestAPISearchToKORMARCConversion` (5개)
  - ✅ `test_api_search_to_kormarc_conversion`: 전체 파이프라인 (API → Record → TOON)
  - ✅ `test_api_marcxml_parsing`: MARCXML 파싱 정확도
  - ✅ `test_toon_generation_from_api_data`: TOON 생성 및 포맷 검증
  - ✅ `test_api_error_handling`: 네트워크 오류, 타임아웃 처리
  - ✅ `test_api_empty_results`: 빈 검색 결과 처리

- `TestAPIDataValidation` (2개)
  - ✅ `test_multiple_books_from_api`: 여러 도서의 고유 TOON ID 생성
  - ✅ `test_toon_dict_structure`: build_toon_dict() JSON 구조 검증

**주요 기술**:
- Mock httpx.AsyncClient로 API 호출 시뮬레이션
- MARCXML 샘플 데이터를 사용한 파싱 테스트
- TOON ID 포맷 및 고유성 검증

### 2. test_scraper_pipeline.py (9개 테스트)

**목적**: Scraper → BookInfo → KORMARC → DB 저장 파이프라인 검증

**테스트 클래스**:
- `TestScraperSearchToDB` (5개)
  - ✅ `test_scraper_search_to_db_save`: 전체 파이프라인 (Scraper → DB → 검색)
  - ✅ `test_scraper_data_extraction`: 스크래핑 데이터 추출 정확도
  - ✅ `test_db_save_and_retrieve`: DB 저장 및 검색 (TOON ID, ISBN)
  - ✅ `test_scraper_error_handling`: 필수 필드 누락 처리
  - ⏭️ `test_playwright_unavailable`: Playwright 미설치 시 graceful skip

- `TestScraperDataIntegrity` (4개)
  - ✅ `test_multiple_records_from_scraper`: 여러 레코드 독립 저장
  - ✅ `test_db_duplicate_handling`: 중복 TOON ID 덮어쓰기
  - ✅ `test_db_schema_validation`: DB 스키마 검증
  - (추가 테스트)

**주요 기술**:
- Mock 스크래핑 데이터 사용
- 임시 SQLite DB (tmp_path fixture)
- DB 스키마 및 인덱스 검증

### 3. test_e2e_workflow.py (8개 테스트)

**목적**: ISBN → API/Scraper → KORMARC → TOON → DB 전체 워크플로우 검증

**테스트 클래스**:
- `TestE2EWorkflow` (5개)
  - ✅ `test_isbn_to_db_via_api`: 전체 파이프라인 (ISBN 입력 → DB 저장)
  - ✅ `test_api_failure_fallback_to_scraper`: API 실패 시 스크래퍼 폴백
  - ✅ `test_data_integrity_end_to_end`: 입력 ISBN과 DB ISBN 일치 검증
  - ✅ `test_duplicate_isbn_handling`: 중복 ISBN 처리
  - ✅ `test_toon_id_consistency`: TOON ID 포맷 일관성

- `TestE2EErrorRecovery` (3개)
  - ✅ `test_partial_data_handling`: 최소 필드만으로 처리 가능
  - ✅ `test_db_connection_recovery`: DB 재연결 후 데이터 접근
  - ✅ `test_concurrent_writes`: 순차 다중 레코드 저장

**주요 기술**:
- 전체 모듈 통합 테스트 (API, Scraper, Builder, TOON, DB)
- 오류 시나리오 및 복구 테스트
- 데이터 무결성 검증

### 4. fixtures/mock_api_responses.py

**제공 데이터**:
- `SAMPLE_ISBN`: "9788960777330" (테스트용 표준 ISBN)
- `SAMPLE_MARCXML_RESPONSE`: 완전한 MARCXML 응답 샘플
- `SAMPLE_EMPTY_MARCXML_RESPONSE`: 빈 검색 결과
- `SAMPLE_KORMARC_DATA`: 파싱된 KORMARC 데이터
- `SAMPLE_SCRAPER_DATA`: 웹 스크래핑 결과 샘플

**헬퍼 함수**:
- `create_mock_marcxml(isbn, title)`: 커스텀 MARCXML 생성
- `create_mock_scraper_data(isbn, **kwargs)`: 커스텀 스크래핑 데이터 생성
- `create_mock_api_error_response()`: API 오류 응답 생성

## 🚀 실행 방법

### 전체 통합 테스트 실행

```bash
# 모든 통합 테스트
uv run pytest tests/test_integration/ -v

# 특정 파일만
uv run pytest tests/test_integration/test_api_pipeline.py -v

# 커버리지 포함
uv run pytest tests/test_integration/ --cov=kormarc --cov-report=html
```

### 마커별 실행

```bash
# integration 마커가 있는 테스트만
uv run pytest -m integration -v

# asyncio 테스트만
uv run pytest -m asyncio -v
```

### 특정 테스트만 실행

```bash
# 특정 테스트 함수
uv run pytest tests/test_integration/test_api_pipeline.py::TestAPISearchToKORMARCConversion::test_api_search_to_kormarc_conversion -v

# 특정 클래스
uv run pytest tests/test_integration/test_e2e_workflow.py::TestE2EWorkflow -v
```

## 📊 테스트 커버리지

**파이프라인 커버리지**:
- ✅ API 호출 → MARCXML 파싱 → KORMARC 생성
- ✅ 웹 스크래핑 → BookInfo 변환 → KORMARC 생성
- ✅ KORMARC → TOON 생성 → JSON 직렬화
- ✅ TOON → DB 저장 → 검색 (TOON ID, ISBN)
- ✅ 오류 처리 및 폴백 로직

**주요 모듈 통합**:
- `api_client.py`: NationalLibraryClient
- `scraper.py`: NationalLibraryScraper (Mock)
- `kormarc_builder.py`: KORMARCBuilder, BookInfo
- `toon_generator.py`: TOONGenerator
- `db.py`: KORMARCDatabase

## 🎯 테스트 전략

### 테스트 피라미드

```
        E2E (10%)
       /         \
    Integration (20%)
   /                 \
 Unit Tests (70%)
```

**통합 테스트 범위** (현재 파일):
- API 파이프라인: 7개 테스트
- Scraper 파이프라인: 9개 테스트
- E2E 워크플로우: 8개 테스트
- **총 24개 테스트** (모두 통과 ✅)

### Mock 전략

**API 테스트**:
- httpx.AsyncClient를 Mock으로 대체
- MARCXML 응답을 fixture에서 제공
- 네트워크 오류 시뮬레이션

**Scraper 테스트**:
- Playwright를 Mock 데이터로 대체
- HTML 파싱 대신 사전 정의된 데이터 사용
- Playwright 미설치 시 graceful skip

**DB 테스트**:
- 임시 SQLite DB (tmp_path fixture)
- 각 테스트 독립적인 DB 인스턴스
- 테스트 후 자동 정리

## ✅ 검증 항목

### 데이터 무결성
- [x] ISBN 일관성 (입력 → DB)
- [x] TOON ID 고유성
- [x] TOON ID 포맷 (prefix_26chars)
- [x] MARCXML 파싱 정확도
- [x] JSON 직렬화 구조

### 오류 처리
- [x] API 네트워크 오류
- [x] API 타임아웃
- [x] 빈 검색 결과
- [x] 필수 필드 누락
- [x] DB 연결 실패 및 복구

### 성능 및 확장성
- [x] 여러 레코드 순차 저장
- [x] 중복 레코드 처리
- [x] DB 재연결 시 데이터 접근

## 🔧 유지보수

### 새로운 테스트 추가

1. **fixtures/mock_api_responses.py에 샘플 데이터 추가**
   ```python
   SAMPLE_NEW_DATA = {...}
   ```

2. **적절한 테스트 파일에 테스트 추가**
   ```python
   @pytest.mark.integration
   @pytest.mark.asyncio
   async def test_new_feature(self, tmp_path):
       # 테스트 구현
       pass
   ```

3. **테스트 실행 및 검증**
   ```bash
   uv run pytest tests/test_integration/test_api_pipeline.py::TestAPISearchToKORMARCConversion::test_new_feature -v
   ```

### 일반적인 문제 해결

**문제**: `AttributeError: 'KORMARCDatabase' object has no attribute 'get_record_by_isbn'`
**해결**: `get_by_isbn()` 메서드 사용 (리스트 반환)

**문제**: `RuntimeWarning: coroutine 'AsyncMockMixin._execute_mock_call' was never awaited`
**해결**: Mock 응답의 `raise_for_status`를 `AsyncMock()`으로 설정

**문제**: Playwright 관련 테스트 실패
**해결**: `@pytest.mark.skipif(not HAS_PLAYWRIGHT)` 데코레이터 사용

## 📝 주석 규칙

- **한글 주석**: 테스트 목적 및 중요 단계 설명
- **English docstrings**: 함수/클래스 설명
- **Assertion 메시지**: 실패 시 명확한 오류 정보 제공

## 🔗 관련 문서

- [TOON Specification](../../docs/TOON_SPEC.md)
- [KORMARC Builder](../../src/kormarc/kormarc_builder.py)
- [API Client](../../src/kormarc/api_client.py)
- [Database Module](../../src/kormarc/db.py)

---

**Last Updated**: 2025-01-10
**Total Tests**: 24 (모두 통과 ✅)
**Total Lines**: 1,313
**Coverage Target**: 85% (통합 테스트)
