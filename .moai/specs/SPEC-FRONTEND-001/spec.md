---
id: SPEC-FRONTEND-001
version: "1.0.0"
status: "draft"
created: "2026-01-11"
updated: "2026-01-11"
author: "지니"
priority: "HIGH"
---

# SPEC-FRONTEND-001: Next.js 프론트엔드 - KORMARC 웹 애플리케이션 UI/UX

## HISTORY

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-01-11 | 지니 | Next.js 프론트엔드 UI/UX 초기 명세서 |

## 개요

SPEC-FRONTEND-001은 KORMARC 웹 애플리케이션의 Next.js 기반 프론트엔드 사용자 인터페이스와 사용자 경험을 정의합니다. 이 프론트엔드는 SPEC-WEB-001 FastAPI 백엔드와 통합되어 KORMARC 레코드 생성, 검증, 시각화 기능을 제공합니다.

### 핵심 목표
- BookInfo 입력 폼을 통한 직관적인 KORMARC 데이터 입력
- 실시간 ISBN 검증 및 형식 피드백
- KORMARC 레코드의 JSON/XML 포맷 실시간 미리보기
- 5단계 KORMARC 검증 결과의 시각적 표현
- 노원구 시방서(040 필드) 필수 사항의 명확한 강조

## 기술 스택

### 핵심 프레임워크 및 라이브러리

**Frontend Framework:**
- Next.js 15.1+ (App Router, TypeScript)
- React 19.0+ (Server Components, use() hook)
- TypeScript 5.7+

**Styling & UI:**
- Tailwind CSS 4.0+ (유틸리티 기반 스타일링)
- Shadcn UI (기본 컴포넌트 라이브러리)
- Pretendard 폰트 (웹 안전 한글 폰트)

**State Management & Forms:**
- React Hook Form 7.54+ (폼 상태 관리)
- Zod 3.24+ (스키마 검증, TypeScript 네이티브)
- TanStack Query (데이터 페칭 및 캐싱)

**API Integration:**
- fetch API (모던 브라우저 기본)
- axios 1.7+ (선택사항: 고급 요청 처리)

**Testing & Quality:**
- Vitest 2.1+ (단위 테스트)
- React Testing Library (컴포넌트 테스트)
- Playwright 1.48+ (E2E 테스트)
- axe-core (접근성 검사)

### 설계 시스템 및 UX 패턴

**Design Pattern Source:**
- Toss 디자인 시스템 (한국형 금융 서비스 UI)
- 당근마켓(Daangn) 디자인 패턴 (지역 기반 UX)

**Color Palette:**
- 검증 성공: 초록색 (#10B981)
- 검증 경고: 노란색 (#F59E0B)
- 검증 실패: 빨간색 (#EF4444)
- 기본 텍스트: 검은색 (#1F2937)
- 배경: 흰색 (#FFFFFF)

**Typography:**
- 제목: Pretendard Bold 28px
- 본문: Pretendard Regular 14-16px
- 라벨: Pretendard Medium 12px

## 아키텍처

### 컴포넌트 구조

```
app/
├── layout.tsx              # 루트 레이아웃
├── page.tsx               # 홈페이지
├── components/
│   ├── BookInfoForm.tsx   # BookInfo 입력 폼 (필드 7개)
│   ├── ISBNInput.tsx      # ISBN 입력 (실시간 검증)
│   ├── KORMARCPreview.tsx # 미리보기 (JSON/XML 탭)
│   ├── ValidationStatus.tsx # 검증 결과 (Tier 1-5)
│   ├── ExportButtons.tsx  # 내보내기 (JSON/XML 다운로드)
│   └── Layout/
│       ├── Header.tsx     # 헤더 (제목, 다크 모드 토글)
│       └── Footer.tsx     # 푸터 (정보, 링크)
├── lib/
│   ├── types.ts           # TypeScript 타입 정의
│   ├── api-client.ts      # API 클라이언트 래퍼
│   ├── validation.ts      # ISBN 검증 로직
│   └── utils.ts           # 유틸리티 함수
└── styles/
    └── globals.css        # 전역 스타일
```

### 상태 관리 흐름

```
BookInfo 폼 상태 (React Hook Form)
  ↓
ISBN 실시간 검증 (Zod + 카스텀 validator)
  ↓
FormData → API 호출 (fetch)
  ↓
KORMARC 레코드 (JSON + XML)
  ↓
UI 렌더링 (TanStack Query 캐싱)
```

### API 통합

**백엔드 연동:**
- 기본 URL: `http://localhost:8000` (개발) / 프로덕션 URL (배포)
- 환경 변수: `NEXT_PUBLIC_API_BASE_URL`

**통합 엔드포인트:**

1. **POST /api/kormarc/build** (KORMARC 생성)
   - 요청: BookInfo JSON
   - 응답: KORMARCRecord (json + xml + validation)
   - 오류 처리: 400 Bad Request, 500 Server Error

2. **GET /api/book/search** (도서 검색 - 선택)
   - 요청: query 파라미터 (isbn, title, author)
   - 응답: 검색 결과 배열
   - 캐싱: 1시간

3. **POST /api/kormarc/validate** (검증 - 선택)
   - 요청: KORMARC 데이터
   - 응답: ValidationResult (tier 1-5)

## 요구사항 (EARS 형식)

### 1️⃣ 항상성 요구사항 (Ubiquitous Requirements)

**REQ-U-001: 시스템은 항상 Next.js 15+ App Router 기반 웹 UI 제공**
- 입력: BookInfo 폼 (ISBN, 제목, 저자, 출판사, 발행년, 판차, 총서명)
- 출력: KORMARC JSON/XML 미리보기
- 플랫폼: 모던 웹 브라우저 (Chrome, Firefox, Safari, Edge)
- 부하 테스트: 초당 100 요청 처리 가능

**REQ-U-002: 시스템은 항상 실시간 ISBN 형식 검증 피드백 제공**
- 검증: 13자리 숫자, Luhn 체크섬 알고리즘
- 디바운스: 입력 완료 후 500ms
- 피드백: 빨간색(실패) / 초록색(성공) 테두리 + 메시지
- 응답 속도: < 100ms

**REQ-U-003: 시스템은 항상 KORMARC 레코드를 JSON/XML 탭으로 표시**
- JSON 탭: 구조화된 JavaScript 객체 형식
- XML 탭: MARCXML 표준 형식 (UTF-8)
- 미리보기: 브라우저 내 렌더링 (코드 미러 또는 기본 텍스트)
- 최대 레코드 크기: 1MB

**REQ-U-004: 시스템은 항상 5단계 검증 결과를 색상 코드로 시각화**
- Tier 1-5: 각 단계별 상태 (✅ 통과 / ⚠️ 경고 / ❌ 실패)
- 색상: 초록색(통과), 노란색(경고), 빨간색(실패)
- 설명: 각 Tier별 검증 규칙 간단 설명
- 아이콘: 체크마크, 경고, 엑스 아이콘 사용

### 2️⃣ 이벤트 기반 요구사항 (Event-Driven Requirements)

**REQ-E-001: WHEN 사용자가 BookInfo 폼 제출 THEN POST /api/kormarc/build 호출**
- Request: BookInfo 데이터 타입 안전성 (TypeScript Zod 검증)
- Response: KORMARCRecord (json + xml + validationResult)
- 오류 처리: 네트워크 오류 (재시도 3회), API 오류 (사용자 친화적 메시지)
- 타임아웃: 30초

**REQ-E-002: WHEN ISBN 입력 변경 THEN 형식 검증 실행**
- 시점: 입력 후 500ms 디바운스
- 검증: Luhn 알고리즘 (체크섬) + 정규식 검증
- 피드백: 인라인 오류 메시지 (필드 아래)
- 성공 메시지: "유효한 ISBN입니다"

**REQ-E-003: WHEN KORMARC 생성 성공 THEN JSON/XML 미리보기 표시**
- 040 필드: 노란색 배경 하이라이트 (노원구 필드)
- Syntax Highlighting: 선택사항 (Prism.js)
- 캐싱: 동일 ISBN 재요청 시 TanStack Query 로컬 캐시
- 캐시 TTL: 5분

**REQ-E-004: WHEN 검증 실패 THEN 필드별 오류 메시지 표시**
- 메시지: 구체적 수정 가이드 포함 (예: "ISBN 체크섬 불일치. 올바른 형식을 확인해주세요.")
- 위치: 해당 필드 아래 빨간색 텍스트 (Tailwind `text-red-500`)
- 개수: 최대 3개 오류 메시지 동시 표시

**REQ-E-005: WHEN 사용자가 내보내기 클릭 THEN KORMARC 파일 다운로드**
- 형식: JSON, XML 선택 가능
- 파일명: `kormarc_{isbn}_{timestamp}.{ext}` (예: `kormarc_9791162233149_20260111120000.json`)
- 방법: Blob API + `<a href>` 다운로드 트리거
- 다운로드 속도: 1MB 파일 < 1초

### 3️⃣ 상태 기반 요구사항 (State-Driven Requirements)

**REQ-S-001: IF 필수 필드 비어있음 THEN "KORMARC 생성" 버튼 비활성화**
- 필수 필드: ISBN, 제목, 저자, 출판사, 발행년
- 버튼: disabled 속성 + 회색 배경 (Tailwind `disabled:bg-gray-300`)
- 툴팁: 호버 시 "필수 필드를 모두 입력해주세요" (aria-label)
- 접근성: 스크린 리더 공지

**REQ-S-002: IF API 요청 중 THEN 로딩 스피너 + 버튼 비활성화**
- UI: 로딩 상태 시각적 피드백 (스피너 또는 프로그래스 바)
- 버튼: disabled + 텍스트 변경 ("생성 중...")
- 취소: 요청 취소 버튼 (선택, AbortController 사용)

**REQ-S-003: IF KORMARC 미리보기 표시 THEN 040 필드 하이라이트**
- 색상: 노란색 배경 (Tailwind `bg-yellow-100`)
- 아이콘: 별표(⭐) 또는 강조 아이콘
- 설명: 호버 시 "노원구 시방서 필수 필드"

### 4️⃣ 선택적 요구사항 (Optional Requirements)

**REQ-O-001: 가능하면 입력 데이터 localStorage 자동 저장**
- 저장: 폼 입력값 30초마다 JSON으로 저장
- 복구: 페이지 새로고침 후 이전 입력값 자동 복구
- 삭제: 폼 초기화 시 저장된 데이터 제거
- 키: `kormarc_form_draft`

**REQ-O-002: 가능하면 다크 모드 지원**
- 토글: Header에 다크 모드 버튼 (달/태양 아이콘)
- 저장: 사용자 선택 localStorage에 저장
- 색상: Tailwind CSS `dark:` 프리픽스 활용
- 기본값: 시스템 설정 따름 (`prefers-color-scheme`)

**REQ-O-003: 가능하면 ISBN 파일 업로드 일괄 처리**
- 형식: CSV, TXT (한 줄당 ISBN 1개)
- 처리: Web Worker 백그라운드 작업 (UI 블로킹 없음)
- 결과: ZIP 파일 다운로드 (각 ISBN별 KORMARC JSON/XML)
- 제한: 최대 100개 ISBN

### 5️⃣ 금지 동작 (Unwanted Behaviors)

**REQ-C-001: 시스템은 내부 오류 스택 트레이스 노출 금지**
- 사용자에게: "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요." (친화적 메시지)
- 로그: 브라우저 콘솔(개발 환경)과 모니터링 시스템(프로덕션)에만 기록
- 민감 정보: API 엔드포인트, SQL 쿼리, 환경 변수 절대 노출 금지

**REQ-C-002: 시스템은 검증 실패한 폼 제출 허용 금지**
- 차단: 필수 필드 미입력 또는 ISBN 체크섬 실패 시 서버 요청 안 함
- 클라이언트 검증: Zod 스키마로 사전 검증
- 서버 검증: FastAPI 백엔드에서 재검증 (이중 검증)

**REQ-C-003: 시스템은 API 엔드포인트나 민감 정보 노출 금지**
- 환경 변수: 모두 `NEXT_PUBLIC_` 접두사 사용 (공개 가능 데이터만)
- 예: `NEXT_PUBLIC_API_BASE_URL` (URL), `NEXT_PUBLIC_APP_VERSION` (버전)
- 민감 정보: API 키, JWT 토큰은 Server Action 또는 서버 환경 변수에만 저장

## 성능 목표

### Web Vitals

- FCP (First Contentful Paint): < 1.5초
- LCP (Largest Contentful Paint): < 2.5초
- CLS (Cumulative Layout Shift): < 0.1
- TTFB (Time to First Byte): < 500ms

### 기타 성능 지표

- ISBN 검증 응답: < 100ms
- API 응답 시간: < 3초 (p95)
- 번들 크기: < 200KB (gzipped)
- 캐시 히트율: > 80%

## 브라우저 지원

- Chrome 131+ (Latest 2 versions)
- Firefox 134+ (Latest 2 versions)
- Safari 17.5+ (Latest 2 versions)
- Edge 131+ (Latest 2 versions)

## 보안 및 규정 준수

### OWASP 보안

- XSS 방지: React JSX 자동 이스케이핑, Sanitize HTML 라이브러리 (선택)
- CSRF 방지: SameSite Cookie, CSRF 토큰 (백엔드에서 관리)
- 입력 검증: Zod 스키마 클라이언트 + 서버 쌍방향 검증

### 접근성

- WCAG 2.1 AA 준수
- 키보드 네비게이션 (Tab, Enter, Escape)
- 스크린 리더 지원 (aria-label, aria-describedby)
- 색상 대비: 최소 4.5:1 (AAA 권고)

## API 통합 명세

### BookInfoForm 데이터 구조

```typescript
interface BookInfo {
  isbn: string;           // 13자리 ISBN
  title: string;         // 도서명
  author: string;        // 저자명
  publisher: string;     // 출판사
  publicationYear: number; // 발행년
  edition?: string;      // 판차 (선택)
  seriesName?: string;   // 총서명 (선택)
}
```

### KORMARC 레코드 응답

```typescript
interface KORMARCRecord {
  isbn: string;
  json: object;          // KORMARC JSON 형식
  xml: string;           // MARCXML 형식
  validation: {
    tier1: { pass: boolean; message: string };
    tier2: { pass: boolean; message: string };
    tier3: { pass: boolean; message: string };
    tier4: { pass: boolean; message: string };
    tier5: { pass: boolean; message: string };
  };
}
```

### 오류 응답

```typescript
interface ErrorResponse {
  error: {
    code: string;        // 오류 코드 (INVALID_ISBN, etc.)
    message: string;     // 사용자 친화적 메시지
    details?: string;    // 기술 세부정보 (개발 모드)
  };
}
```

## 정의된 완료 조건

- 모든 EARS 요구사항 구현
- 테스트 커버리지 ≥ 80%
- Web Vitals 기준 충족
- WCAG 2.1 AA 준수
- E2E 테스트 통과
- 코드 리뷰 승인

---

**작성일**: 2026-01-11
**상태**: Draft
**다음 단계**: /moai:2-run SPEC-FRONTEND-001 으로 TDD 구현 시작
