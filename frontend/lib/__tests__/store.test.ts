/**
 * Unit Tests for Zustand Store
 * Testing state management for records, pagination, and search
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { useRecordsStore } from '../store'

describe('RecordsStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useRecordsStore.getState().reset()
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const state = useRecordsStore.getState()

      expect(state.records).toEqual([])
      expect(state.currentRecord).toBeNull()
      expect(state.total).toBe(0)
      expect(state.page).toBe(1)
      expect(state.size).toBe(20)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBeNull()
      expect(state.searchQuery).toBe('')
      expect(state.searchResults).toEqual([])
      expect(state.searchTotal).toBe(0)
      expect(state.isSearching).toBe(false)
      expect(state.searchError).toBeNull()
      expect(state.theme).toBe('system')
    })
  })

  describe('Records Actions', () => {
    it('should set records from API response', () => {
      const mockResponse = {
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

      useRecordsStore.getState().setRecords(mockResponse)
      const state = useRecordsStore.getState()

      expect(state.records).toEqual(mockResponse.items)
      expect(state.total).toBe(1)
      expect(state.page).toBe(1)
      expect(state.size).toBe(20)
      expect(state.error).toBeNull()
    })

    it('should set current record', () => {
      const mockRecord = {
        id: 'KDC000001',
        title: 'Test Book',
        author: 'Test Author',
        publisher: 'Test Publisher',
        pub_year: '2024',
        isbn: '9791162233149',
        kdc: '005.133',
        language: 'kor',
      }

      useRecordsStore.getState().setCurrentRecord(mockRecord)
      const state = useRecordsStore.getState()

      expect(state.currentRecord).toEqual(mockRecord)
      expect(state.error).toBeNull()
    })

    it('should set loading state', () => {
      useRecordsStore.getState().setLoading(true)
      expect(useRecordsStore.getState().isLoading).toBe(true)

      useRecordsStore.getState().setLoading(false)
      expect(useRecordsStore.getState().isLoading).toBe(false)
    })

    it('should set error state', () => {
      const errorMessage = 'Test error message'
      useRecordsStore.getState().setError(errorMessage)
      const state = useRecordsStore.getState()

      expect(state.error).toBe(errorMessage)
      expect(state.isLoading).toBe(false)
    })

    it('should set page', () => {
      useRecordsStore.getState().setPage(2)
      expect(useRecordsStore.getState().page).toBe(2)
    })

    it('should set size', () => {
      useRecordsStore.getState().setSize(50)
      expect(useRecordsStore.getState().size).toBe(50)
    })
  })

  describe('Search Actions', () => {
    it('should set search query', () => {
      const query = 'Python programming'
      useRecordsStore.getState().setSearchQuery(query)
      expect(useRecordsStore.getState().searchQuery).toBe(query)
    })

    it('should set search results', () => {
      const mockResponse = {
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

      useRecordsStore.getState().setSearchResults(mockResponse)
      const state = useRecordsStore.getState()

      expect(state.searchResults).toEqual(mockResponse.items)
      expect(state.searchTotal).toBe(1)
      expect(state.page).toBe(1)
      expect(state.size).toBe(20)
      expect(state.searchError).toBeNull()
    })

    it('should set searching state', () => {
      useRecordsStore.getState().setSearching(true)
      expect(useRecordsStore.getState().isSearching).toBe(true)

      useRecordsStore.getState().setSearching(false)
      expect(useRecordsStore.getState().isSearching).toBe(false)
    })

    it('should set search error', () => {
      const errorMessage = 'Search failed'
      useRecordsStore.getState().setSearchError(errorMessage)
      const state = useRecordsStore.getState()

      expect(state.searchError).toBe(errorMessage)
      expect(state.isSearching).toBe(false)
    })

    it('should clear search', () => {
      // Set search state
      useRecordsStore.getState().setSearchQuery('test')
      useRecordsStore.getState().setSearchResults({
        items: [],
        total: 0,
        page: 1,
        size: 20,
      })

      // Clear search
      useRecordsStore.getState().clearSearch()
      const state = useRecordsStore.getState()

      expect(state.searchQuery).toBe('')
      expect(state.searchResults).toEqual([])
      expect(state.searchTotal).toBe(0)
      expect(state.isSearching).toBe(false)
      expect(state.searchError).toBeNull()
    })
  })

  describe('UI Actions', () => {
    it('should set theme', () => {
      useRecordsStore.getState().setTheme('dark')
      expect(useRecordsStore.getState().theme).toBe('dark')

      useRecordsStore.getState().setTheme('light')
      expect(useRecordsStore.getState().theme).toBe('light')
    })
  })

  describe('Selectors', () => {
    it('should calculate total pages correctly', () => {
      const state = useRecordsStore.getState()

      // Set total to 100 records with page size 20
      useRecordsStore.getState().setRecords({
        items: [],
        total: 100,
        page: 1,
        size: 20,
      })

      expect(state.total).toBe(100)
      expect(state.size).toBe(20)

      // Total pages should be 5 (100 / 20)
      const totalPages = Math.ceil(state.total / state.size)
      expect(totalPages).toBe(5)
    })
  })

  describe('Reset', () => {
    it('should reset state to initial values', () => {
      // Set some state
      useRecordsStore.getState().setRecords({
        items: [],
        total: 10,
        page: 2,
        size: 20,
      })
      useRecordsStore.getState().setError('Some error')
      useRecordsStore.getState().setSearchQuery('test')
      useRecordsStore.getState().setTheme('dark')

      // Reset
      useRecordsStore.getState().reset()
      const state = useRecordsStore.getState()

      expect(state.records).toEqual([])
      expect(state.total).toBe(0)
      expect(state.page).toBe(1)
      expect(state.error).toBeNull()
      expect(state.searchQuery).toBe('')
      // Theme should be preserved
      expect(state.theme).toBe('dark')
    })
  })
})
