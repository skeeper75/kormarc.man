/**
 * API Client for KORMARC Records Backend
 * Handles records listing, detail, and search operations
 * Based on API_WEB.md documentation
 */

import type { RecordsResponse, RecordDetail } from './store'

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
 * Custom error class for API errors
 */
export class RecordsAPIError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: string
  ) {
    super(message)
    this.name = 'RecordsAPIError'
  }
}

/**
 * Fetch wrapper with error handling
 */
async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      // Try to parse error response
      let errorMessage = '요청 처리 중 오류가 발생했습니다'
      let errorDetail: string | undefined

      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorMessage
        errorDetail = errorData.detail
      } catch {
        // Use default error message
      }

      throw new RecordsAPIError(response.status, errorMessage, errorDetail)
    }

    return response.json()
  } catch (error) {
    if (error instanceof RecordsAPIError) {
      throw error
    }

    // Network or other errors
    throw new Error('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.')
  }
}

/**
 * Health check for backend availability
 * GET /health
 */
export async function healthCheck(): Promise<{ status: string }> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/health`

  return fetchWithErrorHandling<{ status: string }>(url)
}

/**
 * Get API info
 * GET /
 */
export async function getApiInfo(): Promise<{
  name: string
  version: string
  description: string
}> {
  const baseUrl = getApiBaseUrl()
  const url = baseUrl

  return fetchWithErrorHandling<{
    name: string
    version: string
    description: string
  }>(url)
}

/**
 * Get records list with pagination
 * GET /api/v1/records?page=1&size=20
 */
export async function getRecords(
  page: number = 1,
  size: number = 20
): Promise<RecordsResponse> {
  const baseUrl = getApiBaseUrl()
  const params = new URLSearchParams({
    page: page.toString(),
    size: size.toString(),
  })
  const url = `${baseUrl}/api/v1/records?${params.toString()}`

  return fetchWithErrorHandling<RecordsResponse>(url)
}

/**
 * Get record detail by ID
 * GET /api/v1/records/{record_id}
 */
export async function getRecordDetail(
  recordId: string
): Promise<RecordDetail> {
  const baseUrl = getApiBaseUrl()
  const url = `${baseUrl}/api/v1/records/${encodeURIComponent(recordId)}`

  return fetchWithErrorHandling<RecordDetail>(url)
}

/**
 * Search records by query
 * GET /api/v1/search?q={query}&page=1&size=20
 */
export async function searchRecords(
  query: string,
  page: number = 1,
  size: number = 20
): Promise<RecordsResponse> {
  const baseUrl = getApiBaseUrl()
  const params = new URLSearchParams({
    q: query,
    page: page.toString(),
    size: size.toString(),
  })
  const url = `${baseUrl}/api/v1/search?${params.toString()}`

  return fetchWithErrorHandling<RecordsResponse>(url)
}

/**
 * Export API client object
 */
export const recordsApi = {
  healthCheck,
  getApiInfo,
  getRecords,
  getRecordDetail,
  searchRecords,
}

export default recordsApi
