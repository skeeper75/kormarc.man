# KORMARC Web Frontend

KORMARC 웹 애플리케이션 프론트엔드입니다. Next.js 16과 React 19를 기반으로 현대적이고 반응형인 사용자 인터페이스를 제공합니다.

## 특징

- **현대적 프레임워크**: Next.js 16.1, React 19, TypeScript 5.9
- **상태 관리**: Zustand 5.0 기반 효율적인 상태 관리
- **반응형 디자인**: Tailwind CSS 4와 Shadcn/UI로 모든 디바이스 지원
- **다크 모드**: 시스템 테마 자동 감지 및 수동 토글 지원
- **접근성**: WCAG 2.1 AA 준수, ARIA 라벨, 키보드 네비게이션
- **높은 테스트 커버리지**: 84.41% 커버리지, 68개 테스트 통과

## 빠른 시작

### 1. 의존성 설치

```bash
npm install
```

### 2. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 내용을 추가하세요:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 애플리케이션을 확인하세요.

### 4. 빌드

```bash
npm run build
```

### 5. 프로덕션 실행

```bash
npm run start
```

## 테스트

### 단위 테스트

```bash
# 테스트 실행
npm run test

# 커버리지 리포트
npm run test:coverage

# Vitest UI (대화형)
npm run test:ui
```

### E2E 테스트

```bash
# E2E 테스트 실행
npm run test:e2e

# E2E 테스트 UI
npm run test:e2e:ui

# 전체 테스트
npm run test:all
```

## 프로젝트 구조

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # 루트 레이아웃
│   ├── page.tsx             # 홈 페이지
│   ├── records/             # 레코드 페이지
│   │   ├── page.tsx         # 목록 페이지
│   │   └── [id]/page.tsx    # 상세 페이지
│   └── search/              # 검색 페이지
├── components/              # 리액트 컴포넌트
│   ├── layout/              # 레이아웃 컴포넌트
│   ├── providers/           # 컨텍스트 프로바이더
│   └── ui/                  # UI 컴포넌트 (Shadcn)
├── lib/                     # 유틸리티 및 로직
│   ├── store.ts             # Zustand store
│   ├── api-records.ts       # API 클라이언트
│   └── types.ts             # TypeScript 타입
└── e2e/                     # E2E 테스트
```

## 사용 가능한 페이지

| 경로 | 설명 |
|------|------|
| `/` | 홈 페이지 |
| `/records` | 레코드 목록 (페이지네이션) |
| `/records/[id]` | 레코드 상세 |
| `/search` | 전문 검색 |

## 기술 스택

### 핵심 프레임워크
- **Next.js** 16.1.1 - React 프레임워크 (App Router)
- **React** 19.2.3 - UI 라이브러리
- **TypeScript** 5.9+ - 정적 타입 검사

### 상태 관리
- **Zustand** 5.0.9 - 가벼운 상태 관리 라이브러리
- **React Hook Form** 7.71.0 - 폼 상태 관리
- **Zod** 4.3 - 스키마 검증

### 스타일링
- **Tailwind CSS** 4 - 유틸리티 기반 CSS 프레임워크
- **Shadcn/UI** - 접근성 기반 UI 컴포넌트
- **Lucide React** - 아이콘 라이브러리

### 테스트
- **Vitest** 2.1.9 - 단위 테스트 프레임워크
- **Playwright** 1.48.0 - E2E 테스트 프레임워크
- **React Testing Library** 16.3.1 - 컴포넌트 테스트

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `NEXT_PUBLIC_API_BASE_URL` | 백엔드 API 주소 | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_VERSION` | 애플리케이션 버전 | `1.0.0` |

## 브라우저 지원

- Chrome 131+ (최신 2버전)
- Firefox 134+ (최신 2버전)
- Safari 17.5+ (최신 2버전)
- Edge 131+ (최신 2버전)

## 접근성

이 프로젝트는 WCAG 2.1 AA 수준을 준수합니다:

- 키보드 네비게이션 지원
- 스크린 리더 호환
- 색상 대비 4.5:1 이상
- ARIA 라벨 및 설명

## 배포

### Vercel (권장)

```bash
vercel deploy
```

### Docker

```bash
docker build -t kormarc-frontend .
docker run -p 3000:3000 kormarc-frontend
```

## 추가 문서

- [구현 완료 보고서](./FRONTEND_IMPLEMENTATION.md)
- [SPEC 명세서](../.moai/specs/SPEC-FRONTEND-001/spec.md)
- [프로젝트 메인 README](../README.md)

## 라이선스

MIT License

---

버전: 1.0.0
마지막 업데이트: 2026-01-12
