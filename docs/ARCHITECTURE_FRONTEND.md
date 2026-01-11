# SPEC-FRONTEND-001: 프론트엔드 아키텍처

## 개요

KORMARC 웹 인터페이스의 프론트엔드 아키텍처 설명서입니다. Next.js 16 + React 19를 기반으로 구축되었습니다. 본 문서는 시스템 설계, 아키텍처, 컴포넌트 구조 및 통합 패턴을 상세히 설명합니다.

## 기술 스택

### 프레임워크 및 언어
- **프레임워크**: Next.js 16.1 (App Router)
- **UI Library**: React 19.0
- **언어**: TypeScript 5.9
- **스타일**: Tailwind CSS 4.0 + Shadcn UI
- **패키지 관리**: npm/pnpm

### 폼 및 검증
- **폼 관리**: React Hook Form 7.71
- **검증**: Zod 4.3 (스키마 검증)

### 테스팅
- **단위 테스트**: Vitest (68개 테스트)
- **컴포넌트 테스트**: React Testing Library
- **E2E 테스트**: Playwright (준비됨)

### API 통신
- **HTTP 클라이언트**: fetch API (Next.js 내장)
- **API 라우트**: Next.js API Routes (/api/*)

## 프로젝트 구조

```
app/
├── page.tsx                    # 홈 페이지 (메인 KORMARC 생성기)
├── layout.tsx                  # 루트 레이아웃
├── globals.css                 # 전역 스타일
│
├── components/
│   ├── BookInfoForm.tsx        # 도서 정보 입력 폼 (부모)
│   ├── ISBNInput.tsx           # ISBN 입력 필드 (실시간 검증)
│   ├── ValidationStatus.tsx    # 5단계 검증 상태 표시
│   ├── KORMARCPreview.tsx      # JSON/XML 미리보기 (탭)
│   ├── ExportButtons.tsx       # 다운로드/복사 기능
│   └── LoadingSpinner.tsx      # 로딩 표시 애니메이션
│
├── api/
│   └── kormarc/
│       └── route.ts            # POST /api/kormarc (백엔드 프록시)
│
└── lib/
    ├── validators.ts          # Zod 검증 스키마
    └── api-client.ts          # API 클라이언트 유틸리티

__tests__/
├── components/                # 컴포넌트 테스트
│   ├── BookInfoForm.test.tsx
│   ├── ISBNInput.test.tsx (포함되어 있음)
│   ├── ValidationStatus.test.tsx
│   ├── KORMARCPreview.test.tsx
│   ├── ExportButtons.test.tsx
│   └── LoadingSpinner.test.tsx
├── lib/                       # 유틸리티 테스트
├── page.test.tsx             # 홈 페이지 테스트
└── setup.ts                  # 테스트 설정 파일
```

## 핵심 아키텍처 패턴

### 1. 컴포넌트 계층 구조

#### 최상위 컴포넌트: HomePage
- 전체 레이아웃 및 페이지 구조 관리
- 헤더, 메인 콘텐츠, 푸터 구성
- BookInfoForm 컴포넌트 렌더링

#### 부모 컴포넌트: BookInfoForm
- React Hook Form을 활용한 폼 상태 관리
- 5개 필드 관리: ISBN, 제목, 저자, 출판사, 발행년
- 자식 컴포넌트 조합 및 로직 조율
- localStorage를 통한 자동 저장

```
HomePage
└── BookInfoForm (상태 관리)
    ├── ISBNInput (실시간 검증)
    ├── 제목/저자/출판사/발행년 필드 (일반 입력)
    ├── ValidationStatus (검증 상태)
    ├── ExportButtons (다운로드/복사)
    ├── KORMARCPreview (결과 표시)
    └── LoadingSpinner (로딩 중)
```

#### 자식 컴포넌트들
- **ISBNInput**: ISBN 입력 필드, 실시간 체크섬 검증
- **ValidationStatus**: 5단계 색상 검증 상태 표시
- **KORMARCPreview**: JSON/XML 탭 결과 표시
- **ExportButtons**: JSON 다운로드, XML 다운로드, 클립보드 복사
- **LoadingSpinner**: API 호출 중 로딩 애니메이션

### 2. 상태 관리 전략

React Hooks 기반 간단한 상태 관리 (전역 상태 도구 불필요):

```typescript
// BookInfoForm에서의 상태 관리
const [isLoading, setIsLoading] = useState(false);
const [result, setResult] = useState<APIResponse | null>(null);
const [error, setError] = useState<string | null>(null);

const form = useForm<BookInfoInput>({
  resolver: zodResolver(bookInfoSchema),
  mode: 'onChange',
  defaultValues: loadFromLocalStorage(),
});

// localStorage 자동 저장
useEffect(() => {
  const subscription = form.watch((data) => {
    saveToLocalStorage(data);
  });
  return () => subscription.unsubscribe();
}, [form]);
```

### 3. 데이터 흐름

```
사용자 입력
    ↓
Form (React Hook Form)
    ↓
Zod 검증 (클라이언트 측)
    ↓
필수 필드 확인 (버튼 활성화)
    ↓
API 호출 (POST /api/kormarc)
    ↓
로딩 상태 표시
    ↓
결과 수신 (JSON + XML)
    ↓
KORMARCPreview 표시
    ↓
사용자 내보내기 (다운로드/복사)
```

## 검증 시스템

### 필드 검증 계층

**1단계: 입력 타입 검증** (실시간)
- ISBN: 10-13자 숫자만 허용
- 제목/저자/출판사: 1-200자 문자열
- 발행년: 1900-2100 범위의 숫자

**2단계: ISBN 체크섬 검증** (실시간, ISBN 필드 blur 시)
- ISBN-10: 가중치 합 mod 11
- ISBN-13: 특정 위치 가중치 mod 10

**3단계: 필수 필드 검증** (연속)
- 모든 5개 필드 필수
- 빈 값 허용 안 함

**4단계: 백엔드 검증** (API 호출 시)
- 추가 비즈니스 로직 검증
- 데이터베이스 제약 확인

### Zod 스키마 정의

```typescript
export const bookInfoSchema = z.object({
  isbn: z
    .string()
    .min(10, '10자 이상의 ISBN이 필요합니다')
    .max(13, '13자 이하의 ISBN이 필요합니다')
    .regex(/^[0-9]+$/, '숫자만 입력 가능합니다'),
  title: z
    .string()
    .min(1, '제목을 입력하세요')
    .max(200, '제목은 200자 이하여야 합니다'),
  author: z
    .string()
    .min(1, '저자를 입력하세요')
    .max(100, '저자명은 100자 이하여야 합니다'),
  publisher: z
    .string()
    .min(1, '출판사를 입력하세요')
    .max(100, '출판사명은 100자 이하여야 합니다'),
  publicationYear: z
    .number()
    .int('정수만 입력 가능합니다')
    .min(1900, '1900년 이상이어야 합니다')
    .max(new Date().getFullYear(), '미래 날짜는 입력할 수 없습니다'),
});

export type BookInfoInput = z.infer<typeof bookInfoSchema>;
```

## 컴포넌트 상세 설명

### BookInfoForm 컴포넌트

**역할**: 전체 폼 로직 관리, 상태 조율, API 호출

**주요 기능**:
- React Hook Form 초기화 및 관리
- localStorage를 통한 폼 데이터 자동 저장/복원
- API 호출 로직 및 에러 처리
- 자식 컴포넌트들에 상태와 핸들러 전달

**Props**: 없음 (독립적 컴포넌트)

**상태**:
- `form`: React Hook Form instance
- `isLoading`: API 호출 중 여부
- `result`: API 응답 (JSON + XML)
- `error`: 에러 메시지

```typescript
// 초기화 함수
const handleReset = () => {
  form.reset();
  localStorage.removeItem(STORAGE_KEY);
  setResult(null);
  setError(null);
};

// 제출 함수
const onSubmit = async (data: BookInfoInput) => {
  setIsLoading(true);
  setError(null);
  try {
    const response = await apiClient.buildKORMARC(data);
    setResult(response);
  } catch (err) {
    setError(err.message || '요청 중 오류가 발생했습니다');
  } finally {
    setIsLoading(false);
  }
};
```

### ISBNInput 컴포넌트

**역할**: ISBN 필드 입력 및 실시간 검증

**주요 기능**:
- 형식 검증 (10-13자 숫자)
- 실시간 체크섬 검증
- 검증 상태 시각화 (success/error)

**Props**:
```typescript
interface ISBNInputProps {
  field: ControllerRenderProps;
  error?: FieldError;
}
```

### ValidationStatus 컴포넌트

**역할**: 5단계 검증 상태를 색상으로 표시

**상태 정의**:
- **회색**: 미입력 (empty)
- **노랑**: 입력 중 (inputting)
- **녹색**: 검증됨 (valid)
- **빨강**: 오류 (error)
- **회색**: 비활성화 (disabled)

**Props**:
```typescript
interface ValidationStatusProps {
  fields: {
    isbn: { isDirty: boolean; isValid: boolean; };
    title: { isDirty: boolean; isValid: boolean; };
    author: { isDirty: boolean; isValid: boolean; };
    publisher: { isDirty: boolean; isValid: boolean; };
    publicationYear: { isDirty: boolean; isValid: boolean; };
  };
}
```

### KORMARCPreview 컴포넌트

**역할**: JSON/XML 탭 결과 표시

**주요 기능**:
- 탭 전환 (JSON ↔ XML)
- 문법 강조 (syntax highlighting)
- 응답성 있는 레이아웃

**Props**:
```typescript
interface KORMARCPreviewProps {
  json: string;
  xml: string;
  isLoading?: boolean;
}
```

### ExportButtons 컴포넌트

**역할**: 결과 내보내기 기능

**주요 기능**:
- JSON 파일 다운로드
- XML 파일 다운로드
- 클립보드 복사 (JSON 또는 XML)

**Props**:
```typescript
interface ExportButtonsProps {
  json: string;
  xml: string;
  onCopySuccess?: () => void;
}
```

### LoadingSpinner 컴포넌트

**역할**: API 호출 중 로딩 상태 표시

**주요 기능**:
- 애니메이션 스피너
- 로딩 메시지 표시

**Props**:
```typescript
interface LoadingSpinnerProps {
  message?: string;
}
```

## API 통합

### Next.js API 라우트: /api/kormarc

**목적**: 백엔드 API 프록시 역할

**구현**:
```typescript
// app/api/kormarc/route.ts
export async function POST(request: Request) {
  const body = await request.json();

  // 백엔드 API 호출
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/kormarc/build`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }
  );

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

### API 클라이언트: lib/api-client.ts

**목적**: API 호출을 위한 재사용 가능한 유틸리티

```typescript
export const apiClient = {
  async buildKORMARC(data: BookInfoInput): Promise<KORMARCResponse> {
    const response = await fetch('/api/kormarc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '요청 실패');
    }

    return response.json();
  },
};
```

## localStorage 통합

### 자동 저장 기능

폼 데이터가 변경될 때마다 localStorage에 자동 저장:

```typescript
const STORAGE_KEY = 'kormarc_form_data';

const saveToLocalStorage = (data: BookInfoInput) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Failed to save to localStorage:', error);
  }
};

const loadFromLocalStorage = (): Partial<BookInfoInput> => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Failed to load from localStorage:', error);
    return {};
  }
};
```

## 테스트 전략

### 테스트 커버리지

- **전체**: 84.41%
- **컴포넌트**: 77.77%
- **유틸리티**: 100%

### 테스트 유형

**1. 단위 테스트**
- 검증 스키마 테스트
- API 클라이언트 모킹 테스트
- 유틸리티 함수 테스트

**2. 컴포넌트 테스트** (68개)
- 렌더링 테스트
- 사용자 상호작용 테스트
- 폼 제출 테스트
- 에러 처리 테스트

**3. 통합 테스트**
- 전체 폼 워크플로우 테스트
- API 통합 테스트
- localStorage 동작 테스트

### 테스트 실행

```bash
# 모든 테스트 실행
npm test

# 테스트 커버리지 리포트
npm run test:coverage

# Vitest UI (대화형)
npm run test:ui

# 특정 파일 테스트
npm test -- BookInfoForm.test.tsx
```

## 성능 최적화

### 빌드 최적화

- **Next.js 번들 분석**: `npm run build -- --analyze`
- **코드 분할**: 동적 import 사용
- **Tree shaking**: ES modules 활용

### 런타임 최적화

- **메모이제이션**: React.memo, useMemo 활용
- **레이아웃 시프트**: 고정 크기 설정
- **이미지 최적화**: Next.js Image 컴포넌트 (준비됨)

### 성능 기준

- **FCP** (First Contentful Paint): < 1.5초
- **API 응답 시간 (P95)**: < 200ms
- **번들 크기** (gzipped): < 100KB
- **Lighthouse 성능**: ≥ 90

## 보안 아키텍처

### 입력 검증

**클라이언트 측** (Zod):
- 타입 안전성
- 스키마 검증
- 커스텀 규칙 지원

**서버 측** (백엔드):
- 재검증 수행
- 비즈니스 로직 검증

### XSS 방지

**React 자동 이스케이프**:
```typescript
// 안전함 - React가 자동으로 이스케이프함
<p>{userInput}</p>

// 위험함 - dangerouslySetInnerHTML 사용 금지
<p dangerouslySetInnerHTML={{ __html: userInput }} />
```

### CSRF 방지

- CORS 설정 (Next.js 기본)
- SameSite 쿠키 정책
- Origin 검증

## 접근성 (WCAG 2.1 AA)

### 시맨틱 HTML

```html
<form>
  <label htmlFor="isbn">ISBN</label>
  <input
    id="isbn"
    type="text"
    aria-label="ISBN 입력"
    aria-describedby="isbn-error"
  />
  <span id="isbn-error" role="alert">{error}</span>
</form>
```

### 키보드 네비게이션

- Tab: 요소 이동
- Enter: 버튼 클릭, 폼 제출
- Escape: 모달/팝업 닫기

### 스크린 리더 호환

- aria-label, aria-describedby 사용
- role 속성 설정
- role="alert" for 오류 메시지

### 색상 대비

- AA 준수: 4.5:1 (일반 텍스트)
- AAA 준수: 7:1 (강조 텍스트)

## 배포

### Vercel 배포 (권장)

```bash
# 프로젝트 연결
vercel link

# 배포
vercel deploy --prod
```

### Docker 배포

```bash
# 이미지 빌드
docker build -t kormarc-frontend .

# 컨테이너 실행
docker run -p 3000:3000 kormarc-frontend
```

## 개발 워크플로우

### 로컬 개발

```bash
# 의존성 설치
npm install

# 개발 서버 실행 (핫 리로드)
npm run dev
# http://localhost:3000에서 접근
```

### 테스트

```bash
# 단위 테스트
npm test

# 커버리지
npm run test:coverage

# Vitest UI
npm run test:ui

# E2E 테스트 (준비됨)
npm run test:e2e
```

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start

# 빌드 분석
npm run build -- --analyze
```

## 문제 해결

### 일반적인 문제

**1. API 연결 오류**
- 백엔드 서버 실행 확인
- CORS 설정 확인
- 환경 변수 설정 확인

**2. localStorage 오류**
- 브라우저 캐시 삭제
- localStorage 할당량 확인
- 개인정보 보호 모드 확인

**3. 폼 검증 문제**
- Zod 스키마 확인
- React Hook Form 설정 확인
- 필드 이름 일치 확인

## 관련 문서

- [프론트엔드 개발 가이드](FRONTEND_GUIDE.md)
- [API 통합 가이드](API_INTEGRATION.md)
- [테스트 전략 및 모범 사례](FRONTEND_TESTING.md)
- [SPEC 문서](.moai/specs/SPEC-FRONTEND-001/spec.md)
- [백엔드 아키텍처](ARCHITECTURE_WEB.md)

## 버전 히스토리

- **v1.0.0** (2026-01-11): 초기 구현 완료
  - 모든 HIGH 우선순위 기능 구현
  - 68개 테스트 통과 (84.41% 커버리지)
  - 프로덕션 배포 준비 완료
