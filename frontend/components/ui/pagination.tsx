/**
 * Pagination Component
 * Handles pagination controls for records list
 */

'use client'

import * as React from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  className?: string
  showFirstLast?: boolean
  maxVisiblePages?: number
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
  showFirstLast = true,
  maxVisiblePages = 5,
}: PaginationProps) {
  // Generate page numbers to display
  const getPageNumbers = (): (number | string)[] => {
    const pages: (number | string)[] = []
    const halfVisible = Math.floor(maxVisiblePages / 2)

    if (totalPages <= maxVisiblePages) {
      // Show all pages if total is less than max visible
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Always show first page
      pages.push(1)

      if (currentPage <= halfVisible + 1) {
        // Near the start
        for (let i = 2; i <= maxVisiblePages - 1; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - halfVisible) {
        // Near the end
        pages.push('...')
        for (let i = totalPages - maxVisiblePages + 2; i <= totalPages; i++) {
          pages.push(i)
        }
      } else {
        // In the middle
        pages.push('...')
        for (let i = currentPage - halfVisible + 1; i <= currentPage + halfVisible - 1; i++) {
          pages.push(i)
        }
        pages.push('...')
        pages.push(totalPages)
      }
    }

    return pages
  }

  const pageNumbers = getPageNumbers()

  return (
    <nav
      className={cn('flex items-center justify-center gap-2', className)}
      aria-label="페이지 네비게이션"
    >
      {/* Previous Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        aria-label="이전 페이지"
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>

      {/* Page Numbers */}
      {pageNumbers.map((page, index) => (
        typeof page === 'number' ? (
          <Button
            key={index}
            variant={currentPage === page ? 'default' : 'outline'}
            size="icon"
            onClick={() => onPageChange(page)}
            aria-label={`${page} 페이지`}
            aria-current={currentPage === page ? 'page' : undefined}
          >
            {page}
          </Button>
        ) : (
          <span
            key={index}
            className="px-2 text-sm text-muted-foreground"
            aria-hidden="true"
          >
            {page}
          </span>
        )
      ))}

      {/* Next Button */}
      <Button
        variant="outline"
        size="icon"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        aria-label="다음 페이지"
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </nav>
  )
}

/**
 * Pagination Info Component
 * Displays "Showing X-Y of Z results" text
 */
export interface PaginationInfoProps {
  current: number
  size: number
  total: number
  className?: string
}

export function PaginationInfo({
  current,
  size,
  total,
  className,
}: PaginationInfoProps) {
  const start = (current - 1) * size + 1
  const end = Math.min(current * size, total)

  return (
    <p className={cn('text-sm text-muted-foreground', className)}>
      전체 {total}개 중 {start}-{end}개 표시
    </p>
  )
}
