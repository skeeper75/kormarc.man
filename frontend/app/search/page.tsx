/**
 * Search Page - Full-text search for KORMARC records
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { Search, X, BookOpen, AlertCircle } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Pagination, PaginationInfo } from '@/components/ui/pagination'
import { useRecordsStore, selectPagination } from '@/lib/store'
import { recordsApi } from '@/lib/api-records'
import type { Record } from '@/lib/store'

export default function SearchPage() {
  const {
    searchQuery,
    searchResults,
    searchTotal,
    isSearching,
    searchError,
    setSearchQuery,
    setSearchResults,
    setSearching,
    setSearchError,
    clearSearch,
  } = useRecordsStore()

  const [inputValue, setInputValue] = useState(searchQuery)
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // Sync input with store
  useEffect(() => {
    setInputValue(searchQuery)
  }, [searchQuery])

  // Calculate pagination
  const totalPages = Math.ceil(searchTotal / pageSize)
  const pagination = {
    page: currentPage,
    size: pageSize,
    total: searchTotal,
    totalPages,
  }

  // Search function
  const performSearch = useCallback(async (query: string, page: number = 1) => {
    if (!query.trim()) {
      clearSearch()
      return
    }

    setSearching(true)
    setSearchError(null)

    try {
      const response = await recordsApi.searchRecords(query, page, pageSize)
      setSearchResults(response)
      setCurrentPage(page)
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : '검색 중 오류가 발생했습니다')
    } finally {
      setSearching(false)
    }
  }, [setSearchResults, setSearching, setSearchError, clearSearch])

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSearchQuery(inputValue)
    performSearch(inputValue, 1)
  }

  // Handle page change
  const handlePageChange = (page: number) => {
    performSearch(searchQuery, page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Clear search
  const handleClear = () => {
    setInputValue('')
    setSearchQuery('')
    clearSearch()
    setCurrentPage(1)
  }

  // Load initial search on mount if query exists
  useEffect(() => {
    if (searchQuery) {
      performSearch(searchQuery, 1)
    }
  }, []) // Empty deps - only run on mount

  // Loading state
  if (isSearching && searchResults.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
            <p className="text-muted-foreground">검색 중...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Search Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-6">검색</h1>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="제목, 저자, 출판사, 주제어 등으로 검색..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="pl-10 pr-10"
              aria-label="검색어 입력"
            />
            {inputValue && (
              <button
                type="button"
                onClick={handleClear}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label="검색어 지우기"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <Button type="submit" disabled={isSearching || !inputValue.trim()}>
            {isSearching ? '검색 중...' : '검색'}
          </Button>
        </form>

        {/* Search Tips */}
        <div className="mt-4 text-sm text-muted-foreground">
          <p>팁: 여러 단어를 공백으로 구분하여 검색할 수 있습니다 (예: "Python 프로그래밍")</p>
        </div>
      </div>

      {/* Error State */}
      {searchError && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-destructive">검색 오류</p>
            <p className="text-sm text-destructive/80 mt-1">{searchError}</p>
          </div>
        </div>
      )}

      {/* Search Results */}
      {searchQuery && (
        <>
          {searchResults.length > 0 ? (
            <>
              {/* Results Info */}
              <div className="mb-6">
                <p className="text-lg font-medium mb-2">
                  "{searchQuery}" 검색 결과
                </p>
                <PaginationInfo
                  current={currentPage}
                  size={pageSize}
                  total={searchTotal}
                />
              </div>

              {/* Results Grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {searchResults.map((record: Record) => (
                  <RecordCard key={record.id} record={record} />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-2">
                "{searchQuery}"에 대한 검색 결과가 없습니다.
              </p>
              <p className="text-sm text-muted-foreground">
                다른 검색어를 시도해보세요.
              </p>
            </div>
          )}
        </>
      )}

      {/* Initial State (No Search) */}
      {!searchQuery && !isSearching && (
        <div className="text-center py-12">
          <Search className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">KORMARC 레코드 검색</h2>
          <p className="text-muted-foreground mb-6">
            제목, 저자, 출판사, 주제어 등으로 도서를 검색하세요.
          </p>
          <div className="grid md:grid-cols-3 gap-4 max-w-3xl mx-auto text-left">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">제목 검색</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  도서 제목으로 검색 (예: "Python", "프로그래밍")
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">저자 검색</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  저자명으로 검색 (예: "홍길동", "Kim")
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">주제어 검색</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  주제어로 검색 (예: "데이터", "컴퓨터")
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Record Card Component
 */
function RecordCard({ record }: { record: Record }) {
  return (
    <Link href={`/records/${record.id}`}>
      <Card className="h-full transition-shadow hover:shadow-lg cursor-pointer">
        <CardHeader>
          <CardTitle className="line-clamp-2 text-lg">
            {record.title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Author */}
          <div className="flex items-start gap-2 text-sm">
            <span className="text-muted-foreground flex-shrink-0">저자:</span>
            <span className="line-clamp-1">{record.author}</span>
          </div>

          {/* Publisher */}
          <div className="flex items-start gap-2 text-sm">
            <span className="text-muted-foreground flex-shrink-0">출판사:</span>
            <span className="line-clamp-1">{record.publisher}</span>
          </div>

          {/* Publication Year */}
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground flex-shrink-0">발행년:</span>
            <span>{record.pub_year}</span>
          </div>

          {/* ISBN */}
          {record.isbn && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex-shrink-0">ISBN:</span>
              <span className="font-mono text-xs">{record.isbn}</span>
            </div>
          )}

          {/* KDC and Language Badges */}
          <div className="flex flex-wrap gap-2 pt-2">
            <Badge variant="secondary">{record.kdc}</Badge>
            <Badge variant="outline">{record.language}</Badge>
          </div>
        </CardContent>
        <CardFooter>
          <p className="text-xs text-muted-foreground">클릭하여 상세보기</p>
        </CardFooter>
      </Card>
    </Link>
  )
}
