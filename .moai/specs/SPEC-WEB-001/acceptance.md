---
id: SPEC-WEB-001
version: "1.0.0"
status: "draft"
created: "2026-01-11"
updated: "2026-01-11"
---

# SPEC-WEB-001 수락 기준 (Acceptance Criteria)

## 1. 수락 기준 개요

### 1.1 목적

SPEC-WEB-001의 구현 완료를 검증하기 위한 명확한 수락 기준을 정의합니다.

### 1.2 테스트 방법

- **형식**: Given/When/Then 시나리오
- **도구**: pytest (백엔드), Playwright (E2E)
- **커버리지**: 85% 이상

### 1.3 품질 게이트

- **테스트 커버리지**: 85% 이상
- **Linting**: ruff 0 에러, 0 경고
- **타입 체킹**: mypy 0 에러
- **보안**: OWASP Top 10 기본 준수

---

## 2. Given/When/Then 시나리오

### 2.1 Scenario 1: 레코드 목록 조회

**Given** (전제 조건):
- SQLite 데이터베이스에 100개의 KORMARC 레코드가 저장되어 있다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/records?page=1&size=20` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 200 응답을 반환한다.
- 응답 본문에 20개의 레코드 목록이 포함된다.
- 응답 본문에 `total`, `page`, `size` 필드가 포함된다.
- `total` 필드 값이 100이다.

**검증 방법**:
```python
# tests/test_records.py
async def test_get_records_list(async_client):
    response = await async_client.get("/api/v1/records?page=1&size=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 20
    assert data["total"] == 100
    assert data["page"] == 1
    assert data["size"] == 20
```

---

### 2.2 Scenario 2: 단일 레코드 조회 성공

**Given** (전제 조건):
- SQLite 데이터베이스에 ID가 "1"인 레코드가 존재한다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/records/1` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 200 응답을 반환한다.
- 응답 본문에 레코드의 상세 정보가 포함된다.
- 응답 본문에 `id`, `title`, `author`, `publisher` 필드가 포함된다.

**검증 방법**:
```python
# tests/test_records.py
async def test_get_record_detail(async_client):
    response = await async_client.get("/api/v1/records/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert "title" in data
    assert "author" in data
    assert "publisher" in data
```

---

### 2.3 Scenario 3: 존재하지 않는 레코드 조회

**Given** (전제 조건):
- SQLite 데이터베이스에 ID가 "999999"인 레코드가 존재하지 않는다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/records/999999` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 404 응답을 반환한다.
- 응답 본문에 `detail` 필드가 포함되며 "Record not found" 메시지가 포함된다.

**검증 방법**:
```python
# tests/test_records.py
async def test_get_record_not_found(async_client):
    response = await async_client.get("/api/v1/records/999999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()
```

---

### 2.4 Scenario 4: 키워드 검색

**Given** (전제 조건):
- SQLite 데이터베이스에 FTS5 인덱스가 설정되어 있다.
- 제목에 "서울"이 포함된 레코드가 5개 이상 존재한다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/search?q=서울&page=1&size=10` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 200 응답을 반환한다.
- 응답 본문에 검색 결과 목록이 포함된다.
- 검색 결과의 제목 또는 본문에 "서울"이 포함된다.
- 응답 본문에 `total`, `page`, `size` 필드가 포함된다.

**검증 방법**:
```python
# tests/test_search.py
async def test_search_by_keyword(async_client):
    response = await async_client.get("/api/v1/search?q=서울&page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    # 검색 결과가 키워드를 포함하는지 검증
    for item in data["items"]:
        assert "서울" in item["title"] or "서울" in item.get("description", "")
```

---

### 2.5 Scenario 5: 레코드 내보내기 (JSON)

**Given** (전제 조건):
- SQLite 데이터베이스에 ID가 "1", "2", "3"인 레코드가 존재한다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/export/json?record_ids=1,2,3` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 200 응답을 반환한다.
- 응답 헤더의 `Content-Type`이 `application/json`이다.
- 응답 헤더의 `Content-Disposition`이 `attachment; filename="records.json"`이다.
- 응답 본문에 3개의 레코드 데이터가 JSON 배열 형식으로 포함된다.

**검증 방법**:
```python
# tests/test_export.py
async def test_export_json(async_client):
    response = await async_client.get("/api/v1/export/json?record_ids=1,2,3")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers.get("content-disposition", "")
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
```

---

### 2.6 Scenario 6: 레코드 내보내기 (MARCXML)

**Given** (전제 조건):
- SQLite 데이터베이스에 ID가 "1", "2"인 레코드가 존재한다.
- FastAPI 서버가 실행 중이다.

**When** (실행 조건):
- 사용자가 `GET /api/v1/export/marcxml?record_ids=1,2` 엔드포인트를 호출한다.

**Then** (기대 결과):
- HTTP 200 응답을 반환한다.
- 응답 헤더의 `Content-Type`이 `application/xml`이다.
- 응답 헤더의 `Content-Disposition`이 `attachment; filename="records.xml"`이다.
- 응답 본문이 유효한 MARCXML 형식이다.
- MARCXML에 2개의 `<record>` 요소가 포함된다.

**검증 방법**:
```python
# tests/test_export.py
import xml.etree.ElementTree as ET

async def test_export_marcxml(async_client):
    response = await async_client.get("/api/v1/export/marcxml?record_ids=1,2")
    assert response.status_code == 200
    assert "xml" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    # XML 파싱 검증
    root = ET.fromstring(response.content)
    records = root.findall(".//record")
    assert len(records) == 2
```

---

## 3. 성능 기준

### 3.1 응답 시간

**목표**:
- **P50**: 50ms 이하
- **P95**: 100ms 이하
- **P99**: 200ms 이하

**측정 방법**:
- pytest-benchmark를 사용하여 API 엔드포인트 응답 시간 측정
- 100회 요청의 백분위수 계산

**검증 방법**:
```python
# tests/test_performance.py
import pytest
from pytest_benchmark.fixture import BenchmarkFixture

def test_record_list_performance(benchmark: BenchmarkFixture, async_client):
    def fetch_records():
        return async_client.get("/api/v1/records?page=1&size=20")

    result = benchmark(fetch_records)
    # P95 < 100ms 검증
    assert result.stats.stats.q_95 < 0.1  # 100ms
```

### 3.2 동시 사용자 지원

**목표**:
- 10명 동시 접속 시 응답 시간 유지

**측정 방법**:
- pytest-xdist를 사용하여 10개의 병렬 테스트 실행
- 응답 시간이 단일 사용자 대비 2배 이내 유지

**검증 방법**:
```bash
# 10개 병렬 테스트 실행
pytest -n 10 tests/test_performance.py
```

### 3.3 데이터베이스 쿼리 성능

**목표**:
- 모든 쿼리 실행 시간 100ms 이내

**측정 방법**:
- SQLite EXPLAIN QUERY PLAN 분석
- 인덱스 활용 확인

**검증 방법**:
```python
# tests/test_database.py
def test_query_uses_index(db_connection):
    cursor = db_connection.cursor()
    query = "SELECT * FROM records WHERE id = ?"
    cursor.execute(f"EXPLAIN QUERY PLAN {query}", ("1",))
    plan = cursor.fetchall()
    # 인덱스 사용 확인
    assert any("USING INDEX" in str(row) for row in plan)
```

---

## 4. 품질 게이트

### 4.1 테스트 커버리지

**목표**: 85% 이상

**측정 방법**:
```bash
pytest --cov=src/kormarc_web --cov-report=term-missing
```

**기준**:
- **합격**: 커버리지 >= 85%
- **불합격**: 커버리지 < 85%

### 4.2 Linting

**목표**: ruff 0 에러, 0 경고

**측정 방법**:
```bash
ruff check src/kormarc_web
```

**기준**:
- **합격**: 에러 0개, 경고 0개
- **불합격**: 에러 또는 경고 존재

### 4.3 타입 체킹

**목표**: mypy 0 에러

**측정 방법**:
```bash
mypy src/kormarc_web
```

**기준**:
- **합격**: 타입 에러 0개
- **불합격**: 타입 에러 존재

### 4.4 보안 준수

**목표**: OWASP Top 10 기본 준수

**검증 항목**:
1. **SQL 인젝션 방지**: Parameterized 쿼리 사용
2. **XSS 방지**: 프론트엔드 입력 검증 및 이스케이프
3. **CORS 설정**: 허용된 도메인만 접근
4. **입력 검증**: Pydantic 스키마 검증

**검증 방법**:
```python
# tests/test_security.py
async def test_sql_injection_prevention(async_client):
    # SQL 인젝션 시도
    malicious_id = "1' OR '1'='1"
    response = await async_client.get(f"/api/v1/records/{malicious_id}")
    # 404 또는 422 응답 (정상적으로 처리됨)
    assert response.status_code in [404, 422]
```

---

## 5. 프론트엔드 검증

### 5.1 UI 컴포넌트 렌더링

**검증 시나리오**:
- RecordList 컴포넌트가 레코드 목록을 올바르게 렌더링한다.
- RecordDetail 컴포넌트가 레코드 상세 정보를 올바르게 렌더링한다.
- SearchBar 컴포넌트가 검색 입력을 올바르게 처리한다.

**검증 방법**:
```typescript
// tests/RecordList.test.tsx
import { render, screen } from '@testing-library/react';
import RecordList from '../components/RecordList';

test('renders record list', () => {
  const records = [{ id: '1', title: 'Test Record' }];
  render(<RecordList records={records} />);
  expect(screen.getByText('Test Record')).toBeInTheDocument();
});
```

### 5.2 E2E 테스트 (선택)

**검증 시나리오**:
- 사용자가 홈 페이지에서 레코드 목록을 볼 수 있다.
- 사용자가 레코드를 클릭하여 상세 페이지로 이동할 수 있다.
- 사용자가 검색 바에서 키워드를 입력하여 검색 결과를 볼 수 있다.

**검증 방법** (Playwright):
```typescript
// tests/e2e/record-list.spec.ts
import { test, expect } from '@playwright/test';

test('user can view record list', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await expect(page.locator('h1')).toContainText('KORMARC 레코드');
  const recordCount = await page.locator('.record-card').count();
  expect(recordCount).toBeGreaterThan(0);
});

test('user can search records', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.fill('input[placeholder="검색"]', '서울');
  await page.press('input[placeholder="검색"]', 'Enter');
  await expect(page).toHaveURL(/.*search/);
  await expect(page.locator('.search-result')).toContainText('서울');
});
```

---

## 6. 수락 체크리스트

### 6.1 백엔드

- [ ] 레코드 목록 조회 API 동작 (GET /api/v1/records)
- [ ] 단일 레코드 조회 API 동작 (GET /api/v1/records/{record_id})
- [ ] 레코드 필드 조회 API 동작 (GET /api/v1/records/{record_id}/fields)
- [ ] 검색 API 동작 (GET /api/v1/search)
- [ ] 자동 완성 API 동작 (GET /api/v1/search/suggest)
- [ ] JSON 내보내기 API 동작 (GET /api/v1/export/json)
- [ ] MARCXML 내보내기 API 동작 (GET /api/v1/export/marcxml)
- [ ] 404 에러 처리 (존재하지 않는 레코드)
- [ ] 400 에러 처리 (잘못된 페이지 번호)
- [ ] 422 에러 처리 (유효하지 않은 레코드 ID)

### 6.2 프론트엔드

- [ ] RecordList 컴포넌트 렌더링
- [ ] RecordDetail 컴포넌트 렌더링
- [ ] SearchBar 컴포넌트 렌더링
- [ ] Pagination 컴포넌트 렌더링
- [ ] ExportButton 컴포넌트 렌더링
- [ ] 홈 페이지 라우팅 (/)
- [ ] 레코드 상세 페이지 라우팅 (/records/:id)
- [ ] 검색 페이지 라우팅 (/search)

### 6.3 품질

- [ ] 테스트 커버리지 >= 85%
- [ ] ruff 검사 통과 (0 에러, 0 경고)
- [ ] mypy 검사 통과 (0 에러)
- [ ] eslint 검사 통과 (0 에러)
- [ ] prettier 포맷 적용
- [ ] 성능 기준 달성 (P95 < 100ms)

### 6.4 보안

- [ ] SQL 인젝션 방지 검증
- [ ] CORS 설정 검증
- [ ] 입력 검증 (Pydantic) 검증

---

## 7. 추적성

**관련 SPEC**:
- SPEC-KORMARC-PARSER-001: KORMARC 파싱 라이브러리

**프로젝트 문서**:
- `.moai/project/product.md`: 비즈니스 요구사항
- `.moai/project/tech.md`: 기술 스택 및 아키텍처

**구현 태그**:
- `TAG:SPEC-WEB-001:API`: 백엔드 API 구현
- `TAG:SPEC-WEB-001:UI`: 프론트엔드 UI 구현
- `TAG:SPEC-WEB-001:SEARCH`: 검색 기능 구현
- `TAG:SPEC-WEB-001:EXPORT`: 내보내기 기능 구현
- `TAG:SPEC-WEB-001:TEST`: 테스트 구현

---

## 8. 완료 정의 (Definition of Done)

SPEC-WEB-001은 다음 조건이 모두 충족될 때 완료된 것으로 간주합니다:

1. **기능 완료**:
   - 모든 Primary Goals 작업 완료 (Task 1-5)
   - 모든 API 엔드포인트 동작 확인
   - 모든 UI 컴포넌트 렌더링 확인

2. **품질 게이트 통과**:
   - 테스트 커버리지 >= 85%
   - 모든 linting 검사 통과
   - 모든 타입 체킹 통과
   - 보안 검증 항목 통과

3. **성능 기준 달성**:
   - API 응답 시간 P95 < 100ms
   - 동시 사용자 10명 지원

4. **문서화 완료**:
   - API 문서 작성
   - README.md 업데이트
   - 사용자 가이드 작성

5. **검토 완료**:
   - 코드 리뷰 완료
   - SPEC 검토 완료
   - 사용자 수락 테스트 통과
