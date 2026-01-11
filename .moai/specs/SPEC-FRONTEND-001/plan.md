---
id: SPEC-FRONTEND-001
version: "1.0.0"
status: "implementation-plan"
created: "2026-01-11"
updated: "2026-01-11"
author: "지니"
priority: "HIGH"
---

# SPEC-FRONTEND-001 구현 계획 (Plan.md)

## 프로젝트 개요

SPEC-FRONTEND-001 Next.js 프론트엔드 구현 계획입니다. 이 문서는 SPEC-FRONTEND-001 의 모든 요구사항을 구현하기 위한 단계적 로드맵과 기술 접근 방법을 제시합니다.

**SPEC ID**: SPEC-FRONTEND-001
**기술 스택**: Next.js 15.1+, React 19, TypeScript 5.7, Tailwind CSS 4.0, Shadcn UI
**통합 대상**: SPEC-WEB-001 FastAPI 백엔드

---

## Phase 분해 및 우선순위

### Phase 1: 프로젝트 기초 설정 (우선순위: HIGH)

**목표**: Next.js 프로젝트 초기화 및 개발 환경 구성

**작업 항목**:

1. Next.js 15.1 프로젝트 초기화
   - 명령: `npx create-next-app@latest --typescript --tailwind --app`
   - App Router 기반 구조 선택
   - TypeScript 자동 활성화

2. Tailwind CSS 4.0 설정
   - tailwind.config.ts 설정 (다크 모드 지원)
   - globals.css에 Tailwind 디렉티브 추가
   - Pretendard 웹 폰트 import

3. Shadcn UI 설치 및 초기화
   - 명령: `npx shadcn-ui@latest init`
   - 기본 컴포넌트 설치 (Button, Input, Card, Tabs 등)
   - 테마 커스터마이징 (색상 팔레트 설정)

4. 프리텐다드 폰트 설정
   - `next/font/local` 또는 `@import` 사용
   - font-family: 'Pretendard', sans-serif 설정
   - 가변 폰트 가중치 (400, 500, 700)

5. 개발 환경 도구 설치
   - TypeScript 5.7+ (기본 포함)
   - ESLint 설정 (next/eslint-config-next)
   - Prettier 설정 (일관된 포매팅)

**기술 의존성**: Node.js 18+, npm/yarn/pnpm

**완료 기준**:
- npm run dev 로 로컬 서버 실행 가능
- http://localhost:3000 접속 시 기본 Next.js 페이지 표시
- TypeScript 타입 체크 오류 없음

---

### Phase 2: 타입 정의 및 API 클라이언트 (우선순위: HIGH)

**목표**: TypeScript 타입 안전성 및 API 통신 기반 구축

**작업 항목**:

1. TypeScript 타입 정의 (lib/types.ts)
   - BookInfo 인터페이스 (7개 필드)
   - KORMARCRecord 인터페이스 (json, xml, validation)
   - ValidationResult 인터페이스 (Tier 1-5)
   - ErrorResponse 인터페이스
   - Pydantic 백엔드 모델과 동기화

2. Zod 스키마 정의 (lib/validation.ts)
   - BookInfoSchema: Zod z.object() 정의
   - ISBN 커스텀 검증 (정규식 + Luhn 알고리즘)
   - 필수 필드 mark 설정
   - 선택 필드는 z.optional() 처리

3. API 클라이언트 (lib/api-client.ts)
   - fetch 래퍼 함수 (기본 설정, 헤더, 타임아웃)
   - 환경 변수 관리 (NEXT_PUBLIC_API_BASE_URL)
   - 오류 처리 (네트워크 오류, HTTP 오류 코드)
   - 재시도 로직 (3회, exponential backoff)
   - CORS 설정 및 요청 헤더

4. API 엔드포인트 함수
   - createKORMARC(bookInfo: BookInfo): Promise<KORMARCRecord>
   - searchBook(query: string): Promise<Book[]>
   - validateKORMARC(data: object): Promise<ValidationResult>

**기술 의존성**: Zod 3.24+, TypeScript 5.7+

**완료 기준**:
- lib/types.ts, lib/validation.ts, lib/api-client.ts 파일 생성
- TypeScript 타입 검사 통과
- API 클라이언트 함수 테스트 작성

---

### Phase 3: BookInfo 입력 폼 컴포넌트 (우선순위: HIGH)

**목표**: 사용자가 KORMARC 데이터를 입력할 수 있는 폼 UI 구현

**작업 항목**:

1. BookInfoForm 컴포넌트 (components/BookInfoForm.tsx)
   - React Hook Form 통합
   - Zod 스키마 validation
   - 폼 레이아웃: 그리드 또는 플렉스 (Tailwind)
   - 제출 버튼 상태 관리 (필수 필드 체크)

2. ISBNInput 컴포넌트 (components/ISBNInput.tsx)
   - Input 필드 (13자리만 입력 가능)
   - 실시간 형식 검증 (500ms 디바운스)
   - 검증 상태 시각화 (테두리 색상 변경)
   - 오류 메시지 표시 (인라인)

3. 폼 필드 정의
   - ISBN: 13자리 숫자 (필수)
   - 제목: 문자열 (필수)
   - 저자: 문자열 (필수)
   - 출판사: 문자열 (필수)
   - 발행년: 숫자 (필수)
   - 판차: 문자열 (선택)
   - 총서명: 문자열 (선택)

4. 사용자 피드백
   - 필수 필드 표시 (asterisk *)
   - 입력 중 피드백 (character count, validation status)
   - 오류 메시지 (구체적 수정 가이드)
   - 성공 메시지 (폼 제출 전)

**기술 의존성**: React Hook Form 7.54+, Zod 3.24+, Shadcn UI

**완료 기준**:
- BookInfoForm.tsx, ISBNInput.tsx 파일 생성
- 모든 필드 렌더링 확인
- ISBN 검증 로직 동작 확인 (단위 테스트)

---

### Phase 4: KORMARC 생성 및 미리보기 (우선순위: HIGH)

**목표**: API 호출 및 KORMARC 데이터 시각화

**작업 항목**:

1. KORMARCPreview 컴포넌트 (components/KORMARCPreview.tsx)
   - JSON/XML 탭 전환 (Shadcn Tabs 컴포넌트)
   - 예쁜 출력 포맷팅 (JSON.stringify 들여쓰기)
   - 040 필드 하이라이트 (노란색 배경)
   - 코드 미러 또는 기본 pre/code 태그 사용

2. 폼 제출 로직 (BookInfoForm.tsx)
   - 폼 제출 이벤트 핸들러
   - POST /api/kormarc/build API 호출
   - 로딩 상태 관리 (isLoading, isPending)
   - 성공/오류 상태 처리

3. 상태 관리 (useState, useCallback)
   - kormarc: KORMARCRecord | null
   - isLoading: boolean
   - error: ErrorResponse | null
   - activeTab: "json" | "xml"

4. 오류 처리
   - 네트워크 오류 (재시도 버튼)
   - API 오류 (사용자 친화적 메시지)
   - 타임아웃 (30초 이상 응답 없음)
   - 유효성 검증 오류 (필드별)

**기술 의존성**: TanStack Query (캐싱), axios 또는 fetch

**완료 기준**:
- KORMARCPreview.tsx 파일 생성
- API 호출 통합 테스트 (Mock 서버 또는 실제 백엔드)
- JSON/XML 탭 전환 동작 확인
- 040 필드 하이라이트 확인

---

### Phase 5: 검증 결과 시각화 (우선순위: MEDIUM)

**목표**: 5단계 KORMARC 검증 결과를 색상 코드로 표시

**작업 항목**:

1. ValidationStatus 컴포넌트 (components/ValidationStatus.tsx)
   - Tier 1-5 순차 표시
   - 상태별 색상: 초록색(통과), 노란색(경고), 빨간색(실패)
   - 아이콘: 체크마크, 경고, 엑스 (Shadcn Icons)
   - 각 Tier 설명 텍스트

2. Tier 렌더링
   - Tier 1 (기술 검증): KORMARC 형식 유효성
   - Tier 2 (문법 검증): MARC 필드 구문
   - Tier 3 (의미 검증): 노원구 필수 필드 (040)
   - Tier 4 (정합성 검증): 필드 값 일관성
   - Tier 5 (기관 규정 검증): 추가 요구사항

3. 진행 바 또는 진행률 표시
   - 전체 검증 진행도 (5/5 통과 등)
   - 각 Tier별 상태 바

4. 상세 정보 토글
   - 각 Tier 클릭 시 세부 오류 메시지 표시
   - 수정 가이드 (예: "040 필드 추가 필요")

**기술 의존성**: Shadcn UI (Card, Progress)

**완료 기준**:
- ValidationStatus.tsx 파일 생성
- 5가지 Tier 상태 렌더링 확인
- 색상 및 아이콘 시각화 확인

---

### Phase 6: 내보내기 기능 (우선순위: MEDIUM)

**목표**: KORMARC 데이터 JSON/XML 파일 다운로드

**작업 항목**:

1. ExportButtons 컴포넌트 (components/ExportButtons.tsx)
   - JSON 다운로드 버튼
   - XML 다운로드 버튼
   - 클립보드 복사 버튼 (선택)

2. 다운로드 로직 (lib/export-utils.ts)
   - Blob 객체 생성 (JSON, XML)
   - File 다운로드 트리거 (<a href> 다이나믹 생성)
   - 파일명 생성: kormarc_{isbn}_{timestamp}.{ext}
   - 타임스탐프 포맷: YYYYMMDDHHMMSS

3. 클립보드 복사 (선택)
   - navigator.clipboard.writeText() 사용
   - 복사 완료 토스트 메시지
   - 복사 실패 오류 처리

4. 토스트 알림
   - 다운로드 시작 (선택)
   - 다운로드 완료
   - 클립보드 복사 완료

**기술 의존성**: Blob API, Shadcn Toast 또는 react-hot-toast

**완료 기준**:
- ExportButtons.tsx 파일 생성
- 다운로드 로직 테스트 (단위 테스트)
- 수동 테스트: 실제 파일 다운로드 확인

---

### Phase 7: 디자인 및 반응형 (우선순위: MEDIUM)

**목표**: UI 스타일링 및 모든 디바이스에서 보기 좋은 레이아웃

**작업 항목**:

1. 글로벌 스타일 (styles/globals.css)
   - Pretendard 폰트 face 정의
   - 색상 변수 (CSS Custom Properties)
   - 다크 모드 색상 정의 (prefers-color-scheme)

2. 레이아웃 컴포넌트
   - Header 컴포넌트 (제목, 네비게이션, 다크 모드 토글)
   - Main 컴포넌트 (콘텐츠 영역)
   - Footer 컴포넌트 (정보, 링크)
   - 최대 폭: 1200px (xl 브레이크포인트)

3. 반응형 디자인
   - 모바일 (< 768px): 단열, 조정된 패딩/마진
   - 태블릿 (768px - 1024px): 2열, 중간 공간
   - 데스크톱 (> 1024px): 3열 또는 더 넓은 레이아웃
   - Tailwind 반응형 클래스 (md:, lg:, xl:)

4. 다크 모드 지원
   - HTML dark: 클래스 토글
   - localStorage 저장 (user preference)
   - 시스템 설정 자동 감지
   - 모든 색상을 dark: 프리픽스로 정의

5. 애니메이션 및 호버 효과
   - 버튼 호버: 배경색 변경, 스케일 약간 증가
   - 폼 필드 포커스: 테두리색 변경, 그림자 추가
   - 로딩 스피너: 회전 애니메이션
   - 트랜지션: 0.2-0.3초

**기술 의존성**: Tailwind CSS 4.0, Shadcn UI

**완료 기준**:
- 모바일, 태블릿, 데스크톱에서 레이아웃 확인
- 다크 모드 토글 동작 확인
- 모든 색상이 대비 기준 충족 (최소 4.5:1)

---

### Phase 8: 테스트 및 접근성 (우선순위: LOW)

**목표**: 코드 품질 및 접근성 표준 준수

**작업 항목**:

1. 단위 테스트 (Vitest)
   - BookInfoForm 컴포넌트 테스트
   - ISBNInput 검증 로직 테스트
   - API 클라이언트 테스트 (Mock)
   - 유틸리티 함수 테스트
   - 목표: ≥ 80% 커버리지

2. 컴포넌트 테스트 (React Testing Library)
   - 폼 제출 플로우
   - 오류 메시지 표시
   - 로딩 상태 UI
   - 탭 전환 (JSON/XML)

3. E2E 테스트 (Playwright)
   - 전체 플로우: 입력 → 생성 → 다운로드
   - 에러 시나리오: 잘못된 ISBN, 네트워크 오류
   - 브라우저별 테스트 (Chrome, Firefox, Safari)

4. 접근성 테스트 (axe-core)
   - 자동 검사: axe DevTools
   - 키보드 네비게이션: Tab, Enter, Escape 동작
   - 스크린 리더: NVDA, JAWS로 테스트
   - 색상 대비: WCAG AA 기준 확인

5. 성능 테스트
   - Lighthouse 검사
   - Web Vitals 측정 (web-vitals 라이브러리)
   - 번들 크기 확인 (next/bundle-analyzer)

**기술 의존성**: Vitest 2.1+, Playwright 1.48+, axe-core

**완료 기준**:
- 테스트 커버리지 ≥ 80%
- E2E 테스트 모두 통과
- Lighthouse 점수 ≥ 90 (Performance, Accessibility, Best Practices)
- WCAG 2.1 AA 준수

---

## 기술 의존성 및 버전

### 핵심 라이브러리

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
    "@tanstack/react-query": "^5.64.0",
    "@tanstack/react-query-devtools": "^5.64.0"
  },
  "devDependencies": {
    "vitest": "^2.1.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.6.0",
    "@playwright/test": "^1.48.0",
    "axe-core": "^4.10.0",
    "prettier": "^3.4.0",
    "eslint": "^9.16.0"
  }
}
```

### 설치 순서

1. Next.js 초기화 (자동 설치: React, TypeScript)
2. Tailwind CSS 설치
3. Shadcn UI 설치 (기본 컴포넌트)
4. React Hook Form, Zod 설치
5. TanStack Query 설치
6. 테스트 라이브러리 설치

---

## 리스크 관리

### 리스크 1: Frontend-Backend 타입 불일치

**설명**: Python Pydantic 모델과 TypeScript 인터페이스 간 구조 차이

**영향도**: HIGH
**발생 확률**: MEDIUM

**대응 전략**:
- Pydantic 모델 문서화 (JSON Schema 자동 생성)
- TypeScript 타입을 Pydantic에서 자동 생성 (datamodel-code-generator 사용)
- API 통합 테스트 (실제 백엔드와 테스트)
- 정기적 동기화 (월 1회)

### 리스크 2: 성능 저하 (LCP > 2.5s)

**설명**: 큰 KORMARC 레코드 렌더링 시 페이지 느려짐

**영향도**: MEDIUM
**발생 확률**: LOW-MEDIUM

**대응 전략**:
- React.memo() 메모이제이션
- 가상 스크롤링 (react-window, 큰 XML 텍스트용)
- 청크 로딩 (대용량 파일은 분할 로드)
- Lighthouse 성능 점수 ≥ 90 유지

### 리스크 3: CORS 이슈

**설명**: 브라우저 CORS 정책으로 인한 API 호출 실패

**영향도**: HIGH
**발생 확률**: MEDIUM

**대응 전략**:
- 백엔드에서 CORS 헤더 설정 (Access-Control-Allow-Origin)
- 개발/프로덕션 환경별 엔드포인트 분리
- 환경 변수: NEXT_PUBLIC_API_BASE_URL
- 테스트: Playwright에서 CORS 시나리오 검증

### 리스크 4: 사용자 입력 데이터 손실

**설명**: 페이지 새로고침 시 입력한 폼 데이터 손실

**영향도**: LOW
**발생 확률**: HIGH

**대응 전략**:
- localStorage 자동 저장 (REQ-O-001, 선택사항)
- 페이지 언로드 경고 (unsaved changes)
- IndexedDB 백업 (대용량 데이터용, 선택)

### 리스크 5: 브라우저 호환성

**설명**: 구형 브라우저에서 신기능 미지원

**영향도**: MEDIUM
**발생 확률**: LOW

**대응 전략**:
- 폴리필 사용 (fetch, Promise, async/await)
- 크로스 브라우저 테스트 (BrowserStack, Sauce Labs)
- 지원 브라우저: Chrome 131+, Firefox 134+, Safari 17.5+, Edge 131+

---

## 마일스톤 및 완료 기준

### Milestone 1: 기초 설정 완료
- Phase 1-2 완료
- 타입 안전성 확보
- API 클라이언트 작동
- **완료 기준**: npm run dev 실행 시 콘솔 오류 없음

### Milestone 2: 핵심 기능 구현
- Phase 3-6 완료
- BookInfo 입력 → KORMARC 생성 → 다운로드 플로우 완료
- 기본 검증 결과 표시
- **완료 기준**: 수동 테스트에서 전체 플로우 동작

### Milestone 3: 다듬기 및 테스트
- Phase 7-8 완료
- 디자인 완성 (반응형, 다크 모드)
- 테스트 커버리지 ≥ 80%
- **완료 기준**: Lighthouse 점수 ≥ 90, WCAG AA 준수

### Milestone 4: 프로덕션 준비
- 성능 최적화 (LCP < 2.5s)
- 보안 검사 (OWASP)
- 배포 설정 (Vercel 또는 Docker)
- **완료 기준**: 프로덕션 배포 가능

---

## 기술 아키텍처 방향

### 클라이언트 상태 관리

**선택**: React Hook Form (폼 상태) + TanStack Query (서버 상태) + 로컬 상태 (UI)

**이유**:
- React Hook Form: 폼 복잡도 관리 (7개 필드 × 검증)
- TanStack Query: API 응답 캐싱, 재요청 최소화
- 로컬 상태: UI 상태 (탭, 로딩, 모달)

### 스타일링

**선택**: Tailwind CSS 4.0 + Shadcn UI

**이유**:
- Tailwind: 빠른 프로토타이핑, 디자인 시스템 일관성
- Shadcn UI: 접근성 기본 제공 (aria-*, keyboard nav)
- 커스터마이징: CSS 변수로 색상 관리

### API 통신

**선택**: fetch API (기본) + axios (선택)

**이유**:
- fetch: 모던 브라우저 기본 지원, 폴리필 불필요
- axios: 고급 기능 (interceptor, 타임아웃), 타입 안전성

---

## 배포 준비

### 환경 변수

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # 개발
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ANALYTICS_ID=(선택)
```

### 빌드 및 배포

```bash
# 빌드
npm run build

# 로컬 프로덕션 테스트
npm run start

# Vercel 배포 (권장)
vercel deploy --prod
```

---

## 다음 단계

1. **Phase 1 구현**: 프로젝트 초기화 및 기본 설정 완료
2. **Phase 2 구현**: 타입 정의 및 API 클라이언트 작성
3. **Phase 3-6 구현**: 핵심 UI 컴포넌트 개발
4. **테스트 작성**: 각 Phase 완료 후 단위 테스트 작성
5. **통합 테스트**: 모든 Phase 완료 후 E2E 테스트
6. **성능 최적화**: Lighthouse 점수 >= 90 달성
7. **배포**: Vercel 또는 프로덕션 환경에 배포

---

**작성일**: 2026-01-11
**상태**: Implementation Plan Draft
**다음 명령**: `/moai:2-run SPEC-FRONTEND-001`으로 TDD 구현 시작
