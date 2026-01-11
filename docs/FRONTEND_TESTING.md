# SPEC-FRONTEND-001: 프론트엔드 테스트 전략

## 개요

KORMARC 프론트엔드의 종합적인 테스트 전략 및 실행 가이드입니다. Vitest를 이용한 단위 테스트, React Testing Library를 이용한 컴포넌트 테스트, 그리고 Playwright를 이용한 E2E 테스트를 다룹니다.

## 테스트 현황

### 테스트 통계

- **테스트 총 개수**: 68개
- **통과 테스트**: 68개 (100%)
- **실패 테스트**: 0개
- **테스트 커버리지**: 84.41%
- **컴포넌트 커버리지**: 77.77%
- **유틸리티 커버리지**: 100%

### 테스트 분포

- **컴포넌트 테스트**: 58개 (렌더링, 상호작용, 에러 처리)
- **검증 테스트**: 10개 (Zod 스키마)

## Vitest 설정

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['__tests__/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        '__tests__/',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.test.tsx',
      ],
    },
  },
  resolve: {
    alias: {
      '@components': path.resolve(__dirname, './app/components'),
      '@lib': path.resolve(__dirname, './app/lib'),
      '@': path.resolve(__dirname, './'),
    },
  },
})
```

### 테스트 실행 명령어

```bash
# 전체 테스트 실행
npm test

# 감시 모드 (개발 중)
npm test -- --watch

# 커버리지 리포트 생성
npm run test:coverage

# Vitest UI (대화형)
npm run test:ui

# 특정 파일만 테스트
npm test -- BookInfoForm.test.tsx

# 특정 패턴의 테스트만 실행
npm test -- --grep "폼 제출"
```

## 단위 테스트

### 검증 스키마 테스트 (lib/validators.test.ts)

```typescript
import { describe, it, expect } from 'vitest'
import { bookInfoSchema } from '@lib/validators'

describe('bookInfoSchema', () => {
  describe('ISBN 검증', () => {
    it('should accept valid ISBN-13', () => {
      const data = {
        isbn: '9788954687065',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(true)
    })

    it('should accept valid ISBN-10', () => {
      const data = {
        isbn: '0306406713',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(true)
    })

    it('should reject invalid ISBN checksum', () => {
      const data = {
        isbn: '1234567890',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
      expect(result.error?.issues[0].message).toContain('유효하지 않은 ISBN')
    })

    it('should reject non-numeric ISBN', () => {
      const data = {
        isbn: '978895468706X',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })

    it('should reject short ISBN', () => {
      const data = {
        isbn: '123456789',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })

    it('should reject long ISBN', () => {
      const data = {
        isbn: '978895468706512',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })
  })

  describe('필드 검증', () => {
    it('should reject empty title', () => {
      const data = {
        isbn: '9788954687065',
        title: '',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })

    it('should reject future publication year', () => {
      const data = {
        isbn: '9788954687065',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: new Date().getFullYear() + 1,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })

    it('should reject publication year before 1900', () => {
      const data = {
        isbn: '9788954687065',
        title: '테스트',
        author: '저자',
        publisher: '출판사',
        publicationYear: 1899,
      }

      const result = bookInfoSchema.safeParse(data)
      expect(result.success).toBe(false)
    })
  })
})
```

## 컴포넌트 테스트

### React Testing Library 기본 패턴

#### 1. 테스트 설정 (setup.ts)

```typescript
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// 각 테스트 후 정리
afterEach(() => {
  cleanup()
  localStorage.clear()
})

// fetch 모킹
global.fetch = vi.fn()
```

#### 2. BookInfoForm 컴포넌트 테스트

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BookInfoForm } from '@components/BookInfoForm'

describe('BookInfoForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  describe('렌더링', () => {
    it('should render all form fields', () => {
      render(<BookInfoForm />)

      expect(screen.getByLabelText(/isbn/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/제목/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/저자/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/출판사/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/발행년/i)).toBeInTheDocument()
    })

    it('should render submit button', () => {
      render(<BookInfoForm />)
      expect(screen.getByRole('button', { name: /kormarc 생성/i })).toBeInTheDocument()
    })

    it('should render reset button', () => {
      render(<BookInfoForm />)
      expect(screen.getByRole('button', { name: /초기화/i })).toBeInTheDocument()
    })
  })

  describe('폼 검증', () => {
    it('should disable submit button when form is invalid', async () => {
      const { user } = render(<BookInfoForm />)
      const submitButton = screen.getByRole('button', { name: /kormarc 생성/i })

      // 초기에는 비활성화
      expect(submitButton).toBeDisabled()

      // 유효한 데이터로 채우기
      await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
      await user.type(screen.getByLabelText(/제목/i), '테스트 도서')
      await user.type(screen.getByLabelText(/저자/i), '테스트 저자')
      await user.type(screen.getByLabelText(/출판사/i), '테스트 출판사')

      // 활성화됨
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })

    it('should show error for invalid ISBN', async () => {
      const { user } = render(<BookInfoForm />)

      const isbnInput = screen.getByLabelText(/isbn/i)
      await user.type(isbnInput, '1234567890')
      await user.click(screen.getByLabelText(/제목/i)) // 다른 필드로 포커스 이동

      await waitFor(() => {
        expect(screen.getByText(/유효하지 않은 isbn/i)).toBeInTheDocument()
      })
    })

    it('should show error for empty required fields', async () => {
      const { user } = render(<BookInfoForm />)

      const titleInput = screen.getByLabelText(/제목/i)
      await user.type(titleInput, 'test')
      await user.clear(titleInput)
      await user.click(screen.getByLabelText(/isbn/i)) // 다른 필드로 포커스 이동

      await waitFor(() => {
        expect(screen.getByText(/제목을 입력하세요/i)).toBeInTheDocument()
      })
    })
  })

  describe('폼 제출', () => {
    it('should submit form with valid data', async () => {
      const mockResponse = {
        ok: true,
        json: async () => ({
          json: '{}',
          xml: '<record></record>',
        }),
      }
      global.fetch = vi.fn().mockResolvedValue(mockResponse)

      const { user } = render(<BookInfoForm />)

      // 폼 채우기
      await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
      await user.type(screen.getByLabelText(/제목/i), '테스트 도서')
      await user.type(screen.getByLabelText(/저자/i), '테스트 저자')
      await user.type(screen.getByLabelText(/출판사/i), '테스트 출판사')

      // 제출
      const submitButton = screen.getByRole('button', { name: /kormarc 생성/i })
      await user.click(submitButton)

      // API 호출 확인
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/kormarc',
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
            }),
          })
        )
      })
    })

    it('should show loading state during submission', async () => {
      let resolveResponse: Function
      const mockPromise = new Promise((resolve) => {
        resolveResponse = resolve
      })

      global.fetch = vi.fn().mockReturnValue(mockPromise)

      const { user } = render(<BookInfoForm />)

      // 유효한 데이터 입력
      await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
      await user.type(screen.getByLabelText(/제목/i), '테스트 도서')
      await user.type(screen.getByLabelText(/저자/i), '테스트 저자')
      await user.type(screen.getByLabelText(/출판사/i), '테스트 출판사')

      // 제출
      const submitButton = screen.getByRole('button', { name: /kormarc 생성/i })
      await user.click(submitButton)

      // 로딩 상태 확인
      expect(screen.getByRole('button', { name: /생성 중/i })).toBeInTheDocument()

      // 응답 완료
      resolveResponse!({
        ok: true,
        json: async () => ({
          json: '{}',
          xml: '<record></record>',
        }),
      })

      // 로딩 상태 해제
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /kormarc 생성/i })).toBeInTheDocument()
      })
    })

    it('should display error message on API failure', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('네트워크 오류'))

      const { user } = render(<BookInfoForm />)

      // 유효한 데이터 입력
      await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
      await user.type(screen.getByLabelText(/제목/i), '테스트 도서')
      await user.type(screen.getByLabelText(/저자/i), '테스트 저자')
      await user.type(screen.getByLabelText(/출판사/i), '테스트 출판사')

      // 제출
      await user.click(screen.getByRole('button', { name: /kormarc 생성/i }))

      // 에러 메시지 확인
      await waitFor(() => {
        expect(screen.getByText(/네트워크 오류/i)).toBeInTheDocument()
      })
    })
  })

  describe('localStorage 통합', () => {
    it('should save form data to localStorage', async () => {
      const { user } = render(<BookInfoForm />)

      const isbnInput = screen.getByLabelText(/isbn/i)
      await user.type(isbnInput, '9788954687065')

      await waitFor(() => {
        const saved = localStorage.getItem('kormarc_form_data')
        expect(saved).toBeTruthy()

        const data = JSON.parse(saved!)
        expect(data.isbn).toBe('9788954687065')
      })
    })

    it('should restore form data from localStorage', () => {
      const initialData = {
        isbn: '9788954687065',
        title: '저장된 도서',
        author: '저자',
        publisher: '출판사',
        publicationYear: 2026,
      }

      localStorage.setItem('kormarc_form_data', JSON.stringify(initialData))

      render(<BookInfoForm />)

      expect(screen.getByDisplayValue('9788954687065')).toBeInTheDocument()
      expect(screen.getByDisplayValue('저장된 도서')).toBeInTheDocument()
    })

    it('should clear localStorage on reset', async () => {
      const { user } = render(<BookInfoForm />)

      // 데이터 입력
      await user.type(screen.getByLabelText(/isbn/i), '9788954687065')

      // 초기화 버튼 클릭
      await user.click(screen.getByRole('button', { name: /초기화/i }))

      // localStorage 확인
      const saved = localStorage.getItem('kormarc_form_data')
      const data = JSON.parse(saved!)

      expect(data.isbn).toBe('')
      expect(data.title).toBe('')
    })
  })
})
```

## E2E 테스트 (Playwright)

### playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './__tests__/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E 테스트 예제

```typescript
// __tests__/e2e/book-form.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Book Form E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should create KORMARC record with valid data', async ({ page }) => {
    // 폼 필드 채우기
    await page.fill('[name="isbn"]', '9788954687065')
    await page.fill('[name="title"]', 'E2E 테스트 도서')
    await page.fill('[name="author"]', 'E2E 저자')
    await page.fill('[name="publisher"]', 'E2E 출판사')
    await page.fill('[name="publicationYear"]', '2026')

    // 제출 버튼 클릭
    await page.click('button:has-text("KORMARC 생성")')

    // 결과 표시 확인
    await expect(page.locator('text=결과')).toBeVisible()

    // JSON 탭 활성화 확인
    await expect(page.locator('button:has-text("JSON")')).toHaveClass(/active/)
  })

  test('should show validation errors for invalid data', async ({ page }) => {
    // 유효하지 않은 ISBN 입력
    await page.fill('[name="isbn"]', '1234567890')

    // 다른 필드로 포커스 이동 (blur 이벤트 발생)
    await page.fill('[name="title"]', 'test')

    // 에러 메시지 확인
    await expect(page.locator('text=유효하지 않은 ISBN')).toBeVisible()
  })

  test('should disable submit button when form is invalid', async ({ page }) => {
    const submitButton = page.locator('button:has-text("KORMARC 생성")')

    // 초기에는 비활성화
    await expect(submitButton).toBeDisabled()

    // 유효한 데이터 입력 후 활성화
    await page.fill('[name="isbn"]', '9788954687065')
    await page.fill('[name="title"]', 'test')
    await page.fill('[name="author"]', 'author')
    await page.fill('[name="publisher"]', 'publisher')

    await expect(submitButton).toBeEnabled()
  })

  test('should export result as JSON', async ({ page }) => {
    // 유효한 데이터로 KORMARC 생성
    await page.fill('[name="isbn"]', '9788954687065')
    await page.fill('[name="title"]', 'Export Test')
    await page.fill('[name="author"]', 'Author')
    await page.fill('[name="publisher"]', 'Publisher')
    await page.click('button:has-text("KORMARC 생성")')

    // 결과 표시 대기
    await page.waitForSelector('text=결과')

    // JSON 다운로드 버튼 클릭
    const downloadPromise = page.waitForEvent('download')
    await page.click('button:has-text("JSON 다운로드")')
    const download = await downloadPromise

    // 파일명 확인
    expect(download.suggestedFilename()).toContain('.json')
  })

  test('should copy result to clipboard', async ({ page, context }) => {
    // 유효한 데이터로 KORMARC 생성
    await page.fill('[name="isbn"]', '9788954687065')
    await page.fill('[name="title"]', 'Copy Test')
    await page.fill('[name="author"]', 'Author')
    await page.fill('[name="publisher"]', 'Publisher')
    await page.click('button:has-text("KORMARC 생성")')

    // 결과 표시 대기
    await page.waitForSelector('text=결과')

    // 클립보드 권한 허용
    await context.grantPermissions(['clipboard-read', 'clipboard-write'])

    // 복사 버튼 클릭
    await page.click('button:has-text("클립보드 복사")')

    // 복사 성공 메시지 확인
    await expect(page.locator('text=복사되었습니다')).toBeVisible()
  })

  test('should reset form when reset button is clicked', async ({ page }) => {
    // 데이터 입력
    await page.fill('[name="isbn"]', '9788954687065')
    await page.fill('[name="title"]', 'Reset Test')
    await page.fill('[name="author"]', 'Author')
    await page.fill('[name="publisher"]', 'Publisher')

    // 초기화 버튼 클릭
    await page.click('button:has-text("초기화")')

    // 필드가 비어있는지 확인
    await expect(page.locator('[name="isbn"]')).toHaveValue('')
    await expect(page.locator('[name="title"]')).toHaveValue('')
    await expect(page.locator('[name="author"]')).toHaveValue('')
    await expect(page.locator('[name="publisher"]')).toHaveValue('')
  })
})
```

## 테스트 실행 및 커버리지

### 테스트 실행 명령어

```bash
# 단위 테스트 실행
npm test

# 테스트 감시 모드
npm test -- --watch

# 특정 테스트 파일만 실행
npm test -- BookInfoForm.test.tsx

# 커버리지 리포트 생성
npm run test:coverage

# Vitest UI 실행
npm run test:ui

# E2E 테스트 실행 (준비 후)
npm run test:e2e

# E2E 테스트 UI 모드
npm run test:e2e -- --ui
```

### 커버리지 리포트 분석

```bash
# HTML 커버리지 리포트 생성
npm run test:coverage

# 리포트 열기
open coverage/index.html  # macOS
start coverage/index.html  # Windows
```

## 테스트 베스트 프랙티스

### 1. 명확한 테스트 이름

```typescript
// ❌ 나쁜 예: 불명확한 이름
it('test form', () => {})

// ✅ 좋은 예: 명확한 이름
it('should disable submit button when ISBN is invalid', () => {})
```

### 2. AAA 패턴 (Arrange, Act, Assert)

```typescript
it('should submit valid form data', async () => {
  // Arrange: 테스트 데이터 준비
  const { user } = render(<BookInfoForm />)

  // Act: 사용자 행동 수행
  await user.type(screen.getByLabelText(/isbn/i), '9788954687065')
  await user.click(screen.getByRole('button', { name: /submit/i }))

  // Assert: 결과 검증
  expect(global.fetch).toHaveBeenCalledWith(
    '/api/kormarc',
    expect.objectContaining({ method: 'POST' })
  )
})
```

### 3. 테스트 격리

```typescript
describe('BookInfoForm', () => {
  beforeEach(() => {
    // 각 테스트 전 초기화
    vi.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    // 각 테스트 후 정리
    cleanup()
  })

  // 테스트들...
})
```

### 4. 모킹 최소화

```typescript
// ✅ 좋은 예: 필요한 것만 모킹
global.fetch = vi.fn().mockResolvedValue({
  ok: true,
  json: async () => ({ data: 'test' }),
})

// ❌ 나쁜 예: 모든 것을 모킹
vi.mock('@lib/api-client')
vi.mock('@components/Button')
```

## 커버리지 목표

- **전체**: ≥ 85%
- **컴포넌트**: ≥ 80%
- **유틸리티**: ≥ 90%
- **라이브러리**: ≥ 100%

## 연속 통합 (CI)

### GitHub Actions 워크플로우

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v3
```

## 참고 자료

- [Vitest 공식 문서](https://vitest.dev)
- [React Testing Library](https://testing-library.com/react)
- [Playwright 문서](https://playwright.dev)
- [Testing Library Best Practices](https://testing-library.com/docs/queries/about)
