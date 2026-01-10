---
id: SPEC-WEB-001
version: "1.0.0"
status: "draft"
created: "2026-01-11"
updated: "2026-01-11"
author: "지니"
priority: "HIGH"
---

## HISTORY

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-01-11 | 지니 | KORMARC 웹 애플리케이션 초기 명세서 작성 (Playwright 스크래핑 및 국립중앙도서관 API 통합 포함) |

---

# SPEC-WEB-001: KORMARC 웹 애플리케이션 - 노원구 시방서 기반 도서정보 입력 시스템

## 개요 (Overview)

### 목적

이 웹 애플리케이션은 사용자가 도서 정보를 웹 브라우저에서 직접 입력하여 노원구 시방서 규칙을 준수하는 KORMARC 레코드를 생성할 수 있도록 지원합니다. DB에 ISBN 정보가 없는 경우, Playwright를 활용하여 국립중앙도서관 웹사이트에서 자동으로 도서 정보를 수집하고, 향후 국립중앙도서관 오픈 API가 연동되면 API를 우선 사용하도록 설계되었습니다.

### 배경

- 기존 Python CLI 기반 KORMARC 생성기는 기술적 숙련도가 필요하여 사용성이 제한적
- 웹 기반 UI를 통해 비개발자 사용자도 쉽게 접근 가능
- 노원구 시방서의 040 필드 특수 규칙을 자동 검증
- ISBN 정보 부재 시 자동 데이터 수집으로 사용자 편의성 극대화
- 국립중앙도서관 API 연동 준비를 통한 향후 확장성 확보

### 핵심 기능

1. **도서 정보 입력 폼**: ISBN, 제목, 저자, 출판사, 발행년 등 7개 필드 입력
2. **자동 ISBN 검증**: 체크섬 알고리즘 기반 실시간 검증
3. **KORMARC 레코드 생성**: KORMARCBuilder 통합으로 JSON/XML 생성
4. **5단계 검증 시스템**: Tier 1~5 검증 결과 시각화
5. **Playwright 스크래핑**: 국립중앙도서관에서 ISBN 기반 도서 정보 자동 수집
6. **국립중앙도서관 API 통합 준비**: API 우선 정책 및 fallback 전략
7. **다운로드/복사 기능**: JSON, XML 형식 내보내기

---

## 기술 스택 (Technology Stack)

### Frontend

- **프레임워크**: Next.js 15.1+ (App Router)
- **UI 라이브러리**: React 19.0+
- **타입 시스템**: TypeScript 5.7+
- **스타일링**: Tailwind CSS 4.0+, Shadcn UI (latest)
- **폼 관리**: React Hook Form 7.54+
- **유효성 검증**: Zod 3.24+
- **HTTP 클라이언트**: fetch API (Next.js 내장)

### Backend

- **프레임워크**: FastAPI 0.115+
- **비동기 런타임**: uvicorn[standard] with asyncio
- **데이터 검증**: Pydantic 2.9+
- **데이터베이스**: aiosqlite 0.20+ (비동기 SQLite)
- **웹 스크래핑**: Playwright 1.48+ (Python)
- **KORMARC 생성**: 기존 KORMARCBuilder 통합

### 개발 환경

- **Python**: 3.12+
- **Node.js**: 20.x LTS
- **패키지 관리**: poetry (Python), npm (Node.js)

---

## 아키텍처 (Architecture)

### Client-Server 구조

```
┌─────────────────────────────────────────────┐
│           Next.js Frontend (Client)         │
│  ┌─────────────────────────────────────┐   │
│  │ BookInfo Form (React Hook Form)    │   │
│  │  - ISBN, 제목, 저자, 출판사, 발행년 │   │
│  └─────────────────────────────────────┘   │
│                    ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ Validation Layer (Zod)              │   │
│  │  - ISBN 체크섬 검증                  │   │
│  │  - 필수 필드 검증                    │   │
│  └─────────────────────────────────────┘   │
│                    ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ API Integration                     │   │
│  │  - POST /api/kormarc/build          │   │
│  │  - POST /api/kormarc/validate       │   │
│  │  - GET /api/book/search (스크래핑)   │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    ▼ HTTPS
┌─────────────────────────────────────────────┐
│          FastAPI Backend (Server)           │
│  ┌─────────────────────────────────────┐   │
│  │ API Endpoints                       │   │
│  │  - /api/kormarc/build (생성)         │   │
│  │  - /api/kormarc/validate (검증)      │   │
│  │  - /api/book/search (ISBN 조회)      │   │
│  └─────────────────────────────────────┘   │
│                    ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ Data Collection Layer               │   │
│  │  ┌─────────────────────────────┐    │   │
│  │  │ 1. 로컬 DB 조회 (SQLite)    │    │   │
│  │  └─────────────────────────────┘    │   │
│  │           ▼ (없으면)                 │   │
│  │  ┌─────────────────────────────┐    │   │
│  │  │ 2. 국립중앙도서관 API 시도   │    │   │
│  │  │    (향후 구현)               │    │   │
│  │  └─────────────────────────────┘    │   │
│  │           ▼ (실패 시)                │   │
│  │  ┌─────────────────────────────┐    │   │
│  │  │ 3. Playwright 스크래핑       │    │   │
│  │  │    (국립중앙도서관 웹사이트)  │    │   │
│  │  └─────────────────────────────┘    │   │
│  └─────────────────────────────────────┘   │
│                    ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ KORMARCBuilder Integration          │   │
│  │  - BookInfo → KORMARC 변환           │   │
│  │  - 5단계 검증 (Tier 1-5)             │   │
│  └─────────────────────────────────────┘   │
│                    ▼                         │
│  ┌─────────────────────────────────────┐   │
│  │ Database (SQLite)                   │   │
│  │  - books 테이블 (ISBN, metadata)     │   │
│  │  - records 테이블 (KORMARC)          │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 컴포넌트 구조

**Frontend (Next.js)**

```
app/
├── layout.tsx                 # 루트 레이아웃
├── page.tsx                   # 홈페이지 (도서 입력 폼)
├── components/
│   ├── BookInfoForm.tsx       # 도서 정보 입력 폼
│   ├── ISBNInput.tsx          # ISBN 입력 + 실시간 검증
│   ├── ValidationStatus.tsx   # 5단계 검증 상태 표시
│   ├── KORMARCPreview.tsx     # JSON/XML 미리보기
│   └── ExportButtons.tsx      # 다운로드/복사 버튼
├── api/
│   └── proxy/route.ts         # FastAPI로 프록시
└── lib/
    ├── types.ts               # TypeScript 타입 정의
    ├── validators.ts          # Zod 스키마
    └── api-client.ts          # API 호출 함수
```

**Backend (FastAPI)**

```
backend/
├── main.py                    # FastAPI 앱 진입점
├── routers/
│   ├── kormarc.py             # KORMARC 생성/검증 엔드포인트
│   └── books.py               # 도서 정보 조회 엔드포인트
├── services/
│   ├── kormarc_service.py     # KORMARC 생성 비즈니스 로직
│   ├── scraper_service.py     # Playwright 스크래핑 로직
│   └── api_service.py         # 국립중앙도서관 API 통합 (향후)
├── models/
│   ├── book_info.py           # Pydantic 모델 (BookInfo)
│   └── kormarc_record.py      # KORMARC 레코드 모델
├── db/
│   ├── database.py            # SQLite 연결 및 세션
│   └── repositories.py        # DB CRUD 작업
└── utils/
    ├── isbn_validator.py      # ISBN 체크섬 검증
    └── playwright_helper.py   # Playwright 헬퍼 함수
```

---

## 데이터 모델 (Data Models)

### BookInfo (Frontend & Backend)

**TypeScript (Frontend)**

```typescript
interface BookInfo {
  isbn: string;           // ISBN-13 (13자리)
  title: string;          // 도서 제목
  author: string;         // 저자
  publisher: string;      // 출판사
  publicationYear: number; // 발행년 (YYYY)
  edition?: string;       // 판차 (선택)
  seriesTitle?: string;   // 총서명 (선택)
}
```

**Python (Backend - Pydantic)**

```python
class BookInfo(BaseModel):
    isbn: str = Field(pattern=r"^\d{13}$")
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    publication_year: int = Field(ge=1900, le=2100)
    edition: Optional[str] = None
    series_title: Optional[str] = None
```

### KORMARC Record

```python
class KORMARCRecord(BaseModel):
    leader: str
    control_fields: Dict[str, str]  # 001, 003, 005, 008
    data_fields: List[DataField]    # 020 (ISBN), 040 (노원구), 245 (제목) 등
    validation_results: ValidationResults
```

### Scraping Result

```python
class ScrapingResult(BaseModel):
    success: bool
    isbn: str
    book_info: Optional[BookInfo] = None
    source: Literal["database", "api", "scraping"]
    error_message: Optional[str] = None
    collected_at: datetime
```

---

## API 엔드포인트 (API Endpoints)

### POST /api/kormarc/build

**설명**: BookInfo를 받아 KORMARC 레코드 생성

**Request Body** (JSON):

```json
{
  "isbn": "9791162233149",
  "title": "Python 프로그래밍",
  "author": "박응용",
  "publisher": "한빛미디어",
  "publicationYear": 2025
}
```

**Response** (JSON):

```json
{
  "status": "success",
  "kormarc": {
    "json": { "leader": "...", "fields": [...] },
    "xml": "<record>...</record>"
  },
  "validation": {
    "tier1": { "passed": true, "errors": [] },
    "tier2": { "passed": true, "errors": [] },
    "tier3": { "passed": true, "warnings": [] },
    "tier4": { "passed": true, "warnings": [] },
    "tier5": { "passed": true, "errors": [] }
  }
}
```

### POST /api/kormarc/validate

**설명**: KORMARC 레코드 5단계 검증

**Request Body** (JSON): KORMARC JSON

**Response** (JSON): ValidationResults

### GET /api/book/search?isbn={isbn}

**설명**: ISBN으로 도서 정보 조회 (로컬 DB → API → Playwright 순서)

**Query Parameters**:

- `isbn`: ISBN-13 (필수)

**Response** (JSON):

```json
{
  "success": true,
  "source": "scraping",
  "book_info": {
    "isbn": "9788970509143",
    "title": "데이터베이스 설계",
    "author": "김영철",
    "publisher": "한국방송통신대학교출판부",
    "publicationYear": 2015
  },
  "collected_at": "2026-01-11T10:30:00Z"
}
```

### GET /api/health

**설명**: 서버 상태 확인

**Response** (JSON):

```json
{
  "status": "ok",
  "playwright_available": true,
  "database_connected": true
}
```

---

## Playwright 스크래핑 (Web Scraping)

### 국립중앙도서관 스크래핑 전략

**목표 사이트**: https://www.nl.go.kr/

**스크래핑 플로우**:

1. **ISBN 검색 페이지 접속**: Playwright 브라우저 시작
2. **검색어 입력**: ISBN을 검색창에 입력
3. **검색 결과 대기**: 검색 결과 페이지 로딩 대기 (waitForSelector)
4. **도서 정보 추출**:
   - 제목 (title)
   - 저자 (author)
   - 출판사 (publisher)
   - 발행년 (publicationYear)
5. **데이터 정제**: HTML 태그 제거, 공백 정리
6. **DB 저장**: 추출된 정보를 로컬 SQLite DB에 캐싱
7. **브라우저 종료**: 리소스 정리

**Playwright 설정**:

```python
from playwright.async_api import async_playwright

async def scrape_book_info(isbn: str) -> Optional[BookInfo]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            # 국립중앙도서관 검색
            await page.goto("https://www.nl.go.kr/")
            await page.fill('input[name="kwd"]', isbn)
            await page.click('button[type="submit"]')
            await page.wait_for_selector('.book-item', timeout=10000)

            # 도서 정보 추출
            title = await page.locator('.book-title').inner_text()
            author = await page.locator('.book-author').inner_text()
            publisher = await page.locator('.book-publisher').inner_text()
            year_text = await page.locator('.book-year').inner_text()
            year = int(re.search(r'\d{4}', year_text).group())

            return BookInfo(
                isbn=isbn,
                title=title.strip(),
                author=author.strip(),
                publisher=publisher.strip(),
                publication_year=year
            )
        except Exception as e:
            logger.error(f"Scraping failed for ISBN {isbn}: {e}")
            return None
        finally:
            await browser.close()
```

### Rate Limiting 및 오류 처리

- **Rate Limiting**: 1분당 최대 10회 스크래핑 (Redis 또는 메모리 기반)
- **Timeout**: 10초 내 응답 없으면 실패 처리
- **User-Agent Rotation**: 차단 방지를 위한 User-Agent 변경
- **Retry 전략**: 최대 3회 재시도 (exponential backoff)
- **오류 로깅**: 실패 시 상세 로그 기록

---

## 국립중앙도서관 API 연동 준비 (API Integration)

### API 우선 정책 (API-First Policy)

도서 정보 수집 시 다음 순서로 시도:

1. **로컬 DB 조회**: 이미 수집된 ISBN이면 즉시 반환
2. **국립중앙도서관 오픈 API 호출**: API 키 발급 후 우선 사용
3. **Playwright 스크래핑 Fallback**: API 실패 시 스크래핑

### API 엔드포인트 (예상)

**API Base URL** (향후 설정):

```
https://www.nl.go.kr/openapi/search
```

**Request Example**:

```http
GET /openapi/search?isbn=9788970509143&key=YOUR_API_KEY
```

**Response Example**:

```json
{
  "status": "success",
  "result": {
    "title": "데이터베이스 설계",
    "author": "김영철",
    "publisher": "한국방송통신대학교출판부",
    "pub_year": "2015"
  }
}
```

### API 통합 구현 (향후)

```python
async def fetch_book_from_api(isbn: str) -> Optional[BookInfo]:
    api_key = os.getenv("NLK_API_KEY")
    if not api_key:
        return None  # API 키 없으면 스킵

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.nl.go.kr/openapi/search",
                params={"isbn": isbn, "key": api_key},
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return parse_api_response(data)
    except Exception as e:
        logger.warning(f"API call failed: {e}")
        return None  # Fallback to scraping
```

---

## EARS 요구사항 (Requirements)

### 1. 항상성 요구사항 (Ubiquitous Requirements)

- **R-001**: 시스템은 **항상** 웹 기반 사용자 인터페이스를 제공해야 한다
  - **WHY**: 비개발자 사용자도 쉽게 접근 가능
  - **IMPACT**: CLI 대비 사용성 70% 향상

- **R-002**: 시스템은 **항상** 입력된 ISBN의 체크섬을 검증해야 한다
  - **WHY**: 잘못된 ISBN 입력으로 인한 오류 방지
  - **IMPACT**: 데이터 무결성 보장

- **R-003**: 시스템은 **항상** 노원구 시방서의 040 필드 규칙을 검증해야 한다
  - **WHY**: 노원구 특수 요구사항 준수
  - **IMPACT**: 규칙 위반 레코드 0%

- **R-004**: 시스템은 **항상** 생성된 KORMARC 레코드를 JSON과 XML 형식으로 제공해야 한다
  - **WHY**: 다양한 시스템 통합 지원
  - **IMPACT**: 상호운용성 확보

### 2. 이벤트 기반 요구사항 (Event-Driven Requirements)

- **R-005**: **WHEN** 사용자가 도서 정보를 제출하면 **THEN** KORMARC 레코드를 생성해야 한다
  - **WHY**: 즉각적인 변환 제공
  - **IMPACT**: 사용자 대기 시간 최소화

- **R-006**: **WHEN** ISBN이 로컬 DB에 존재하지 않으면 **THEN** 국립중앙도서관 API를 시도하고, 실패 시 Playwright로 스크래핑해야 한다
  - **WHY**: 자동 데이터 수집으로 사용자 입력 부담 감소
  - **IMPACT**: 수동 입력 시간 80% 절감

- **R-007**: **WHEN** 스크래핑이 성공하면 **THEN** 수집된 정보를 로컬 DB에 저장해야 한다
  - **WHY**: 동일 ISBN 재요청 시 속도 향상
  - **IMPACT**: 중복 스크래핑 방지

- **R-008**: **WHEN** 검증이 실패하면 **THEN** 구체적인 오류 메시지를 사용자에게 표시해야 한다
  - **WHY**: 사용자 수정 가능성 제공
  - **IMPACT**: 재시도율 60% 감소

- **R-009**: **WHEN** KORMARC 생성이 성공하면 **THEN** JSON/XML 다운로드 옵션을 제공해야 한다
  - **WHY**: 사용자 편의성 극대화
  - **IMPACT**: 후속 작업 효율 향상

### 3. 상태 기반 요구사항 (State-Driven Requirements)

- **R-010**: **IF** 사용자가 ISBN을 입력 중이면 **THEN** 실시간 형식 검증을 수행해야 한다
  - **WHY**: 즉각적인 피드백 제공
  - **IMPACT**: 입력 오류 조기 발견

- **R-011**: **IF** 필수 필드가 비어있으면 **THEN** "KORMARC 생성" 버튼을 비활성화해야 한다
  - **WHY**: 불완전한 데이터 제출 방지
  - **IMPACT**: 서버 부하 감소

- **R-012**: **IF** KORMARC 미리보기가 표시되면 **THEN** 040 필드를 노란색으로 하이라이트해야 한다
  - **WHY**: 노원구 규칙 확인 용이성
  - **IMPACT**: 사용자 인지 향상

### 4. 선택적 요구사항 (Optional Requirements)

- **R-013**: **가능하면** 사용자가 입력 중인 데이터를 자동 저장하는 옵션을 제공한다
  - **WHY**: 브라우저 종료 시 데이터 손실 방지
  - **IMPACT**: 사용자 경험 개선

- **R-014**: **가능하면** ISBN 파일 업로드를 통한 일괄 처리를 지원한다
  - **WHY**: 대량 작업 효율성
  - **IMPACT**: 처리 시간 90% 단축

### 5. 금지 동작 (Unwanted Behaviors)

- **R-015**: 시스템은 체크섬이 올바르지 않은 ISBN을 **허용하지 않아야 한다**
  - **WHY**: 데이터 무결성 보장
  - **IMPACT**: 잘못된 레코드 생성 방지

- **R-016**: 시스템은 040 필드 규칙을 위반하는 KORMARC 레코드 생성을 **허용하지 않아야 한다**
  - **WHY**: 노원구 시방서 준수
  - **IMPACT**: 규칙 위반 0%

- **R-017**: 시스템은 내부 오류 메시지(스택 트레이스)를 사용자에게 **노출하지 않아야 한다**
  - **WHY**: 보안 취약점 방지
  - **IMPACT**: 정보 유출 차단

---

## 제약사항 (Constraints)

### 기술적 제약사항

- **브라우저 호환성**: Chrome, Firefox, Safari, Edge 최신 2개 버전
- **응답 시간**: P95 < 200ms (KORMARC 생성 API)
- **스크래핑 시간**: P95 < 5초 (Playwright 스크래핑)
- **동시 사용자**: 최소 100명 동시 접속 지원
- **데이터베이스**: SQLite (초기), PostgreSQL (향후 확장 고려)

### 보안 제약사항

- **CORS 정책**: Next.js 도메인만 FastAPI 접근 허용
- **Rate Limiting**: API 요청 1분당 60회 (사용자당)
- **입력 검증**: 모든 사용자 입력 XSS 방지 이스케이핑
- **Secrets 관리**: 국립중앙도서관 API 키는 환경 변수로 관리

### 성능 제약사항

- **First Contentful Paint**: < 1.5초
- **Time to Interactive**: < 3.0초
- **API 응답 시간**: 평균 < 150ms

---

## 품질 속성 (Quality Attributes)

### 성능 (Performance)

- **KORMARC 생성**: P50 < 100ms, P95 < 200ms
- **스크래핑**: P50 < 3초, P95 < 5초
- **페이지 로딩**: First Contentful Paint < 1.5초

### 테스트 커버리지 (Test Coverage)

- **백엔드**: ≥85% (pytest)
- **프론트엔드**: ≥80% (Vitest)
- **E2E**: 핵심 사용자 플로우 100% (Playwright E2E)

### 접근성 (Accessibility)

- **WCAG 2.1 AA 준수**
- **키보드 네비게이션 지원**
- **스크린 리더 호환성**

### 보안 (Security)

- **OWASP Top 10 대응**
- **입력 검증 및 이스케이핑**
- **HTTPS 강제**

---

## 추적성 태그 (Traceability Tags)

- `#SPEC-WEB-001`
- `#KORMARC`
- `#Next.js`
- `#FastAPI`
- `#Playwright`
- `#NoSQL-Spec`
- `#Web-Application`
- `#TDD`
