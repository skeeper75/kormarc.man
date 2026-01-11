/**
 * Zustand Store for KORMARC Web Frontend State Management
 * Handles records, pagination, search, and UI state
 */

import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// Record type from backend API
export interface Record {
  id: string
  title: string
  author: string
  publisher: string
  pub_year: string
  isbn: string | null
  kdc: string
  language: string
}

// Detailed record with additional fields
export interface RecordDetail extends Record {
  pub_place?: string
  description?: string
  pages?: string
  size?: string
  subject?: string[]
  notes?: string[]
  marc_fields?: MARCField[]
}

export interface MARCField {
  tag: string
  indicators: string
  subfields: Array<{ code: string; value: string }>
}

// Paginated response from backend
export interface RecordsResponse {
  items: Record[]
  total: number
  page: number
  size: number
}

// Search query state
export interface SearchQuery {
  q: string
  page: number
  size: number
}

// Store state interface
interface RecordsStore {
  // Records state
  records: Record[]
  currentRecord: RecordDetail | null
  total: number
  page: number
  size: number
  isLoading: boolean
  error: string | null

  // Search state
  searchQuery: string
  searchResults: Record[]
  searchTotal: number
  isSearching: boolean
  searchError: string | null

  // UI state
  theme: 'light' | 'dark' | 'system'

  // Actions
  setRecords: (response: RecordsResponse) => void
  setCurrentRecord: (record: RecordDetail | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setPage: (page: number) => void
  setSize: (size: number) => void

  // Search actions
  setSearchQuery: (query: string) => void
  setSearchResults: (response: RecordsResponse) => void
  setSearching: (searching: boolean) => void
  setSearchError: (error: string | null) => void
  clearSearch: () => void

  // UI actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  reset: () => void
}

// Initial state
const initialState = {
  records: [],
  currentRecord: null,
  total: 0,
  page: 1,
  size: 20,
  isLoading: false,
  error: null,
  searchQuery: '',
  searchResults: [],
  searchTotal: 0,
  isSearching: false,
  searchError: null,
  theme: 'system' as const,
}

// Create the store
export const useRecordsStore = create<RecordsStore>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // Records actions
        setRecords: (response) =>
          set({
            records: response.items,
            total: response.total,
            page: response.page,
            size: response.size,
            error: null,
          }),

        setCurrentRecord: (record) =>
          set({
            currentRecord: record,
            error: null,
          }),

        setLoading: (loading) =>
          set({
            isLoading: loading,
          }),

        setError: (error) =>
          set({
            error,
            isLoading: false,
          }),

        setPage: (page) =>
          set({
            page,
          }),

        setSize: (size) =>
          set({
            size,
          }),

        // Search actions
        setSearchQuery: (query) =>
          set({
            searchQuery: query,
          }),

        setSearchResults: (response) =>
          set({
            searchResults: response.items,
            searchTotal: response.total,
            page: response.page,
            size: response.size,
            searchError: null,
          }),

        setSearching: (searching) =>
          set({
            isSearching: searching,
          }),

        setSearchError: (error) =>
          set({
            searchError: error,
            isSearching: false,
          }),

        clearSearch: () =>
          set({
            searchQuery: '',
            searchResults: [],
            searchTotal: 0,
            isSearching: false,
            searchError: null,
          }),

        // UI actions
        setTheme: (theme) =>
          set({
            theme,
          }),

        reset: () =>
          set((state) => ({
            ...initialState,
            theme: state.theme, // Preserve theme
          })),
      }),
      {
        name: 'kormarc-storage',
        // Only persist theme and search query
        partialize: (state) => ({
          theme: state.theme,
          searchQuery: state.searchQuery,
        }),
      }
    ),
    { name: 'KORMARC Store' }
  )
)

// Selectors for computed values
export const selectRecords = (state: RecordsStore) => state.records
export const selectCurrentRecord = (state: RecordsStore) => state.currentRecord
export const selectIsLoading = (state: RecordsStore) => state.isLoading
export const selectError = (state: RecordsStore) => state.error
export const selectPagination = (state: RecordsStore) => ({
  page: state.page,
  size: state.size,
  total: state.total,
  totalPages: Math.ceil(state.total / state.size),
})
export const selectSearchResults = (state: RecordsStore) => state.searchResults
export const selectIsSearching = (state: RecordsStore) => state.isSearching
export const selectTheme = (state: RecordsStore) => state.theme
