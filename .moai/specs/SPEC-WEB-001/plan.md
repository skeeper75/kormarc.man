# SPEC-WEB-001 구현 계획 (Implementation Plan)

## 문서 메타데이터

- **SPEC ID**: SPEC-WEB-001
- **제목**: KORMARC 웹 애플리케이션 구현 계획
- **작성자**: 지니
- **작성일**: 2026-01-11
- **버전**: 1.0.0

---

## 구현 전략 (Implementation Strategy)

### 개발 방식

**백엔드 우선 구현 → 프론트엔드 통합**

1. FastAPI 백엔드를 먼저 구현하고 pytest로 테스트
2. 프론트엔드는 백엔드 API 완성 후 통합
3. 각 Phase별 TDD 방식 적용 (RED-GREEN-REFACTOR)
4. E2E 테스트는 전체 통합 후 수행

### 테스트 전략

- **Backend**: pytest + pytest-asyncio (비동기 테스트)
- **Frontend**: Vitest + React Testing Library
- **E2E**: Playwright (브라우저 자동화)
- **Coverage Goal**: Backend ≥85%, Frontend ≥80%

### CI/CD 파이프라인

- **CI**: GitHub Actions (pytest, Vitest, lint 자동 실행)
- **CD**: Vercel (Next.js), Docker (FastAPI)
- **Quality Gate**: TRUST 5 프레임워크 검증

---

## Phase 분해 (Phase Breakdown)

### Phase 1: FastAPI 백엔드 설정 (우선순위: HIGH)

**목표**: FastAPI 프로젝트 초기화 및 기본 엔드포인트 구현

**작업 항목**:

1. **프로젝트 구조 생성**:
   - `backend/` 디렉토리 생성
   - `pyproject.toml` 설정 (Poetry)
   - 필수 패키지 설치: FastAPI, Pydantic, uvicorn, aiosqlite

2. **FastAPI 앱 초기화**:
   - `main.py` 생성
   - CORS 미들웨어 설정 (Next.js 도메인 허용)
   - 헬스체크 엔드포인트 (`GET /api/health`)

3. **기존 KORMARCBuilder 통합**:
   - `services/kormarc_service.py` 생성
   - BookInfo → KORMARC 변환 로직 통합
   - 5단계 검증 (Tier 1-5) 통합

4. **POST /api/kormarc/build 엔드포인트**:
   - Pydantic 모델 정의 (`BookInfo`)
   - KORMARC JSON/XML 응답 구조
   - 오류 처리 (422, 500)

5. **pytest 테스트 작성**:
   - `test_kormarc_service.py`: 단위 테스트
   - `test_api_kormarc.py`: 엔드포인트 통합 테스트
   - 테스트 커버리지 ≥85%

**의존성**: 기존 KORMARCBuilder 코드베이스

**예상 작업량**: Primary Goal

---

### Phase 2: Next.js 프론트엔드 설정 (우선순위: HIGH)

**목표**: Next.js 15 프로젝트 생성 및 기본 레이아웃 구성

**작업 항목**:

1. **Next.js 프로젝트 생성**:
   - `npx create-next-app@latest` (App Router, TypeScript)
   - Tailwind CSS 설정
   - 디렉토리 구조 구성 (`app/`, `components/`, `lib/`)

2. **Shadcn UI 설치**:
   - `npx shadcn-ui@latest init`
   - 필요한 컴포넌트 추가: Button, Input, Card, Alert

3. **TypeScript 타입 정의**:
   - `lib/types.ts`: BookInfo, KORMARCRecord, ValidationResult
   - Pydantic 모델과 1:1 매핑

4. **기본 레이아웃**:
   - `app/layout.tsx`: 헤더, 푸터
   - 프리텐다드 폰트 적용
   - 다크모드 지원 (선택)

5. **API 클라이언트 설정**:
   - `lib/api-client.ts`: fetch 래퍼 함수
   - 오류 처리 및 타입 안전성

**의존성**: Phase 1 완료 (FastAPI 엔드포인트)

**예상 작업량**: Primary Goal

---

### Phase 3: BookInfo 폼 구현 (우선순위: HIGH)

**목표**: 사용자 입력 폼 및 실시간 유효성 검증

**작업 항목**:

1. **React Hook Form + Zod 통합**:
   - `lib/validators.ts`: Zod 스키마 정의
   - ISBN 체크섬 커스텀 validator
   - 필수 필드 검증

2. **BookInfoForm 컴포넌트**:
   - `components/BookInfoForm.tsx` 생성
   - 7개 입력 필드 (ISBN, 제목, 저자, 출판사, 발행년, 판차, 총서명)
   - 필수 필드 표시 (*)

3. **ISBNInput 컴포넌트**:
   - `components/ISBNInput.tsx` 생성
   - 실시간 형식 검증 (디바운스 500ms)
   - 체크섬 검증 피드백 (빨간색/초록색 테두리)

4. **제출 버튼 상태 관리**:
   - 필수 필드 비어있으면 비활성화
   - 제출 중 로딩 스피너 표시

5. **Vitest 테스트**:
   - `BookInfoForm.test.tsx`: 컴포넌트 렌더링 테스트
   - `validators.test.ts`: Zod 스키마 테스트

**의존성**: Phase 2 완료

**예상 작업량**: Primary Goal

---

### Phase 3.5: Playwright 스크래핑 구현 (우선순위: HIGH)

**목표**: 국립중앙도서관 웹사이트에서 ISBN 기반 도서 정보 자동 수집

**작업 항목**:

1. **Playwright Python 설치**:
   - `poetry add playwright`
   - `playwright install chromium`

2. **스크래핑 서비스 구현**:
   - `services/scraper_service.py` 생성
   - `scrape_book_info(isbn: str)` 함수
   - 국립중앙도서관 검색 페이지 자동화
   - 도서 정보 추출 (제목, 저자, 출판사, 발행년)

3. **오류 처리 및 Retry 전략**:
   - Timeout 10초 설정
   - 최대 3회 재시도 (exponential backoff)
   - User-Agent 변경으로 차단 방지

4. **Rate Limiting 구현**:
   - 메모리 기반 또는 Redis
   - 1분당 최대 10회 스크래핑 제한

5. **GET /api/book/search 엔드포인트**:
   - Query Parameter: `isbn`
   - 응답: `ScrapingResult` (BookInfo + source + timestamp)
   - 로컬 DB 조회 → 스크래핑 순서

6. **DB 저장 로직**:
   - SQLite `books` 테이블에 수집된 정보 캐싱
   - 중복 ISBN 방지 (UNIQUE 제약)

7. **pytest 테스트**:
   - `test_scraper_service.py`: Mock Playwright 테스트
   - `test_api_books.py`: 엔드포인트 통합 테스트

**의존성**: Phase 1 완료 (FastAPI 기본 설정)

**예상 작업량**: Primary Goal

---

### Phase 4: KORMARC 생성 통합 (우선순위: HIGH)

**목표**: 프론트엔드에서 FastAPI 호출 및 KORMARC 미리보기

**작업 항목**:

1. **API 호출 로직**:
   - `lib/api-client.ts`에 `buildKORMARC()` 함수 추가
   - POST /api/kormarc/build 호출
   - 오류 처리 (네트워크 오류, 422, 500)

2. **로딩 상태 관리**:
   - `useState`로 `isLoading` 상태 관리
   - 제출 중 스피너 표시
   - 버튼 비활성화

3. **KORMARCPreview 컴포넌트**:
   - `components/KORMARCPreview.tsx` 생성
   - JSON/XML 탭 전환
   - Syntax Highlighting (선택)
   - 040 필드 노란색 하이라이트

4. **오류 메시지 표시**:
   - Alert 컴포넌트로 오류 메시지 표시
   - 사용자 친화적인 메시지 변환

5. **E2E 테스트 (Playwright)**:
   - `e2e/kormarc-generation.spec.ts`
   - 전체 플로우 테스트 (입력 → 생성 → 미리보기)

**의존성**: Phase 1, Phase 3 완료

**예상 작업량**: Primary Goal

---

### Phase 4.5: 국립중앙도서관 API 연동 준비 (우선순위: MEDIUM)

**목표**: 오픈 API 통합 및 API 우선 정책 구현

**작업 항목**:

1. **API 키 발급 및 설정**:
   - 국립중앙도서관 오픈 API 신청
   - `.env` 파일에 `NLK_API_KEY` 추가
   - 환경 변수 로드 (`python-dotenv`)

2. **API 서비스 구현**:
   - `services/api_service.py` 생성
   - `fetch_book_from_api(isbn: str)` 함수
   - httpx를 사용한 비동기 HTTP 호출

3. **API 우선 정책 구현**:
   - `GET /api/book/search` 수정
   - 순서: 로컬 DB → 국립중앙도서관 API → Playwright
   - 각 단계 실패 시 다음 단계로 fallback

4. **Rate Limiting 및 캐싱**:
   - API 호출 제한 (예: 1초당 5회)
   - 응답 캐싱 (TTL 24시간)

5. **오류 처리**:
   - API 호출 실패 시 로그 기록
   - 자동으로 Playwright로 fallback

6. **pytest 테스트**:
   - `test_api_service.py`: Mock httpx 테스트
   - API 성공/실패 시나리오 커버

**의존성**: Phase 3.5 완료 (Playwright 스크래핑)

**예상 작업량**: Secondary Goal

---

### Phase 5: 검증 결과 시각화 (우선순위: MEDIUM)

**목표**: 5단계 검증 상태를 사용자에게 명확하게 표시

**작업 항목**:

1. **ValidationStatus 컴포넌트**:
   - `components/ValidationStatus.tsx` 생성
   - Tier 1-5 검증 결과 표시
   - 각 Tier별 ✅ 통과 / ⚠️ 경고 / ❌ 실패

2. **필드별 오류 메시지**:
   - 검증 실패 시 해당 필드 하이라이트
   - 구체적인 수정 제안 (예: "040 필드 형식이 올바르지 않습니다")

3. **경고 메시지 처리**:
   - Tier 3, 4의 경고는 생성 허용하되 표시
   - 사용자가 인지할 수 있도록 노란색 경고 아이콘

4. **접근성 개선**:
   - ARIA 레이블 추가
   - 스크린 리더 호환성

**의존성**: Phase 4 완료

**예상 작업량**: Secondary Goal

---

### Phase 6: 내보내기 기능 (우선순위: MEDIUM)

**목표**: KORMARC 레코드 다운로드 및 클립보드 복사

**작업 항목**:

1. **ExportButtons 컴포넌트**:
   - `components/ExportButtons.tsx` 생성
   - "JSON 다운로드", "XML 다운로드" 버튼
   - "클립보드 복사" 버튼

2. **다운로드 로직**:
   - Blob API 사용하여 파일 생성
   - 파일명: `KORMARC_{ISBN}_{timestamp}.json`

3. **클립보드 복사 로직**:
   - Navigator Clipboard API
   - 복사 성공 시 Toast 메시지 표시

4. **Vitest 테스트**:
   - `ExportButtons.test.tsx`: 다운로드/복사 동작 테스트

**의존성**: Phase 4 완료

**예상 작업량**: Secondary Goal

---

### Phase 7: 디자인 시스템 개선 (우선순위: MEDIUM)

**목표**: Toss/당근마켓 스타일 디자인 적용

**작업 항목**:

1. **색상 팔레트 정의**:
   - Primary: 파란색 계열
   - Secondary: 회색 계열
   - Success: 초록색
   - Error: 빨간색

2. **프리텐다드 폰트 적용**:
   - `app/layout.tsx`에 폰트 로드
   - Tailwind CSS 폰트 설정

3. **애니메이션 추가**:
   - 버튼 호버 효과
   - 로딩 스피너
   - 페이드 인/아웃 트랜지션

4. **반응형 디자인**:
   - 모바일 (< 768px)
   - 태블릿 (768px - 1024px)
   - 데스크톱 (> 1024px)

**의존성**: Phase 3, 4, 5 완료

**예상 작업량**: Secondary Goal

---

### Phase 8: E2E 테스트 및 접근성 (우선순위: LOW)

**목표**: 전체 사용자 플로우 테스트 및 WCAG 2.1 AA 준수

**작업 항목**:

1. **Playwright E2E 테스트**:
   - `e2e/full-workflow.spec.ts`: 전체 플로우 테스트
   - ISBN 입력 → 생성 → 다운로드

2. **접근성 검사**:
   - axe-core 통합 (`@axe-core/playwright`)
   - WCAG 2.1 AA 검증

3. **브라우저 호환성 테스트**:
   - Chrome, Firefox, Safari, Edge 최신 2개 버전
   - 크로스 브라우저 테스트 자동화

4. **성능 테스트**:
   - Lighthouse CI 통합
   - First Contentful Paint < 1.5초 목표

**의존성**: Phase 1-7 완료

**예상 작업량**: Final Goal

---

## 기술 의존성 (Technical Dependencies)

### Backend Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
pydantic = "^2.9.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
aiosqlite = "^0.20.0"
playwright = "^1.48.0"
httpx = "^0.28.0"  # API 호출용

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
pytest-cov = "^6.0.0"
ruff = "^0.8.0"
```

### Frontend Dependencies

```json
{
  "dependencies": {
    "next": "^15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "typescript": "^5.7.0",
    "tailwindcss": "^4.0.0",
    "react-hook-form": "^7.54.0",
    "zod": "^3.24.0",
    "@hookform/resolvers": "^3.9.0"
  },
  "devDependencies": {
    "vitest": "^2.1.0",
    "@testing-library/react": "^16.1.0",
    "@playwright/test": "^1.48.0",
    "eslint": "^9.0.0",
    "eslint-config-next": "^15.1.0"
  }
}
```

---

## 리스크 관리 (Risk Management)

### 리스크 1: 스크래핑 차단

**설명**: 국립중앙도서관이 스크래핑을 차단할 가능성

**완화 전략**:
- User-Agent 변경 및 rotation
- Rate Limiting 적용 (1분당 10회)
- 국립중앙도서관 API 우선 정책 (API 연동 시 스크래핑 최소화)

**대안**: robots.txt 준수, 공식 API 사용

---

### 리스크 2: Frontend-Backend 타입 불일치

**설명**: Pydantic (Python)과 TypeScript 간 타입 불일치

**완화 전략**:
- Pydantic 모델을 JSON Schema로 변환
- TypeScript 타입 자동 생성 도구 검토 (예: `pydantic-to-typescript`)
- 수동 타입 정의 시 주석으로 매핑 관계 명시

**대안**: OpenAPI 스키마 기반 타입 자동 생성

---

### 리스크 3: ISBN 검증 성능

**설명**: 실시간 ISBN 검증 시 프론트엔드 성능 저하

**완화 전략**:
- 디바운스 500ms 적용
- 클라이언트 사이드 사전 검증 (정규식)
- 서버 검증은 제출 시에만 수행

**대안**: Web Worker 사용 (비동기 검증)

---

### 리스크 4: Playwright 설치 용량

**설명**: Playwright 브라우저 바이너리 크기 (~300MB)

**완화 전략**:
- Docker 이미지에 Playwright 미리 설치
- Chromium만 설치 (Firefox, WebKit 제외)
- CI/CD 캐싱 활용

**대안**: Puppeteer 고려 (더 가벼움, 하지만 기능 제한)

---

## 품질 목표 (Quality Goals)

### 테스트 커버리지

- **Backend**: ≥85% (pytest-cov)
- **Frontend**: ≥80% (Vitest)
- **E2E**: 핵심 플로우 100% (Playwright)

### 성능 목표

- **API 응답 시간**: P95 < 200ms (KORMARC 생성)
- **스크래핑 시간**: P95 < 5초
- **First Contentful Paint**: < 1.5초
- **Time to Interactive**: < 3.0초

### 접근성 목표

- **WCAG 2.1 AA 준수**
- **키보드 네비게이션**: 모든 기능 키보드로 접근 가능
- **스크린 리더**: NVDA, JAWS 호환성

### 브라우저 호환성

- **Chrome**: 최신 2개 버전
- **Firefox**: 최신 2개 버전
- **Safari**: 최신 2개 버전
- **Edge**: 최신 2개 버전

---

## 다음 단계 (Next Steps)

1. **Phase 1 시작**: FastAPI 백엔드 설정
2. **KORMARCBuilder 통합 확인**: 기존 코드베이스 리뷰
3. **Phase 3.5 준비**: Playwright 설치 및 국립중앙도서관 사이트 분석
4. **/moai:2-run SPEC-WEB-001** 실행하여 TDD 구현 시작

---

## 추적성 태그 (Traceability Tags)

- `#SPEC-WEB-001`
- `#Implementation-Plan`
- `#TDD`
- `#Playwright`
- `#FastAPI`
- `#Next.js`
