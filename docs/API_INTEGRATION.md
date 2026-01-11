# SPEC-FRONTEND-001: API 통합 가이드

## 개요

이 문서는 프론트엔드와 백엔드 API 간의 통합 방법을 설명합니다. Next.js API 라우트를 통한 프록시 패턴, 에러 처리, 그리고 실제 통합 예제를 포함합니다.

## 아키텍처 개요

### 통합 흐름

```
클라이언트 (React)
    ↓
Next.js API Route (/api/kormarc)
    ↓
백엔드 API (FastAPI)
    ↓
응답 반환
    ↓
클라이언트 렌더링
```

### 프로토콜

- **프로토콜**: HTTP/HTTPS
- **Method**: POST
- **Content-Type**: application/json
- **인증**: 현재 필요 없음 (향후 추가 예상)

## 백엔드 API 명세

### 1. KORMARC 생성 엔드포인트

#### 엔드포인트
```
POST /api/kormarc/build
```

#### 요청 스키마

```typescript
interface KORMARCBuildRequest {
  isbn: string           // 10-13자 숫자 (유효한 체크섬)
  title: string          // 1-200자
  author: string         // 1-100자
  publisher: string      // 1-100자
  publicationYear: number // 1900-현재년도
}
```

#### 요청 예제

```bash
curl -X POST http://localhost:8000/api/kormarc/build \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "9788954687065",
    "title": "한국 도서관 자동화",
    "author": "홍길동",
    "publisher": "출판사",
    "publicationYear": 2026
  }'
```

#### 응답 스키마

```typescript
interface KORMARCBuildResponse {
  json: string           // JSON 형식 KORMARC 레코드
  xml: string           // XML 형식 KORMARC 레코드
  validationTiers: {
    tier1: boolean      // 기본 검증
    tier2: boolean      // ISBN 검증
    tier3: boolean      // 필수 필드 검증
    tier4: boolean      // 비즈니스 로직 검증
    tier5: boolean      // 최종 검증
  }
}
```

#### 응답 예제

```json
{
  "json": "{\"kormarc\": {...}}",
  "xml": "<record xmlns=\"http://www.loc.gov/MARC21/slim\">...</record>",
  "validationTiers": {
    "tier1": true,
    "tier2": true,
    "tier3": true,
    "tier4": true,
    "tier5": true
  }
}
```

### 2. 헬스 체크 엔드포인트

#### 엔드포인트
```
GET /health
```

#### 응답
```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T15:30:00Z"
}
```

## Next.js API 라우트 구현

### app/api/kormarc/route.ts

```typescript
import { NextRequest, NextResponse } from 'next/server'

interface KORMARCBuildRequest {
  isbn: string
  title: string
  author: string
  publisher: string
  publicationYear: number
}

interface KORMARCBuildResponse {
  json: string
  xml: string
  validationTiers: Record<string, boolean>
}

export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    // 요청 본문 파싱
    const body: KORMARCBuildRequest = await request.json()

    // 기본 검증
    if (!body.isbn || !body.title || !body.author || !body.publisher || !body.publicationYear) {
      return NextResponse.json(
        { error: '필수 필드가 누락되었습니다' },
        { status: 400 }
      )
    }

    // 백엔드 API 호출
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/kormarc/build`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    // 응답 처리
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          error: errorData.message || `백엔드 API 오류: ${response.status}`,
        },
        { status: response.status }
      )
    }

    const data: KORMARCBuildResponse = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('[API Error]', error)

    // 네트워크 오류
    if (error instanceof Error && error.message.includes('fetch')) {
      return NextResponse.json(
        { error: '백엔드 서버에 연결할 수 없습니다' },
        { status: 503 }
      )
    }

    // 일반 오류
    return NextResponse.json(
      { error: 'API 요청 처리 중 오류가 발생했습니다' },
      { status: 500 }
    )
  }
}
```

## API 클라이언트 구현

### app/lib/api-client.ts

```typescript
export interface BookInfoInput {
  isbn: string
  title: string
  author: string
  publisher: string
  publicationYear: number
}

export interface KORMARCResponse {
  json: string
  xml: string
  validationTiers: Record<string, boolean>
}

export interface ApiError {
  message: string
  status?: number
}

/**
 * API 클라이언트 유틸리티
 * 프론트엔드와 백엔드 간의 통신을 처리합니다
 */
export const apiClient = {
  /**
   * KORMARC 레코드 생성
   * @param data 도서 정보
   * @returns KORMARC 응답 (JSON + XML)
   * @throws ApiError
   */
  async buildKORMARC(data: BookInfoInput): Promise<KORMARCResponse> {
    try {
      const response = await fetch('/api/kormarc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      // 응답이 JSON이 아닌 경우 처리
      const contentType = response.headers.get('content-type')
      if (!contentType?.includes('application/json')) {
        throw new Error('유효하지 않은 응답 형식')
      }

      const responseData = await response.json()

      // HTTP 오류 처리
      if (!response.ok) {
        throw new Error(
          responseData.error || `HTTP ${response.status}: 요청 실패`
        )
      }

      return responseData
    } catch (error) {
      // 네트워크 오류
      if (error instanceof TypeError) {
        throw new Error('네트워크 오류: 서버에 연결할 수 없습니다')
      }

      // 기타 오류
      if (error instanceof Error) {
        throw error
      }

      throw new Error('알 수 없는 오류가 발생했습니다')
    }
  },

  /**
   * 헬스 체크
   * @returns 서버 상태
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch('/api/kormarc/health', {
        method: 'GET',
      })
      return response.ok
    } catch {
      return false
    }
  },
}
```

## 에러 처리 패턴

### 1. 클라이언트 측 에러 처리

```typescript
const handleSubmit = async (data: BookInfoInput) => {
  setIsLoading(true)
  setError(null)

  try {
    const result = await apiClient.buildKORMARC(data)
    setResult(result)
    // 성공 로직
  } catch (error) {
    // 에러 메시지 추출
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류'

    // 사용자 친화적인 메시지로 변환
    let userMessage = errorMessage

    if (errorMessage.includes('네트워크')) {
      userMessage = '네트워크 연결을 확인해주세요'
    } else if (errorMessage.includes('HTTP 400')) {
      userMessage = '입력한 정보를 확인해주세요'
    } else if (errorMessage.includes('HTTP 500')) {
      userMessage = '서버에 문제가 발생했습니다. 나중에 다시 시도해주세요'
    }

    setError(userMessage)
  } finally {
    setIsLoading(false)
  }
}
```

### 2. 에러 메시지 매핑

```typescript
interface ErrorMapping {
  pattern: RegExp
  message: string
}

const errorMappings: ErrorMapping[] = [
  {
    pattern: /네트워크/i,
    message: '네트워크 연결을 확인해주세요',
  },
  {
    pattern: /HTTP 400/,
    message: '입력한 정보가 올바르지 않습니다',
  },
  {
    pattern: /HTTP 401/,
    message: '인증이 필요합니다',
  },
  {
    pattern: /HTTP 403/,
    message: '접근 권한이 없습니다',
  },
  {
    pattern: /HTTP 404/,
    message: '요청한 리소스를 찾을 수 없습니다',
  },
  {
    pattern: /HTTP 500/,
    message: '서버에 문제가 발생했습니다. 나중에 다시 시도해주세요',
  },
  {
    pattern: /HTTP 503/,
    message: '서버가 일시적으로 사용 불가능합니다',
  },
]

export const mapErrorMessage = (error: Error): string => {
  for (const mapping of errorMappings) {
    if (mapping.pattern.test(error.message)) {
      return mapping.message
    }
  }
  return '오류가 발생했습니다. 나중에 다시 시도해주세요'
}
```

## 환경 변수 설정

### .env.local

```env
# 백엔드 API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# 개발 환경에서의 API URL (Vercel 배포 시)
NEXT_PUBLIC_API_URL_PRODUCTION=https://api.example.com
```

### .env.production

```env
# 프로덕션 환경 API URL
NEXT_PUBLIC_API_URL=https://api.example.com
```

## CORS 설정

### Next.js 미들웨어 (선택)

프론트엔드 라우트에서 직접 외부 API 호출 시:

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  // CORS 헤더 설정
  response.headers.set('Access-Control-Allow-Origin', process.env.NEXT_PUBLIC_API_URL)
  response.headers.set('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type')

  return response
}

export const config = {
  matcher: '/api/:path*',
}
```

## 통합 테스트

### API 모킹

```typescript
import { vi } from 'vitest'
import { apiClient } from '@lib/api-client'

describe('API Integration', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })

  it('should call buildKORMARC with correct parameters', async () => {
    const mockResponse = {
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({
        json: '{}',
        xml: '<record></record>',
      }),
    }

    global.fetch = vi.fn().mockResolvedValue(mockResponse)

    const data = {
      isbn: '9788954687065',
      title: '테스트',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    const result = await apiClient.buildKORMARC(data)

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/kormarc',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    )

    expect(result.json).toBeDefined()
    expect(result.xml).toBeDefined()
  })

  it('should handle network errors', async () => {
    global.fetch = vi.fn().mockRejectedValue(new TypeError('Network error'))

    const data = {
      isbn: '9788954687065',
      title: '테스트',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    await expect(apiClient.buildKORMARC(data)).rejects.toThrow('네트워크 오류')
  })

  it('should handle HTTP errors', async () => {
    const mockResponse = {
      ok: false,
      status: 400,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ error: '유효하지 않은 요청' }),
    }

    global.fetch = vi.fn().mockResolvedValue(mockResponse)

    const data = {
      isbn: '9788954687065',
      title: '테스트',
      author: '저자',
      publisher: '출판사',
      publicationYear: 2026,
    }

    await expect(apiClient.buildKORMARC(data)).rejects.toThrow('유효하지 않은 요청')
  })
})
```

## 성능 최적화

### 요청 캐싱 (선택)

```typescript
const cache = new Map<string, any>()
const CACHE_DURATION = 5 * 60 * 1000 // 5분

export const apiClientWithCache = {
  async buildKORMARC(data: BookInfoInput): Promise<KORMARCResponse> {
    const cacheKey = JSON.stringify(data)

    // 캐시 확인
    if (cache.has(cacheKey)) {
      const cachedEntry = cache.get(cacheKey)
      if (Date.now() - cachedEntry.timestamp < CACHE_DURATION) {
        return cachedEntry.data
      }
      cache.delete(cacheKey)
    }

    // API 호출
    const result = await apiClient.buildKORMARC(data)

    // 캐시 저장
    cache.set(cacheKey, {
      data: result,
      timestamp: Date.now(),
    })

    return result
  },
}
```

### 요청 취소

```typescript
const controller = new AbortController()

export const apiClientWithCancellation = {
  async buildKORMARC(data: BookInfoInput): Promise<KORMARCResponse> {
    try {
      const response = await fetch('/api/kormarc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new Error('요청이 취소되었습니다')
      }
      throw error
    }
  },

  cancel() {
    controller.abort()
  },
}
```

## 배포 시 주의사항

### Vercel 배포

```env
# .env.production
NEXT_PUBLIC_API_URL=https://api.kormarc.example.com
```

### 환경 변수 검증

```typescript
// lib/env-validation.ts
export const validateEnv = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  if (!apiUrl) {
    throw new Error('NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다')
  }

  return { apiUrl }
}
```

## 문제 해결

### 1. CORS 오류

**증상**: `Access-Control-Allow-Origin` 오류

**해결책**:
- 백엔드 CORS 설정 확인
- 프론트엔드 API 라우트 사용 (프록시 패턴)
- 환경 변수 확인

### 2. 연결 거부

**증상**: `ERR_CONNECTION_REFUSED`

**해결책**:
- 백엔드 서버 실행 확인
- 포트 번호 확인
- 방화벽 설정 확인

### 3. 응답 파싱 오류

**증상**: `Invalid JSON response`

**해결책**:
- Content-Type 헤더 확인
- 응답 형식 검증
- 백엔드 에러 응답 확인

## 참고 자료

- [Next.js API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
