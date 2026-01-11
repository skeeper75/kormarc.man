# SPEC-FRONTEND-001: 프론트엔드 개발 가이드

## 개요

이 문서는 KORMARC 프론트엔드 개발자를 위한 실무 가이드입니다. 컴포넌트 개발 방법, React Hook Form + Zod 패턴, 테스트 작성, 그리고 모범 사례를 다룹니다.

## 개발 환경 설정

### 필수 소프트웨어

- **Node.js**: 20.0+ (nvm 추천)
- **npm**: 10.0+ (또는 pnpm)
- **VS Code**: 최신 버전 (또는 선호하는 IDE)

### 프로젝트 초기 설정

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저에서 확인
# http://localhost:3000
```

### VS Code 확장 추천

- **ES7+ React/Redux/React-Native snippets**: dsznajder.es7-react-js-snippets
- **TypeScript Vue Plugin (Volar)**: Vue.volar
- **Tailwind CSS IntelliSense**: bradlc.vscode-tailwindcss
- **Prettier - Code formatter**: esbenp.prettier-vscode
- **ESLint**: dbaeumer.vscode-eslint

## 컴포넌트 개발 패턴

### 1. 함수형 컴포넌트 기본 구조

```typescript
'use client' // Next.js App Router를 위한 클라이언트 컴포넌트 마크

import React from 'react'

interface ComponentProps {
  // 프로퍼티 정의
  title: string
  onSubmit?: (data: any) => void
}

/**
 * 컴포넌트 설명
 * - 역할
 * - 주요 기능
 */
export const MyComponent: React.FC<ComponentProps> = ({ title, onSubmit }) => {
  // 상태 선언
  const [state, setState] = React.useState('')

  // 이펙트 정의
  React.useEffect(() => {
    // 설정 코드
  }, [])

  // 핸들러 함수
  const handleAction = () => {
    // 로직
  }

  // 렌더링
  return (
    <div className="container">
      <h1>{title}</h1>
      {/* 컨텐츠 */}
    </div>
  )
}
```

### 2. TypeScript 프로퍼티 정의

```typescript
// ❌ 나쁜 예: 불명확한 타입
interface Props {
  data: any
  callback: Function
}

// ✅ 좋은 예: 명확한 타입
interface ButtonProps {
  label: string
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  className?: string
}

export const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
  className,
}) => {
  return (
    <button
      className={`btn btn-${variant} ${className || ''}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  )
}
```

### 3. React Hook Form과 Zod를 활용한 폼 컴포넌트

#### Zod 스키마 정의

```typescript
// lib/validators.ts
import { z } from 'zod'

// ISBN 체크섬 검증 함수
const validateISBNChecksum = (isbn: string): boolean => {
  if (isbn.length === 10) {
    // ISBN-10 검증
    let sum = 0
    for (let i = 0; i < 10; i++) {
      sum += (10 - i) * parseInt(isbn[i])
    }
    return sum % 11 === 0
  } else if (isbn.length === 13) {
    // ISBN-13 검증
    let sum = 0
    for (let i = 0; i < 13; i++) {
      const weight = i % 2 === 0 ? 1 : 3
      sum += weight * parseInt(isbn[i])
    }
    return sum % 10 === 0
  }
  return false
}

// 검증 스키마
export const bookInfoSchema = z.object({
  isbn: z
    .string()
    .min(10, '10자 이상의 ISBN이 필요합니다')
    .max(13, '13자 이하의 ISBN이 필요합니다')
    .regex(/^[0-9]+$/, '숫자만 입력 가능합니다')
    .refine(validateISBNChecksum, '유효하지 않은 ISBN입니다'),

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
})

export type BookInfoInput = z.infer<typeof bookInfoSchema>
```

#### 폼 컴포넌트 구현

```typescript
'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { bookInfoSchema, type BookInfoInput } from '@lib/validators'

export const BookInfoForm: React.FC = () => {
  const [isLoading, setIsLoading] = React.useState(false)
  const [result, setResult] = React.useState<any>(null)
  const [error, setError] = React.useState<string | null>(null)

  const form = useForm<BookInfoInput>({
    resolver: zodResolver(bookInfoSchema),
    mode: 'onChange', // 입력할 때마다 검증
    defaultValues: {
      isbn: '',
      title: '',
      author: '',
      publisher: '',
      publicationYear: new Date().getFullYear(),
    },
  })

  // 자동 저장
  React.useEffect(() => {
    const subscription = form.watch((data) => {
      localStorage.setItem('kormarc_form_data', JSON.stringify(data))
    })
    return () => subscription.unsubscribe()
  }, [form])

  // 폼 제출
  const onSubmit = async (data: BookInfoInput) => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/kormarc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('API 요청에 실패했습니다')
      }

      const result = await response.json()
      setResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {/* ISBN 필드 */}
      <div>
        <label htmlFor="isbn" className="block font-medium">
          ISBN *
        </label>
        <input
          {...form.register('isbn')}
          id="isbn"
          type="text"
          placeholder="9788954687065"
          className="w-full border rounded px-3 py-2"
        />
        {form.formState.errors.isbn && (
          <span className="text-red-600 text-sm">
            {form.formState.errors.isbn.message}
          </span>
        )}
      </div>

      {/* 제목 필드 */}
      <div>
        <label htmlFor="title" className="block font-medium">
          제목 *
        </label>
        <input
          {...form.register('title')}
          id="title"
          type="text"
          placeholder="도서 제목"
          className="w-full border rounded px-3 py-2"
        />
        {form.formState.errors.title && (
          <span className="text-red-600 text-sm">
            {form.formState.errors.title.message}
          </span>
        )}
      </div>

      {/* 저자 필드 */}
      <div>
        <label htmlFor="author" className="block font-medium">
          저자 *
        </label>
        <input
          {...form.register('author')}
          id="author"
          type="text"
          placeholder="저자명"
          className="w-full border rounded px-3 py-2"
        />
        {form.formState.errors.author && (
          <span className="text-red-600 text-sm">
            {form.formState.errors.author.message}
          </span>
        )}
      </div>

      {/* 출판사 필드 */}
      <div>
        <label htmlFor="publisher" className="block font-medium">
          출판사 *
        </label>
        <input
          {...form.register('publisher')}
          id="publisher"
          type="text"
          placeholder="출판사명"
          className="w-full border rounded px-3 py-2"
        />
        {form.formState.errors.publisher && (
          <span className="text-red-600 text-sm">
            {form.formState.errors.publisher.message}
          </span>
        )}
      </div>

      {/* 발행년 필드 */}
      <div>
        <label htmlFor="year" className="block font-medium">
          발행년 *
        </label>
        <input
          {...form.register('publicationYear', { valueAsNumber: true })}
          id="year"
          type="number"
          placeholder={new Date().getFullYear().toString()}
          className="w-full border rounded px-3 py-2"
        />
        {form.formState.errors.publicationYear && (
          <span className="text-red-600 text-sm">
            {form.formState.errors.publicationYear.message}
          </span>
        )}
      </div>

      {/* 버튼 그룹 */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isLoading || !form.formState.isValid}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {isLoading ? '생성 중...' : 'KORMARC 생성'}
        </button>
        <button
          type="button"
          onClick={() => form.reset()}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded"
        >
          초기화
        </button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 text-red-800">
          {error}
        </div>
      )}

      {/* 결과 표시 */}
      {result && (
        <div className="bg-green-50 border border-green-200 rounded p-4">
          <h3 className="font-semibold mb-2">결과</h3>
          <pre className="bg-white border rounded p-2 text-sm overflow-auto">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </form>
  )
}
```

## 테스트 작성 패턴

### 1. 컴포넌트 렌더링 테스트

```typescript
// __tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '@components/Button'

describe('Button', () => {
  it('should render button with label', () => {
    render(<Button label="Click me" onClick={() => {}} />)

    const button = screen.getByRole('button', { name: /click me/i })
    expect(button).toBeInTheDocument()
  })

  it('should call onClick when clicked', async () => {
    const handleClick = vi.fn()
    const { user } = render(
      <Button label="Click" onClick={handleClick} />
    )

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('should be disabled when disabled prop is true', () => {
    render(<Button label="Disabled" onClick={() => {}} disabled={true} />)

    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })
})
```

### 2. 폼 컴포넌트 테스트

```typescript
// __tests__/components/BookInfoForm.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BookInfoForm } from '@components/BookInfoForm'
import * as api from '@lib/api-client'

vi.mock('@lib/api-client')

describe('BookInfoForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render all form fields', () => {
    render(<BookInfoForm />)

    expect(screen.getByLabelText(/isbn/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/제목/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/저자/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/출판사/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/발행년/i)).toBeInTheDocument()
  })

  it('should disable submit button when form is invalid', async () => {
    const { user } = render(<BookInfoForm />)

    const submitButton = screen.getByRole('button', { name: /kormarc 생성/i })
    expect(submitButton).toBeDisabled()
  })

  it('should submit form with valid data', async () => {
    const mockBuild = vi.fn().mockResolvedValue({
      json: '{}',
      xml: '<record></record>',
    })
    vi.mocked(api.apiClient.buildKORMARC).mockImplementation(mockBuild)

    const { user } = render(<BookInfoForm />)

    // 폼 필드 채우기
    await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
    await user.type(screen.getByLabelText(/제목/i), '테스트 도서')
    await user.type(screen.getByLabelText(/저자/i), '테스트 저자')
    await user.type(screen.getByLabelText(/출판사/i), '테스트 출판사')
    await user.clear(screen.getByLabelText(/발행년/i))
    await user.type(screen.getByLabelText(/발행년/i), '2026')

    // 제출
    await user.click(screen.getByRole('button', { name: /kormarc 생성/i }))

    // API 호출 확인
    await waitFor(() => {
      expect(mockBuild).toHaveBeenCalledWith(
        expect.objectContaining({
          isbn: '9788954687065',
          title: '테스트 도서',
        })
      )
    })
  })

  it('should display error message on API failure', async () => {
    const mockError = new Error('API 오류')
    vi.mocked(api.apiClient.buildKORMARC).mockRejectedValue(mockError)

    const { user } = render(<BookInfoForm />)

    // 폼 채우고 제출...
    await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
    // ... 다른 필드들 ...
    await user.click(screen.getByRole('button', { name: /kormarc 생성/i }))

    // 에러 메시지 확인
    await waitFor(() => {
      expect(screen.getByText(/api 오류/i)).toBeInTheDocument()
    })
  })
})
```

### 3. 검증 스키마 테스트

```typescript
// __tests__/lib/validators.test.ts
import { bookInfoSchema } from '@lib/validators'

describe('bookInfoSchema', () => {
  it('should validate correct data', () => {
    const validData = {
      isbn: '9788954687065',
      title: '테스트',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    const result = bookInfoSchema.safeParse(validData)
    expect(result.success).toBe(true)
  })

  it('should reject invalid ISBN', () => {
    const invalidData = {
      isbn: '1234567890', // 유효하지 않은 체크섬
      title: '테스트',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    const result = bookInfoSchema.safeParse(invalidData)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues[0].message).toContain('유효하지 않은 ISBN')
    }
  })

  it('should reject missing required fields', () => {
    const incompleteData = {
      isbn: '9788954687065',
      title: '',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    const result = bookInfoSchema.safeParse(incompleteData)
    expect(result.success).toBe(false)
  })
})
```

## 스타일 가이드

### Tailwind CSS 활용

```typescript
// ✅ 좋은 예: 명확한 클래스 이름
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50" />

// ❌ 나쁜 예: 불명확한 클래스 조합
<button className="p-4 bg-blue rounded" />

// ✅ 반응형 디자인
<div className="w-full md:w-1/2 lg:w-1/4 px-2">
  Content
</div>

// ✅ 다크 모드 지원
<button className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white" />
```

### 조건부 클래스 처리

```typescript
// ✅ 좋은 예: clsx 활용
import clsx from 'clsx'

interface ButtonProps {
  variant: 'primary' | 'secondary'
  size: 'sm' | 'md' | 'lg'
}

const buttonStyles = {
  variant: {
    primary: 'bg-blue-600 text-white',
    secondary: 'bg-gray-200 text-gray-900',
  },
  size: {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  },
}

export const Button: React.FC<ButtonProps> = ({ variant, size, ...props }) => (
  <button
    className={clsx(
      buttonStyles.variant[variant],
      buttonStyles.size[size],
      'rounded font-medium transition'
    )}
    {...props}
  />
)
```

## 모범 사례

### 1. 파일 구조

```
app/
├── components/
│   ├── Button.tsx                # 공유 컴포넌트
│   ├── BookInfoForm.tsx          # 폼 컴포넌트
│   └── index.ts                  # 배럴 export
├── lib/
│   ├── validators.ts             # Zod 스키마
│   ├── api-client.ts             # API 유틸
│   └── utils.ts                  # 헬퍼 함수
├── api/                          # API 라우트
└── __tests__/                    # 테스트 파일
```

### 2. 컴포넌트 분리

```typescript
// ❌ 나쁜 예: 모든 로직이 한 컴포넌트에
const BookForm = () => {
  const [form, setForm] = useState(...)
  const [isLoading, setIsLoading] = useState(...)
  // 200+ 줄의 코드
}

// ✅ 좋은 예: 책임 분리
const BookForm = () => <form>/* 폼 구조 */</form>
const FormInputField = ({ name }) => <input />
const FormSubmitButton = ({ isValid }) => <button />
const FormErrorDisplay = ({ error }) => <div>{error}</div>
```

### 3. 에러 처리

```typescript
// ❌ 나쁜 예
try {
  const response = await fetch(...)
  const data = await response.json()
  setResult(data)
} catch (e) {
  console.log(e)
}

// ✅ 좋은 예
try {
  const response = await fetch(...)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: 요청 실패`)
  }
  const data = await response.json()
  setResult(data)
} catch (error) {
  const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류'
  setError(errorMessage)
  console.error('API 호출 실패:', errorMessage)
}
```

### 4. 타입 안전성

```typescript
// ❌ 나쁜 예: any 타입 사용
const handleSubmit = (data: any) => {
  // ...
}

// ✅ 좋은 예: 명확한 타입
interface FormData {
  isbn: string
  title: string
  author: string
  publisher: string
  publicationYear: number
}

const handleSubmit = (data: FormData) => {
  // ...
}
```

## 디버깅 팁

### 1. React DevTools

```bash
# Chrome 확장 설치
# React Developer Tools 사용
# - 컴포넌트 트리 확인
# - Props 및 상태 검사
# - 성능 프로파일링
```

### 2. 콘솔 로깅

```typescript
// ✅ 좋은 예: 조건부 로깅
const isDev = process.env.NODE_ENV === 'development'

if (isDev) {
  console.log('폼 데이터:', formData)
}
```

### 3. Next.js 디버깅

```bash
# VS Code에서 디버깅
# .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/.bin/next",
      "args": ["dev"],
      "console": "integratedTerminal",
      "internalConsoleOptions": "neverOpen"
    }
  ]
}
```

## 최적화 기법

### 1. 메모이제이션

```typescript
// useMemo: 계산 결과 캐싱
const expensiveValue = React.useMemo(() => {
  return calculateExpensive(data)
}, [data])

// useCallback: 함수 참조 유지
const handleSubmit = React.useCallback((data) => {
  onSubmit(data)
}, [onSubmit])
```

### 2. 코드 분할

```typescript
// 동적 import로 번들 크기 감소
const HeavyComponent = React.lazy(() => import('./HeavyComponent'))

export const App = () => (
  <React.Suspense fallback={<div>로딩 중...</div>}>
    <HeavyComponent />
  </React.Suspense>
)
```

### 3. 성능 모니터링

```bash
# 번들 분석
npm run build -- --analyze

# 성능 메트릭
# Lighthouse 실행
npm run lighthouse
```

## 참고 자료

- [React 공식 문서](https://react.dev)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [React Hook Form](https://react-hook-form.com)
- [Zod 검증](https://zod.dev)
- [Tailwind CSS](https://tailwindcss.com)
