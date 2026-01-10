---
id: SPEC-WEB-001
version: "1.0.0"
status: "draft"
created: "2026-01-11"
updated: "2026-01-11"
---

# SPEC-WEB-001 구현 계획

## 1. 구현 계획 개요

### 1.1 목표

KORMARC 레코드 100개에 대한 읽기 전용 웹 인터페이스를 구현합니다.

### 1.2 방법론

- **개발 방식**: TDD (Test-Driven Development)
- **우선순위**: Primary Goals → Secondary Goals → Optional Goals
- **품질 기준**: TRUST 5 프레임워크 준수

### 1.3 범위

**포함**:
- FastAPI 백엔드 API (9개 엔드포인트)
- React 프론트엔드 UI (레코드 목록, 상세, 검색)
- JSON/MARCXML 내보내기 기능

**제외**:
- 레코드 수정/삭제 기능
- 사용자 인증/권한 관리
- 외부 API 연동

---

## 2. 백엔드 아키텍처 (FastAPI)

### 2.1 디렉터리 구조

```
src/kormarc_web/
├── __init__.py
├── main.py                      # FastAPI 애플리케이션 진입점
├── config.py                    # 설정 관리 (환경 변수)
├── api/
│   ├── __init__.py
│   ├── dependencies.py          # 공통 의존성 (DB 세션, 페이지네이션)
│   └── routes/
│       ├── __init__.py
│       ├── records.py           # 레코드 조회 라우터
│       ├── search.py            # 검색 라우터
│       └── export.py            # 내보내기 라우터
├── services/
│   ├── __init__.py
│   ├── record_service.py        # 레코드 비즈니스 로직
│   └── search_service.py        # 검색 비즈니스 로직
├── data/
│   ├── __init__.py
│   ├── database.py              # SQLite 연결 관리
│   └── repositories.py          # 데이터 액세스 계층
├── schemas/
│   ├── __init__.py
│   ├── record.py                # RecordResponse, RecordDetail 스키마
│   ├── pagination.py            # PaginationParams, PaginatedResponse 스키마
│   └── search.py                # SearchResponse 스키마
└── tests/
    ├── __init__.py
    ├── conftest.py              # pytest fixtures
    ├── test_records.py          # 레코드 엔드포인트 테스트
    ├── test_search.py           # 검색 엔드포인트 테스트
    └── test_export.py           # 내보내기 엔드포인트 테스트
```

### 2.2 API 엔드포인트

**레코드 관리 (records.py)**:
1. `GET /api/v1/records` - 페이지네이션된 레코드 목록
2. `GET /api/v1/records/{record_id}` - 단일 레코드 상세
3. `GET /api/v1/records/{record_id}/fields` - 레코드의 모든 KORMARC 필드

**검색 (search.py)**:
4. `GET /api/v1/search` - 키워드 기반 전문 검색 (FTS5)
5. `GET /api/v1/search/suggest` - 자동 완성 검색어 제안

**내보내기 (export.py)**:
6. `GET /api/v1/export/json` - JSON 형식 내보내기
7. `GET /api/v1/export/marcxml` - MARCXML 형식 내보내기

**통계 (선택 사항)**:
8. `GET /api/v1/stats` - 통계 정보 (총 레코드 수, 인기 키워드)

### 2.3 데이터베이스 통합

**기존 라이브러리 재사용**:
- `kormarc` 라이브러리의 파싱 기능 활용
- `kormarc_prototype_100.db` SQLite 데이터베이스 연결

**연결 관리** (`database.py`):
```python
import sqlite3
from contextlib import contextmanager

DB_PATH = "kormarc_prototype_100.db"

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Dict-like access
    try:
        yield conn
    finally:
        conn.close()
```

**Repository 패턴** (`repositories.py`):
- `RecordRepository`: 레코드 CRUD 메서드
- `SearchRepository`: FTS5 전문 검색 메서드

---

## 3. 프론트엔드 구조 (React)

### 3.1 디렉터리 구조

```
web/
├── public/
│   └── index.html
├── src/
│   ├── App.tsx                  # 앱 진입점
│   ├── main.tsx                 # React 렌더링
│   ├── components/
│   │   ├── RecordList.tsx       # 레코드 목록 컴포넌트
│   │   ├── RecordCard.tsx       # 레코드 카드 컴포넌트
│   │   ├── RecordDetail.tsx     # 레코드 상세 컴포넌트
│   │   ├── SearchBar.tsx        # 검색 바 컴포넌트
│   │   ├── Pagination.tsx       # 페이지네이션 컴포넌트
│   │   └── ExportButton.tsx     # 내보내기 버튼 컴포넌트
│   ├── pages/
│   │   ├── Home.tsx             # 홈 페이지 (레코드 목록)
│   │   ├── RecordDetailPage.tsx # 레코드 상세 페이지
│   │   └── SearchPage.tsx       # 검색 결과 페이지
│   ├── hooks/
│   │   └── useRecords.ts        # TanStack Query 훅
│   ├── api/
│   │   └── client.ts            # Axios API 클라이언트
│   ├── types/
│   │   └── record.ts            # TypeScript 타입 정의
│   └── styles/
│       └── global.css           # Tailwind CSS 설정
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

### 3.2 주요 컴포넌트

**RecordList.tsx**:
- 레코드 목록 표시
- 페이지네이션 통합
- 검색 필터 적용

**RecordDetail.tsx**:
- 레코드 상세 정보 표시
- KORMARC 필드 전체 보기
- 내보내기 버튼 제공

**SearchBar.tsx**:
- 실시간 검색 입력
- 자동 완성 제안 (debounce 적용)

**Pagination.tsx**:
- 페이지 번호 표시 및 이동
- 이전/다음 버튼

**ExportButton.tsx**:
- JSON/MARCXML 내보내기 옵션
- 파일 다운로드 트리거

### 3.3 상태 관리

**TanStack Query 활용**:
```typescript
// hooks/useRecords.ts
import { useQuery } from '@tanstack/react-query';
import { fetchRecords } from '../api/client';

export function useRecords(page: number, size: number) {
  return useQuery({
    queryKey: ['records', page, size],
    queryFn: () => fetchRecords(page, size),
  });
}
```

**React Router 라우팅**:
```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/records/:id" element={<RecordDetailPage />} />
        <Route path="/search" element={<SearchPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 4. 작업 분해 (Task Breakdown)

### 4.1 Primary Goals (최우선 구현)

**Task 1: 백엔드 프로젝트 초기화**
- FastAPI 프로젝트 구조 생성
- `pyproject.toml` 설정 (의존성, 린터, 포맷터)
- SQLite 데이터베이스 연결 검증
- **TAG**: `TAG:SPEC-WEB-001:INIT`

**Task 2: 레코드 조회 API 구현**
- `GET /api/v1/records` 엔드포인트 (목록)
- `GET /api/v1/records/{record_id}` 엔드포인트 (상세)
- Pydantic 스키마 정의
- 단위 테스트 작성
- **TAG**: `TAG:SPEC-WEB-001:API:RECORDS`

**Task 3: 검색 API 구현**
- `GET /api/v1/search` 엔드포인트 (FTS5 검색)
- `GET /api/v1/search/suggest` 엔드포인트 (자동 완성)
- 검색 서비스 로직 구현
- 단위 테스트 작성
- **TAG**: `TAG:SPEC-WEB-001:API:SEARCH`

**Task 4: 프론트엔드 프로젝트 초기화**
- React + TypeScript + Vite 프로젝트 생성
- Tailwind CSS 설정
- TanStack Query 및 React Router 설정
- API 클라이언트 구성
- **TAG**: `TAG:SPEC-WEB-001:UI:INIT`

**Task 5: 프론트엔드 UI 구현**
- RecordList, RecordDetail 컴포넌트 구현
- SearchBar, Pagination 컴포넌트 구현
- 라우팅 설정 (Home, RecordDetailPage, SearchPage)
- **TAG**: `TAG:SPEC-WEB-001:UI:COMPONENTS`

### 4.2 Secondary Goals (2차 구현)

**Task 6: 내보내기 기능 구현**
- `GET /api/v1/export/json` 엔드포인트
- `GET /api/v1/export/marcxml` 엔드포인트
- ExportButton 컴포넌트 구현
- **TAG**: `TAG:SPEC-WEB-001:EXPORT`

**Task 7: 통합 테스트 작성**
- FastAPI TestClient를 사용한 API 통합 테스트
- 레코드 조회, 검색, 내보내기 시나리오 검증
- **TAG**: `TAG:SPEC-WEB-001:TEST:INTEGRATION`

**Task 8: E2E 테스트 작성 (선택)**
- Playwright를 사용한 E2E 테스트
- 사용자 시나리오 검증 (목록 조회, 검색, 상세 보기)
- **TAG**: `TAG:SPEC-WEB-001:TEST:E2E`

### 4.3 Optional Goals (선택 기능)

**Task 9: 통계 대시보드 구현**
- `GET /api/v1/stats` 엔드포인트
- 통계 정보 표시 컴포넌트
- **TAG**: `TAG:SPEC-WEB-001:STATS`

**Task 10: 다크 모드 지원**
- Tailwind CSS 다크 모드 설정
- 테마 토글 버튼 구현
- **TAG**: `TAG:SPEC-WEB-001:UI:DARKMODE`

**Task 11: MARCXML 미리보기**
- MARCXML 렌더링 컴포넌트
- 코드 하이라이팅
- **TAG**: `TAG:SPEC-WEB-001:UI:MARCXML`

---

## 5. 기술 스택

### 5.1 백엔드

**프레임워크 및 라이브러리**:
- `fastapi >= 0.115.0`: 웹 프레임워크
- `uvicorn >= 0.32.0`: ASGI 서버
- `python-multipart >= 0.0.9`: 파일 업로드 지원
- `pydantic >= 2.9.0`: 데이터 검증

**기존 라이브러리**:
- `kormarc >= 1.0.0`: KORMARC 파싱 (SPEC-KORMARC-PARSER-001)

**개발 도구**:
- `pytest >= 8.0.0`: 테스트 프레임워크
- `pytest-asyncio >= 0.24.0`: 비동기 테스트
- `ruff >= 0.8.0`: 린터 및 포맷터
- `mypy >= 1.13.0`: 타입 체킹

### 5.2 프론트엔드

**프레임워크 및 라이브러리**:
- `react >= 19.0.0`: UI 라이브러리
- `typescript >= 5.9.0`: 타입 안전성
- `tailwindcss >= 3.4.0`: CSS 프레임워크
- `@tanstack/react-query >= 5.0.0`: 서버 상태 관리
- `axios >= 1.7.0`: HTTP 클라이언트
- `react-router-dom >= 7.0.0`: 라우팅

**빌드 도구**:
- `vite >= 6.0.0`: 빌드 도구
- `@vitejs/plugin-react >= 4.3.0`: React 플러그인

**개발 도구**:
- `@playwright/test >= 1.50.0`: E2E 테스트 (선택)
- `eslint >= 9.0.0`: JavaScript 린터
- `prettier >= 3.4.0`: 코드 포맷터

### 5.3 데이터베이스

- **SQLite**: 기존 `kormarc_prototype_100.db`
- **FTS5**: 전문 검색 인덱스

---

## 6. 품질 기준 (TRUST 5)

### 6.1 Test-first (테스트 우선)

- **목표**: 테스트 커버리지 85% 이상
- **방법**: TDD 방식 (RED-GREEN-REFACTOR)
- **도구**: pytest (백엔드), Playwright (E2E)

### 6.2 Readable (가독성)

- **목표**: 명확한 변수명, 함수명 사용
- **방법**: 린터 검사 통과 (ruff, eslint)
- **도구**: ruff, prettier

### 6.3 Unified (일관성)

- **목표**: 코드 스타일 일관성
- **방법**: 자동 포맷터 적용
- **도구**: ruff, black, prettier

### 6.4 Secured (보안)

- **목표**: OWASP Top 10 기본 준수
- **방법**: 입력 검증 (Pydantic), SQL 인젝션 방지 (Parameterized 쿼리)
- **검증**: 보안 검토

### 6.5 Trackable (추적성)

- **목표**: 명확한 커밋 메시지
- **방법**: `TAG:SPEC-WEB-001:*` 태그 사용
- **검증**: Git 커밋 히스토리

---

## 7. 리스크 및 완화 방안

### 7.1 SQLite 동시 접속 제한

**리스크**: 읽기 전용이지만 동시 접속 시 성능 저하 가능

**완화 방안**:
- SQLite WAL 모드 활성화
- 읽기 전용 연결 사용
- 연결 풀링 고려 (필요 시)

### 7.2 CORS 설정 오류

**리스크**: 프론트엔드가 백엔드 API에 접근하지 못할 수 있음

**완화 방안**:
- FastAPI CORSMiddleware 설정
- 허용된 도메인 명시적 설정
- 개발 환경에서 테스트

### 7.3 FTS5 검색 성능

**리스크**: 검색 쿼리가 느릴 수 있음

**완화 방안**:
- 인덱스 활용 확인
- 페이지네이션 적용
- 검색 결과 캐싱 고려

---

## 8. 추적성

**관련 SPEC**:
- SPEC-KORMARC-PARSER-001: KORMARC 파싱 라이브러리

**프로젝트 문서**:
- `.moai/project/product.md`: 비즈니스 요구사항
- `.moai/project/tech.md`: 기술 스택 및 아키텍처

**구현 태그**:
- `TAG:SPEC-WEB-001:INIT`: 프로젝트 초기화
- `TAG:SPEC-WEB-001:API:RECORDS`: 레코드 API 구현
- `TAG:SPEC-WEB-001:API:SEARCH`: 검색 API 구현
- `TAG:SPEC-WEB-001:UI:INIT`: 프론트엔드 초기화
- `TAG:SPEC-WEB-001:UI:COMPONENTS`: UI 컴포넌트 구현
- `TAG:SPEC-WEB-001:EXPORT`: 내보내기 기능
- `TAG:SPEC-WEB-001:TEST:INTEGRATION`: 통합 테스트
- `TAG:SPEC-WEB-001:TEST:E2E`: E2E 테스트
- `TAG:SPEC-WEB-001:STATS`: 통계 대시보드
- `TAG:SPEC-WEB-001:UI:DARKMODE`: 다크 모드
- `TAG:SPEC-WEB-001:UI:MARCXML`: MARCXML 미리보기
