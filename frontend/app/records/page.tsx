/**
 * Records List Page - Paginated list of KORMARC records
 */

'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { BookOpen, User, Building, Calendar, Tag } from 'lucide-react'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Pagination, PaginationInfo } from '@/components/ui/pagination'
import { useRecordsStore, selectPagination } from '@/lib/store'
import { recordsApi } from '@/lib/api-records'
import type { Record } from '@/lib/store'

export default function RecordsPage() {
  const {
    records,
    isLoading,
    error,
    page,
    size,
    setRecords,
    setLoading,
    setError,
    setPage,
  } = useRecordsStore()

  const pagination = selectPagination(useRecordsStore.getState())

  // Fetch records on mount and page change
  useEffect(() => {
    async function fetchRecords() {
      setLoading(true)
      setError(null)

      try {
        const response = await recordsApi.getRecords(page, size)
        setRecords(response)
      } catch (err) {
        setError(err instanceof Error ? err.message : '레코드를 불러오는데 실패했습니다')
      } finally {
        setLoading(false)
      }
    }

    fetchRecords()
  }, [page, size, setRecords, setLoading, setError])

  // Handle page change
  const handlePageChange = (newPage: number) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // Loading state
  if (isLoading && records.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
            <p className="text-muted-foreground">레코드를 불러오는 중...</p>
          </div>
        </div>
      </div>
    )
  }

  // Error state
  if (error && records.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-destructive text-lg mb-4">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="text-primary hover:underline"
            >
              다시 시도
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">도서 목록</h1>
        <PaginationInfo
          current={page}
          size={size}
          total={pagination.total}
          className="mb-4"
        />
      </div>

      {/* Records Grid */}
      {records.length > 0 ? (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {records.map((record: Record) => (
              <RecordCard key={record.id} record={record} />
            ))}
          </div>

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="flex justify-center">
              <Pagination
                currentPage={page}
                totalPages={pagination.totalPages}
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">표시할 레코드가 없습니다.</p>
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
            <User className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
            <span className="line-clamp-1">{record.author}</span>
          </div>

          {/* Publisher */}
          <div className="flex items-start gap-2 text-sm">
            <Building className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
            <span className="line-clamp-1">{record.publisher}</span>
          </div>

          {/* Publication Year */}
          <div className="flex items-center gap-2 text-sm">
            <Calendar className="h-4 w-4 text-muted-foreground flex-shrink-0" />
            <span>{record.pub_year}</span>
          </div>

          {/* ISBN */}
          {record.isbn && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Tag className="h-4 w-4 flex-shrink-0" />
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
