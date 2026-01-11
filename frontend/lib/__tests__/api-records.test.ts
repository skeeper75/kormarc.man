/**
 * Unit Tests for Records API Client
 * Testing API functions for records, search, and health check
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { recordsApi, RecordsAPIError, getApiBaseUrl } from '../api-records'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('Records API Client', () => {
  beforeEach(() => {
    // Clear mocks before each test
    mockFetch.mockClear()
  })

  describe('getApiBaseUrl', () => {
    it('should return localhost URL by default', () => {
      // Mock window object for client-side
      const originalWindow = global.window
      global.window = { ...originalWindow } as any

      const url = getApiBaseUrl()
      expect(url).toBe('http://localhost:8000')

      // Restore window
      global.window = originalWindow
    })

    it('should return env variable if set', () => {
      process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com'
      const url = getApiBaseUrl()
      expect(url).toBe('https://api.example.com')

      delete process.env.NEXT_PUBLIC_API_BASE_URL
    })
  })

  describe('healthCheck', () => {
    it('should return health status', async () => {
      const mockResponse = { status: 'healthy' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await recordsApi.healthCheck()

      expect(result).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/health'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
    })

    it('should throw error on non-OK response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      })

      await expect(recordsApi.healthCheck()).rejects.toThrow(RecordsAPIError)
    })
  })

  describe('getApiInfo', () => {
    it('should return API information', async () => {
      const mockInfo = {
        name: 'KORMARC Web API',
        version: '1.0.0',
        description: 'Test API',
      }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockInfo,
      })

      const result = await recordsApi.getApiInfo()

      expect(result).toEqual(mockInfo)
    })
  })

  describe('getRecords', () => {
    it('should fetch records with pagination', async () => {
      const mockRecordsResponse = {
        items: [
          {
            id: 'KDC000001',
            title: 'Test Book',
            author: 'Test Author',
            publisher: 'Test Publisher',
            pub_year: '2024',
            isbn: '9791162233149',
            kdc: '005.133',
            language: 'kor',
          },
        ],
        total: 1,
        page: 1,
        size: 20,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecordsResponse,
      })

      const result = await recordsApi.getRecords(1, 20)

      expect(result).toEqual(mockRecordsResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/records?page=1&size=20'),
        expect.any(Object)
      )
    })

    it('should use default pagination values', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, size: 20 }),
      })

      await recordsApi.getRecords()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('page=1&size=20'),
        expect.any(Object)
      )
    })
  })

  describe('getRecordDetail', () => {
    it('should fetch record detail by ID', async () => {
      const mockRecordDetail = {
        id: 'KDC000001',
        title: 'Test Book',
        author: 'Test Author',
        publisher: 'Test Publisher',
        pub_year: '2024',
        isbn: '9791162233149',
        kdc: '005.133',
        language: 'kor',
        description: 'Test description',
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecordDetail,
      })

      const result = await recordsApi.getRecordDetail('KDC000001')

      expect(result).toEqual(mockRecordDetail)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/records/KDC000001'),
        expect.any(Object)
      )
    })

    it('should encode record ID properly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'test' }),
      })

      await recordsApi.getRecordDetail('ID with spaces')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('ID%20with%20spaces'),
        expect.any(Object)
      )
    })
  })

  describe('searchRecords', () => {
    it('should search records with query', async () => {
      const mockSearchResponse = {
        items: [
          {
            id: 'KDC000001',
            title: 'Python Programming',
            author: 'Test Author',
            publisher: 'Test Publisher',
            pub_year: '2024',
            isbn: '9791162233149',
            kdc: '005.133',
            language: 'kor',
          },
        ],
        total: 1,
        page: 1,
        size: 20,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSearchResponse,
      })

      const result = await recordsApi.searchRecords('Python', 1, 20)

      expect(result).toEqual(mockSearchResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/search?q=Python&page=1&size=20'),
        expect.any(Object)
      )
    })

    it('should encode search query properly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, page: 1, size: 20 }),
      })

      await recordsApi.searchRecords('검색어 test')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent('검색어 test')),
        expect.any(Object)
      )
    })
  })

  describe('Error Handling', () => {
    it('should throw RecordsAPIError on 404', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Record not found' }),
      })

      await expect(recordsApi.getRecordDetail('INVALID')).rejects.toThrow(
        RecordsAPIError
      )

      try {
        await recordsApi.getRecordDetail('INVALID')
      } catch (error) {
        expect(error).toBeInstanceOf(RecordsAPIError)
        expect((error as RecordsAPIError).status).toBe(404)
      }
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(recordsApi.getRecords()).rejects.toThrow('네트워크 오류')
    })
  })
})
