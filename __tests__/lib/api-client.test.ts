import { describe, it, expect, vi, beforeEach } from 'vitest'
import { buildKORMARC } from '@lib/api-client'
import type { BookInfo } from '@lib/validators'

// Mock fetch
global.fetch = vi.fn()

const mockBookData: BookInfo = {
  isbn: '9788954687065',
  title: 'KORMARC 테스트',
  author: '테스트 저자',
  publisher: '테스트 출판사',
  publicationYear: 2024,
  description: '테스트 설명',
  classification: 'KDC-3',
}

const mockResponse = {
  kormarc: '<record>...</record>',
  json: '{"status": "success"}',
  validationTiers: [
    { level: 1, status: 'passed' },
    { level: 2, status: 'passed' },
    { level: 3, status: 'passed' },
    { level: 4, status: 'passed' },
    { level: 5, status: 'passed' },
  ],
}

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('buildKORMARC', () => {
    it('should fetch KORMARC from /api/kormarc/build', async () => {
      // Arrange
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      const result = await buildKORMARC(mockBookData)

      // Assert
      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith('/api/kormarc/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockBookData),
      })
    })

    it('should throw error when API returns non-ok status', async () => {
      // Arrange
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
      })

      // Act & Assert
      await expect(buildKORMARC(mockBookData)).rejects.toThrow('API error: 500')
    })

    it('should throw error on network failure', async () => {
      // Arrange
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      // Act & Assert
      await expect(buildKORMARC(mockBookData)).rejects.toThrow('Network error')
    })

    it('should handle API error response gracefully', async () => {
      // Arrange
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ error: 'Invalid data' }),
      })

      // Act
      const result = await buildKORMARC(mockBookData)

      // Assert
      expect(result).toEqual({ error: 'Invalid data' })
    })

    it('should send correct headers and method', async () => {
      // Arrange
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      await buildKORMARC(mockBookData)

      // Assert
      const [url, options] = (global.fetch as any).mock.calls[0]
      expect(url).toBe('/api/kormarc/build')
      expect(options.method).toBe('POST')
      expect(options.headers['Content-Type']).toBe('application/json')
    })

    it('should serialize BookInfo data correctly', async () => {
      // Arrange
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      // Act
      await buildKORMARC(mockBookData)

      // Assert
      const [, options] = (global.fetch as any).mock.calls[0]
      const sentData = JSON.parse(options.body)
      expect(sentData.isbn).toBe(mockBookData.isbn)
      expect(sentData.title).toBe(mockBookData.title)
      expect(sentData.author).toBe(mockBookData.author)
    })
  })
})
