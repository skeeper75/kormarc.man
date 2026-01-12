/**
 * API Client for KORMARC Records Backend
 * Handles records listing, detail, and search operations
 * Based on API_WEB.md documentation
 */

import type { RecordsResponse, RecordDetail, Record } from './store'

/**
 * Backend API response types (with toon_id)
 */
interface BackendRecord {
  toon_id: string
  timestamp_ms: number
  created_at: string
  record_type: string
  isbn: string | null
  title: string | null
  author: string | null
  publisher: string | null
  pub_year: number | null
  kdc_code: string | null
}

interface BackendRecordsResponse {
  items: BackendRecord[]
  total: number
  page: number
  size: number
}

interface BackendRecordDetail extends BackendRecord {
  record_length: number | null
  record_status: string | null
  raw_kormarc: string | null
  parsed_data: unknown | null
}

/**
 * Map backend record to frontend record
 */
function mapBackendRecord(backend: BackendRecord): Record {
  const id = backend.toon_id || `unknown-${Date.now()}-${Math.random()}`
  if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    console.log('[mapBackendRecord] Input:', backend)
    console.log('[mapBackendRecord] Mapped id:', id)
  }
  return {
    id: id,
    title: backend.title || '',
    author: backend.author || '',
    publisher: backend.publisher || '',
    pub_year: backend.pub_year?.toString() || '',
    isbn: backend.isbn,
    kdc: backend.kdc_code || '',
    language: 'ko', // Default language
  }
}

/**
 * Map backend record detail to frontend record detail
 */
function mapBackendRecordDetail(backend: BackendRecordDetail): RecordDetail {
  return {
    ...mapBackendRecord(backend),
    pub_place: undefined, // Not available in backend yet
    description: undefined, // Not available in backend yet
    pages: undefined, // Not available in backend yet
    size: undefined, // Not available in backend yet
    subject: undefined, // Not available in backend yet
    notes: undefined, // Not available in backend yet
    marc_fields: undefined, // Not available in backend yet
  }
}

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

  const backend = await fetchWithErrorHandling<BackendRecordsResponse>(url)
  return {
    items: backend.items.map(mapBackendRecord),
    total: backend.total,
    page: backend.page,
    size: backend.size,
  }
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

  const backend = await fetchWithErrorHandling<BackendRecordDetail>(url)
  return mapBackendRecordDetail(backend)
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

  const backend = await fetchWithErrorHandling<BackendRecordsResponse>(url)
  return {
    items: backend.items.map(mapBackendRecord),
    total: backend.total,
    page: backend.page,
    size: backend.size,
  }
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
