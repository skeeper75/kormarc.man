/**
 * API client for KORMARC backend integration
 * Connects to SPEC-WEB-001 FastAPI backend
 */

import type { BookInfo, KORMARCRecord, ErrorResponse, APIOptions } from './types'

/**
 * Get API base URL from environment variable
 * Defaults to localhost:8000 for development
 */
export function getApiBaseUrl(): string {
  if (typeof window !== 'undefined') {
    // Client-side: use public env variable
    return process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
  }
  // Server-side: use server env variable
  return process.env.API_BASE_URL || 'http://localhost:8000'
}

/**
 * Default API options
 */
const DEFAULT_OPTIONS: APIOptions = {
  timeout: 30000, // 30 seconds
  retries: 3,
}

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    public code: string,
    message: string,
    public status?: number,
    public details?: string
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Sleep utility for retry delay
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Fetch wrapper with retry logic and timeout
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit & { timeout?: number; retries?: number } = {}
): Promise<Response> {
  const { timeout = DEFAULT_OPTIONS.timeout, retries = DEFAULT_OPTIONS.retries, ...fetchOptions } = options

  let lastError: Error | null = null

  for (let attempt = 0; attempt <= retries!; attempt++) {
    try {
      // Create abort controller for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), timeout)

      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      return response
    } catch (error) {
      lastError = error as Error

      // Don't retry if it's not a network error
      if (error instanceof TypeError && attempt < retries!) {
        // Exponential backoff: 2^attempt * 100ms
        const delay = Math.pow(2, attempt) * 100
        await sleep(delay)
        continue
      }

      // Don't retry if it's an abort (timeout)
      if (error instanceof Error && error.name === 'AbortError') {
        throw new APIError('TIMEOUT', '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.')
      }

      throw error
    }
  }

  throw lastError || new APIError('NETWORK_ERROR', '네트워크 오류가 발생했습니다.')
}

/**
 * Handle API response and check for errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type')

  if (!response.ok) {
    // Try to parse error response
    if (contentType?.includes('application/json')) {
      const errorData = (await response.json()) as ErrorResponse
      throw new APIError(
        errorData.error.code,
        errorData.error.message,
        response.status,
        errorData.error.details
      )
    }

    // Generic HTTP error
    throw new APIError(
      `HTTP_${response.status}`,
      getErrorMessage(response.status),
      response.status
    )
  }

  // Parse successful response
  if (contentType?.includes('application/json')) {
    return response.json() as Promise<T>
  }

  throw new APIError('INVALID_RESPONSE', '유효하지 않은 응답 형식입니다.')
}

/**
 * Get user-friendly error message for HTTP status codes
 */
function getErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return '입력 데이터가 올바르지 않습니다.'
    case 401:
      return '인증이 필요합니다.'
    case 403:
      return '접근 권한이 없습니다.'
    case 404:
      return '요청한 리소스를 찾을 수 없습니다.'
    case 500:
      return '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    case 502:
    case 503:
    case 504:
      return '서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.'
    default:
      return '오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
  }
}

/**
 * Create KORMARC record from BookInfo
 * POST /api/kormarc/build
 */
export async function createKORMARC(
  bookInfo: BookInfo,
  options: APIOptions = {}
): Promise<KORMARCRecord> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/api/kormarc/build`

  const response = await fetchWithRetry(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(bookInfo),
    timeout: options.timeout,
    retries: options.retries,
  })

  return handleResponse<KORMARCRecord>(response)
}

/**
 * Search books by query (optional feature)
 * GET /api/book/search?query=...
 */
export async function searchBooks(
  query: string,
  options: APIOptions = {}
): Promise<BookInfo[]> {
  const baseUrl = getApiBaseUrl()
  const url = new URL(`${baseUrl}/api/book/search`)
  url.searchParams.append('query', query)

  const response = await fetchWithRetry(url.toString(), {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: options.timeout,
    retries: options.retries,
  })

  return handleResponse<BookInfo[]>(response)
}

/**
 * Validate KORMARC data (optional feature)
 * POST /api/kormarc/validate
 */
export async function validateKORMARC(
  data: unknown,
  options: APIOptions = {}
): Promise<KORMARCRecord['validation']> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/api/kormarc/validate`

  const response = await fetchWithRetry(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
    timeout: options.timeout,
    retries: options.retries,
  })

  return handleResponse<KORMARCRecord['validation']>(response)
}

/**
 * Health check for backend availability
 * GET /api/health
 */
export async function healthCheck(options: APIOptions = {}): Promise<{
  status: string
  timestamp: string
}> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/api/health`

  const response = await fetchWithRetry(url, {
    method: 'GET',
    timeout: options.timeout || 5000, // Shorter timeout for health check
    retries: 1, // Only retry once for health check
  })

  return handleResponse<{ status: string; timestamp: string }>(response)
}

/**
 * Export API client object
 */
export const apiClient = {
  createKORMARC,
  searchBooks,
  validateKORMARC,
  healthCheck,
}

export default apiClient
