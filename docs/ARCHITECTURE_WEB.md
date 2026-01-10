# KORMARC Web API 아키텍처

**버전**: 1.0.0
**기준일**: 2026-01-11
**SPEC**: SPEC-WEB-001

## 개요

KORMARC Web API는 100개의 프로토타입 KORMARC 레코드를 제공하는 읽기 전용 REST API입니다. FastAPI 프레임워크를 기반으로 하며, 계층형 아키텍처 패턴을 따릅니다.

### 설계 원칙

1. **단순성**: 읽기 전용 API로 복잡도 최소화
2. **성능**: SQLite FTS5로 빠른 검색 제공
3. **확장성**: 모듈화된 구조로 향후 기능 추가 용이
4. **테스트 가능성**: 계층 분리로 단위 테스트 지원
5. **타입 안전성**: Pydantic 모델로 데이터 검증 보장

---

## 시스템 아키텍처

### 전체 구조

```
┌─────────────────┐
│   Frontend      │ (향후 구현)
│   (React)       │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────────────────────────────┐
│          FastAPI Application            │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │         API Layer                 │ │
│  │  (routes: records, search)        │ │
│  └──────────────┬────────────────────┘ │
│                 │                       │
│  ┌──────────────▼────────────────────┐ │
│  │       Schema Layer                │ │
│  │  (Pydantic models: validation)    │ │
│  └──────────────┬────────────────────┘ │
│                 │                       │
│  ┌──────────────▼────────────────────┐ │
│  │      Repository Layer             │ │
│  │  (data access: RecordRepository)  │ │
│  └──────────────┬────────────────────┘ │
│                 │                       │
│  ┌──────────────▼────────────────────┐ │
│  │      Database Layer               │ │
│  │  (SQLite connection management)   │ │
│  └──────────────┬────────────────────┘ │
└─────────────────┼───────────────────────┘
                  │
                  ↓
         ┌────────────────┐
         │ SQLite Database│
         │  (FTS5 index)  │
         └────────────────┘
```

### 계층별 역할

**API Layer (routes/)**:
- HTTP 요청 처리 및 라우팅
- 쿼리 파라미터 검증
- HTTP 응답 생성
- 에러 처리 및 상태 코드 관리

**Schema Layer (schemas/)**:
- 요청/응답 데이터 모델 정의
- Pydantic을 통한 자동 검증
- 타입 힌트 제공
- API 문서 자동 생성 지원

**Repository Layer (data/repositories.py)**:
- 데이터 액세스 로직 캡슐화
- SQL 쿼리 실행
- 도메인 모델 변환
- 비즈니스 로직과 데이터 액세스 분리

**Database Layer (data/database.py)**:
- SQLite 연결 관리
- 연결 풀링 (향후 추가 가능)
- 트랜잭션 관리 (읽기 전용)

---

## 디렉터리 구조

```
src/kormarc_web/
├── __init__.py              # 패키지 초기화
├── main.py                  # FastAPI 애플리케이션 진입점
│
├── api/                     # API 계층
│   ├── __init__.py
│   └── routes/              # 라우트 모듈
│       ├── __init__.py
│       ├── records.py       # 레코드 조회 엔드포인트
│       └── search.py        # 검색 엔드포인트
│
├── schemas/                 # 스키마 계층
│   ├── __init__.py
│   ├── record.py            # 레코드 스키마 정의
│   └── pagination.py        # 페이지네이션 스키마
│
├── data/                    # 데이터 계층
│   ├── __init__.py
│   ├── database.py          # 데이터베이스 연결 관리
│   └── repositories.py      # 데이터 액세스 객체
│
└── services/                # 비즈니스 로직 (향후 확장)
    └── __init__.py

tests/                       # 테스트 코드
├── conftest.py              # pytest 설정 및 픽스처
├── test_api/                # API 계층 테스트
│   ├── test_records.py
│   └── test_search.py
└── test_data/               # 데이터 계층 테스트
    └── test_repositories.py
```

---

## 주요 컴포넌트

### 1. FastAPI 애플리케이션 (main.py)

**역할**:
- FastAPI 인스턴스 생성 및 설정
- 라우터 등록
- CORS 미들웨어 설정
- 전역 예외 핸들러 (향후 추가)

**핵심 코드**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="KORMARC Web API",
    description="Read-only API for KORMARC record browsing and search",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(records.router)
app.include_router(search.router)
```

**설계 결정**:
- CORS 활성화: 프론트엔드 통합 지원
- 버전 정보 명시: API 버전 관리 준비
- 모듈화된 라우터: 기능별 엔드포인트 분리

---

### 2. 레코드 API 라우터 (api/routes/records.py)

**역할**:
- 레코드 조회 엔드포인트 제공
- 페이지네이션 파라미터 검증
- HTTP 에러 처리

**엔드포인트**:
1. `GET /api/v1/records` - 레코드 목록 조회
2. `GET /api/v1/records/{record_id}` - 레코드 상세 조회

**핵심 로직**:
```python
@router.get("", response_model=PaginatedResponse[RecordResponse])
async def get_records(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    """Get paginated list of KORMARC records"""
    repo = RecordRepository()

    # 페이지네이션 계산
    offset = (page - 1) * size

    # 데이터 조회
    total = repo.get_total_count()
    records = repo.get_records(offset=offset, limit=size)

    return PaginatedResponse(
        items=[RecordResponse(**record) for record in records],
        total=total,
        page=page,
        size=size,
    )
```

**설계 결정**:
- Query 파라미터로 페이지네이션 제어
- Repository 패턴으로 데이터 액세스 캡슐화
- Pydantic 응답 모델로 타입 안전성 보장

---

### 3. 검색 API 라우터 (api/routes/search.py)

**역할**:
- FTS5 전문 검색 엔드포인트 제공
- 검색어 파라미터 처리
- 검색 결과 페이지네이션

**엔드포인트**:
1. `GET /api/v1/search` - 전문 검색

**핵심 로직**:
```python
@router.get("", response_model=PaginatedResponse[RecordResponse])
async def search_records(
    q: str = Query(default="", description="Search query"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    """Search KORMARC records using FTS5 full-text search"""
    repo = SearchRepository()

    offset = (page - 1) * size
    records, total = repo.search_records(query=q, offset=offset, limit=size)

    return PaginatedResponse(
        items=[RecordResponse(**record) for record in records],
        total=total,
        page=page,
        size=size,
    )
```

**설계 결정**:
- 빈 검색어 허용 (전체 레코드 반환)
- SearchRepository로 검색 로직 분리
- 레코드 조회와 동일한 응답 형식

---

### 4. 스키마 (schemas/)

#### RecordResponse
기본 레코드 정보 (목록용)

```python
class RecordResponse(BaseModel):
    id: str
    title: str
    author: str | None
    publisher: str | None
    pub_year: str | None
    isbn: str | None
    kdc: str | None
    language: str | None
```

#### RecordDetail
상세 레코드 정보 (상세 조회용)

```python
class RecordDetail(RecordResponse):
    pub_place: str | None
    description: str | None
    pages: str | None
    size: str | None
    subject: list[str]
    notes: list[str]
    marc_fields: list[MarcField]
```

#### PaginatedResponse
페이지네이션 응답

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
```

**설계 결정**:
- Optional 필드로 유연성 확보
- 제네릭 타입으로 재사용성 증가
- MARC 필드 원본 데이터 보존

---

### 5. 리포지토리 (data/repositories.py)

#### RecordRepository
레코드 데이터 액세스

**주요 메서드**:
```python
class RecordRepository:
    def get_total_count(self) -> int:
        """전체 레코드 수 조회"""

    def get_records(self, offset: int, limit: int) -> list[dict]:
        """페이지네이션된 레코드 목록 조회"""

    def get_record_by_id(self, record_id: str) -> dict | None:
        """ID로 레코드 조회"""
```

#### SearchRepository
검색 전용 리포지토리

**주요 메서드**:
```python
class SearchRepository:
    def search_records(self, query: str, offset: int, limit: int) -> tuple[list[dict], int]:
        """FTS5 검색 실행 및 결과 반환"""
```

**설계 결정**:
- 읽기 전용 메서드만 제공
- SQLite 연결은 메서드 내부에서 관리
- 딕셔너리 형태로 반환 (Pydantic 변환은 상위 계층에서)

---

### 6. 데이터베이스 (data/database.py)

**역할**:
- SQLite 연결 생성 및 관리
- 데이터베이스 파일 경로 관리

**핵심 함수**:
```python
def get_db_path() -> Path:
    """데이터베이스 파일 경로 반환"""
    return Path(__file__).parent.parent.parent / "kormarc_prototype_100.db"

def get_connection():
    """SQLite 연결 객체 생성"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
    return conn
```

**설계 결정**:
- 프로젝트 루트의 DB 파일 사용
- Row factory로 딕셔너리 접근 지원
- 읽기 전용 모드 (향후 추가 가능)

---

## 데이터 흐름

### 레코드 목록 조회 흐름

```
1. 클라이언트 요청
   GET /api/v1/records?page=1&size=20

2. FastAPI 라우터
   ↓ 쿼리 파라미터 검증 (Pydantic)

3. records.get_records() 핸들러
   ↓ offset 계산: (page - 1) * size

4. RecordRepository.get_records()
   ↓ SQL 쿼리 실행
   SELECT * FROM records LIMIT 20 OFFSET 0

5. SQLite 데이터베이스
   ↓ 결과 반환 (list[dict])

6. Pydantic 응답 모델
   ↓ RecordResponse 변환 및 검증

7. JSON 응답
   {
     "items": [...],
     "total": 100,
     "page": 1,
     "size": 20
   }
```

### 검색 흐름

```
1. 클라이언트 요청
   GET /api/v1/search?q=Python&page=1&size=20

2. FastAPI 라우터
   ↓ 검색어 및 파라미터 검증

3. search.search_records() 핸들러
   ↓ offset 계산

4. SearchRepository.search_records()
   ↓ FTS5 검색 쿼리 실행
   SELECT * FROM records_fts
   WHERE records_fts MATCH 'Python'
   LIMIT 20 OFFSET 0

5. SQLite FTS5 인덱스
   ↓ 전문 검색 실행 및 결과 반환

6. Pydantic 응답 모델
   ↓ RecordResponse 변환

7. JSON 응답
   {
     "items": [...],
     "total": 15,
     "page": 1,
     "size": 20
   }
```

---

## 데이터베이스 스키마

### records 테이블

```sql
CREATE TABLE records (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    publisher TEXT,
    pub_year TEXT,
    pub_place TEXT,
    isbn TEXT,
    kdc TEXT,
    language TEXT,
    description TEXT,
    pages TEXT,
    size TEXT,
    subject TEXT,  -- JSON 배열
    notes TEXT,    -- JSON 배열
    marc_data TEXT -- 전체 MARC 데이터 (JSON)
);
```

### records_fts 테이블 (FTS5 가상 테이블)

```sql
CREATE VIRTUAL TABLE records_fts USING fts5(
    title,
    author,
    publisher,
    subject,
    description,
    content='records',
    content_rowid='rowid'
);
```

**인덱스 전략**:
- FTS5로 전문 검색 성능 최적화
- 주요 텍스트 필드만 인덱싱
- content 옵션으로 원본 테이블 연결

---

## 성능 최적화

### 현재 구현

1. **SQLite FTS5 사용**
   - 전문 검색 성능 향상
   - 인덱스 기반 빠른 조회

2. **페이지네이션**
   - LIMIT/OFFSET으로 메모리 사용 최소화
   - 한 번에 최대 100개 레코드만 반환

3. **Row Factory 활용**
   - 딕셔너리 접근으로 코드 간결화
   - 자동 타입 변환

### 향후 개선 사항

1. **연결 풀링**
   - SQLAlchemy 또는 aiosqlite 도입
   - 비동기 데이터베이스 액세스

2. **캐싱**
   - Redis 또는 메모리 캐시로 자주 조회되는 레코드 캐싱
   - 전체 레코드 수 캐싱

3. **인덱스 추가**
   - `kdc` 필드에 인덱스 추가 (분류별 조회)
   - `pub_year` 필드 인덱스 (연도별 필터링)

---

## 보안 고려사항

### 현재 구현

1. **SQL 인젝션 방지**
   - Parameterized 쿼리 사용
   - 사용자 입력 검증 (Pydantic)

2. **CORS 제한**
   - 허용 오리진 명시적 설정
   - 프로덕션 환경에서는 실제 도메인만 허용

3. **입력 검증**
   - 페이지네이션 파라미터 범위 제한
   - 레코드 ID 형식 검증

### 향후 추가 예정

1. **속도 제한**
   - slowapi 또는 redis-ratelimit 도입
   - IP 기반 요청 제한

2. **로깅 및 모니터링**
   - 구조화된 로깅 (structlog)
   - 접근 로그 기록

3. **입력 Sanitization**
   - XSS 방지를 위한 HTML 이스케이프
   - 검색어 길이 제한

---

## 테스트 전략

### 단위 테스트

**Repository 테스트**:
```python
def test_get_records():
    repo = RecordRepository()
    records = repo.get_records(offset=0, limit=10)
    assert len(records) <= 10
    assert all('id' in r for r in records)
```

**API 테스트**:
```python
def test_get_records_endpoint(test_client):
    response = test_client.get("/api/v1/records?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data['page'] == 1
    assert len(data['items']) <= 10
```

### 테스트 커버리지

- **현재 커버리지**: 95.68%
- **목표**: 90% 이상 유지
- **주요 커버 영역**:
  - API 엔드포인트 (100%)
  - 리포지토리 메서드 (100%)
  - 스키마 검증 (95%)

### CI/CD 통합

```yaml
# .github/workflows/test.yml
name: Test Backend

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e .[dev]
      - run: pytest --cov=src/kormarc_web --cov-report=xml
      - run: ruff check src/
      - run: mypy src/
```

---

## 배포 아키텍처 (향후)

### 개발 환경

```
┌────────────┐
│ Developer  │
│   Machine  │
└─────┬──────┘
      │
      ↓
┌─────────────┐
│  uvicorn    │ (개발 서버)
│  --reload   │
└─────┬───────┘
      │
      ↓
┌─────────────┐
│   SQLite    │
│    (local)  │
└─────────────┘
```

### 프로덕션 환경 (예정)

```
┌──────────────┐
│    Nginx     │ (리버스 프록시)
│  (SSL/TLS)   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Gunicorn   │ (WSGI 서버)
│  + Uvicorn   │ (4 workers)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│  FastAPI App │ (컨테이너)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   SQLite     │ (볼륨 마운트)
│  (ReadOnly)  │
└──────────────┘
```

---

## 확장 계획

### Phase 2: 프론트엔드 통합

- React 프론트엔드 구현
- TanStack Query로 서버 상태 관리
- 반응형 UI 컴포넌트

### Phase 3: 고급 기능

- 레코드 내보내기 (JSON, MARCXML)
- 검색어 자동완성
- 통계 대시보드

### Phase 4: 인프라

- Docker 컨테이너화
- CI/CD 파이프라인
- 모니터링 및 로깅

---

## 관련 문서

- **[API 레퍼런스](API_WEB.md)** - REST API 상세 명세
- **[SPEC 문서](../.moai/specs/SPEC-WEB-001/spec.md)** - 요구사항 및 설계
- **[README](../README.md)** - 프로젝트 개요 및 빠른 시작

---

**문서 버전**: 1.0.0
**최종 업데이트**: 2026-01-11
**작성자**: 지니 (SPEC-WEB-001 구현팀)
