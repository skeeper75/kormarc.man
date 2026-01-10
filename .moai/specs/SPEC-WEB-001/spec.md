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

- 2026-01-11: SPEC 초안 생성 (v1.0.0)

---

# SPEC-WEB-001: KORMARC 레코드 조회 및 표시를 위한 웹 인터페이스

## 1. 개요

### 1.1 목적

100개의 KORMARC 프로토타입 레코드에 대한 웹 기반 조회 및 검색 인터페이스를 제공합니다.

### 1.2 범위

- **포함**: 읽기 전용 REST API, React 기반 프론트엔드 UI, 검색 및 내보내기 기능
- **제외**: 레코드 수정/삭제 기능, 사용자 인증, 외부 API 연동

### 1.3 관련 문서

- SPEC-KORMARC-PARSER-001: KORMARC 파싱 라이브러리
- `.moai/project/tech.md`: 기술 스택 및 아키텍처 표준

---

## 2. 요구사항 (EARS 형식)

### 2.1 Ubiquitous Requirements (항상 활성)

**U-001**: 시스템은 **항상** 읽기 전용 방식으로 KORMARC 레코드를 제공해야 한다.

**U-002**: 시스템은 **항상** JSON 형식으로 API 응답을 반환해야 한다.

**U-003**: 시스템은 **항상** CORS를 지원하여 프론트엔드 접근을 허용해야 한다.

**U-004**: 시스템은 **항상** 정규화된 KORMARC 필드를 제공해야 한다 (예: 제목, 저자, 출판사).

### 2.2 Event-Driven Requirements (이벤트 기반)

**E-001**: **WHEN** 사용자가 레코드 목록을 요청하면 **THEN** 페이지네이션된 레코드 목록을 반환해야 한다.

**E-002**: **WHEN** 사용자가 특정 레코드 ID를 요청하면 **THEN** 해당 레코드의 상세 정보를 반환해야 한다.

**E-003**: **WHEN** 사용자가 키워드로 검색하면 **THEN** FTS5 전문 검색을 통해 관련 레코드를 반환해야 한다.

**E-004**: **WHEN** 사용자가 레코드 내보내기를 요청하면 **THEN** JSON 또는 MARCXML 형식으로 내보내야 한다.

**E-005**: **WHEN** 존재하지 않는 레코드를 요청하면 **THEN** HTTP 404 에러를 반환해야 한다.

### 2.3 State-Driven Requirements (상태 기반)

**S-001**: **IF** 잘못된 페이지 번호가 제공되면 **THEN** HTTP 400 에러를 반환해야 한다.

**S-002**: **IF** 유효하지 않은 레코드 ID가 제공되면 **THEN** HTTP 422 에러를 반환해야 한다.

**S-003**: **IF** 검색 키워드가 비어있으면 **THEN** 전체 레코드 목록을 반환해야 한다.

### 2.4 Optional Requirements (선택 사항)

**O-001**: **가능하면** 통계 대시보드를 제공한다 (총 레코드 수, 자주 검색된 키워드).

**O-002**: **가능하면** 다크 모드를 제공한다.

**O-003**: **가능하면** MARCXML 미리보기 기능을 제공한다.

### 2.5 Unwanted Requirements (금지 사항)

**C-001**: 시스템은 레코드를 수정하거나 삭제**하지 않아야 한다**.

**C-002**: 시스템은 사용자 인증을 요구**하지 않아야 한다**.

**C-003**: 시스템은 외부 API를 호출**하지 않아야 한다**.

---

## 3. 기술 아키텍처

### 3.1 백엔드 아키텍처 (FastAPI)

**계층 구조**:
```
src/kormarc_web/
├── api/
│   ├── routes/
│   │   ├── records.py       # 레코드 조회 엔드포인트
│   │   ├── search.py        # 검색 엔드포인트
│   │   └── export.py        # 내보내기 엔드포인트
│   └── dependencies.py      # 공통 의존성
├── services/
│   ├── record_service.py    # 레코드 비즈니스 로직
│   └── search_service.py    # 검색 비즈니스 로직
├── data/
│   ├── database.py          # SQLite 연결 관리
│   └── repositories.py      # 데이터 액세스 계층
├── schemas/
│   ├── record.py            # Pydantic 스키마
│   └── pagination.py        # 페이지네이션 스키마
└── main.py                  # FastAPI 애플리케이션 진입점
```

**통합 방식**:
- 기존 `kormarc` 라이브러리 재사용
- `kormarc_prototype_100.db` SQLite 데이터베이스 연결
- FTS5 전문 검색 인덱스 활용

### 3.2 프론트엔드 아키텍처 (React)

**디렉터리 구조**:
```
web/src/
├── components/
│   ├── RecordList.tsx       # 레코드 목록 컴포넌트
│   ├── RecordDetail.tsx     # 레코드 상세 컴포넌트
│   ├── SearchBar.tsx        # 검색 바 컴포넌트
│   ├── Pagination.tsx       # 페이지네이션 컴포넌트
│   └── ExportButton.tsx     # 내보내기 버튼 컴포넌트
├── pages/
│   ├── Home.tsx             # 홈 페이지
│   ├── RecordDetailPage.tsx # 레코드 상세 페이지
│   └── SearchPage.tsx       # 검색 결과 페이지
├── hooks/
│   └── useRecords.ts        # TanStack Query 훅
├── api/
│   └── client.ts            # Axios API 클라이언트
└── App.tsx                  # 앱 진입점
```

**상태 관리**:
- TanStack Query를 사용한 서버 상태 관리
- React Router를 사용한 라우팅

### 3.3 데이터베이스

- **기존 데이터베이스**: `kormarc_prototype_100.db` (SQLite v2 스키마)
- **읽기 전용 모드**: WAL 모드 활성화
- **FTS5 검색**: `records_fts` 테이블 활용

---

## 4. API 엔드포인트

### 4.1 레코드 관리

**GET /api/v1/records**
- 설명: 페이지네이션된 레코드 목록 조회
- 쿼리 파라미터: `page` (기본값: 1), `size` (기본값: 20)
- 응답: `{ "items": [...], "total": 100, "page": 1, "size": 20 }`

**GET /api/v1/records/{record_id}**
- 설명: 단일 레코드 상세 조회
- 경로 파라미터: `record_id` (문자열)
- 응답: `{ "id": "...", "title": "...", "author": "...", ... }`

**GET /api/v1/records/{record_id}/fields**
- 설명: 레코드의 모든 KORMARC 필드 조회
- 경로 파라미터: `record_id` (문자열)
- 응답: `{ "fields": [{ "tag": "245", "indicators": "10", "value": "..." }] }`

### 4.2 검색

**GET /api/v1/search**
- 설명: 키워드 기반 전문 검색
- 쿼리 파라미터: `q` (검색어), `page` (기본값: 1), `size` (기본값: 20)
- 응답: `{ "items": [...], "total": 10, "page": 1, "size": 20 }`

**GET /api/v1/search/suggest**
- 설명: 자동 완성 검색어 제안
- 쿼리 파라미터: `q` (부분 검색어)
- 응답: `{ "suggestions": ["서울", "서울대학교"] }`

### 4.3 내보내기

**GET /api/v1/export/json**
- 설명: 레코드를 JSON 형식으로 내보내기
- 쿼리 파라미터: `record_ids` (쉼표로 구분된 ID 목록)
- 응답: JSON 파일 다운로드

**GET /api/v1/export/marcxml**
- 설명: 레코드를 MARCXML 형식으로 내보내기
- 쿼리 파라미터: `record_ids` (쉼표로 구분된 ID 목록)
- 응답: XML 파일 다운로드

### 4.4 통계 (선택)

**GET /api/v1/stats**
- 설명: 통계 정보 조회
- 응답: `{ "total_records": 100, "top_keywords": [...] }`

---

## 5. 의존성

### 5.1 백엔드 의존성

**필수**:
- `fastapi >= 0.115.0`: 웹 프레임워크
- `uvicorn >= 0.32.0`: ASGI 서버
- `python-multipart >= 0.0.9`: 파일 업로드 지원
- `kormarc >= 1.0.0`: 기존 KORMARC 파싱 라이브러리 (SPEC-KORMARC-PARSER-001)

**개발**:
- `pytest >= 8.0.0`: 테스트 프레임워크
- `pytest-asyncio >= 0.24.0`: 비동기 테스트 지원
- `ruff >= 0.8.0`: 린터 및 포맷터

### 5.2 프론트엔드 의존성

**필수**:
- `react >= 19.0.0`: UI 라이브러리
- `typescript >= 5.9.0`: 타입 안전성
- `tailwindcss >= 3.4.0`: CSS 프레임워크
- `@tanstack/react-query >= 5.0.0`: 서버 상태 관리
- `axios >= 1.7.0`: HTTP 클라이언트
- `react-router-dom >= 7.0.0`: 라우팅

**개발**:
- `vite >= 6.0.0`: 빌드 도구
- `@playwright/test >= 1.50.0`: E2E 테스트 (선택)

### 5.3 시스템 의존성

- **Node.js**: 18+ (프론트엔드 개발)
- **Python**: 3.11+ (백엔드 개발)
- **SQLite**: 3.35+ (FTS5 지원)

---

## 6. 비기능 요구사항

### 6.1 성능

- **응답 시간**: P50 < 50ms, P95 < 100ms, P99 < 200ms
- **동시 사용자**: 10명 동시 접속 시 응답 시간 유지
- **데이터베이스 쿼리**: 인덱스 활용하여 100ms 이내

### 6.2 보안

- **CORS 설정**: 허용된 도메인만 접근
- **입력 검증**: Pydantic을 통한 자동 검증
- **SQL 인젝션 방지**: Parameterized 쿼리 사용

### 6.3 유지보수성

- **테스트 커버리지**: 85% 이상
- **린팅**: ruff 0 에러, 0 경고
- **타입 체킹**: mypy 0 에러

---

## 7. 제약 사항

### 7.1 기술 제약

- SQLite 데이터베이스 사용 (읽기 전용)
- 기존 kormarc 라이브러리 재사용
- 프로토타입 100개 레코드로 제한

### 7.2 프로젝트 제약

- 인증 시스템 없음 (읽기 전용 공개 접근)
- 레코드 수정/삭제 기능 없음
- 외부 API 연동 없음

---

## 8. 추적성

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
