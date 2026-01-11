/**
 * Record Detail Page - Single KORMARC record view
 */

'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeft, BookOpen, User, Building, Calendar, Tag, FileText, Hash, Layers } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useRecordsStore } from '@/lib/store'
import { recordsApi } from '@/lib/api-records'
import type { RecordDetail, MARCField } from '@/lib/store'

export default function RecordDetailPage() {
  const params = useParams()
  const recordId = params.id as string

  const {
    currentRecord,
    isLoading,
    error,
    setCurrentRecord,
    setLoading,
    setError,
  } = useRecordsStore()

  // Fetch record detail on mount
  useEffect(() => {
    async function fetchRecordDetail() {
      setLoading(true)
      setError(null)

      try {
        const record = await recordsApi.getRecordDetail(recordId)
        setCurrentRecord(record)
      } catch (err) {
        setError(err instanceof Error ? err.message : '레코드를 불러오는데 실패했습니다')
      } finally {
        setLoading(false)
      }
    }

    if (recordId) {
      fetchRecordDetail()
    }
  }, [recordId, setCurrentRecord, setLoading, setError])

  // Loading state
  if (isLoading) {
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
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-destructive text-lg mb-4">{error}</p>
            <div className="flex gap-4 justify-center">
              <Button asChild variant="outline">
                <Link href="/records">목록으로</Link>
              </Button>
              <Button onClick={() => window.location.reload()}>다시 시도</Button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // No record found
  if (!currentRecord) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground mb-4">레코드를 찾을 수 없습니다.</p>
          <Button asChild variant="outline">
            <Link href="/records">목록으로</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back Button */}
      <Button asChild variant="ghost" className="mb-6">
        <Link href="/records">
          <ArrowLeft className="mr-2 h-4 w-4" />
          목록으로
        </Link>
      </Button>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title and Basic Info */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-2xl mb-4">
                    {currentRecord.title}
                  </CardTitle>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">{currentRecord.kdc}</Badge>
                    <Badge variant="outline">{currentRecord.language}</Badge>
                    {currentRecord.isbn && (
                      <Badge variant="success">ISBN: {currentRecord.isbn}</Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Author */}
              <InfoRow
                icon={<User className="h-5 w-5" />}
                label="저자"
                value={currentRecord.author}
              />

              {/* Publisher */}
              <InfoRow
                icon={<Building className="h-5 w-5" />}
                label="출판사"
                value={currentRecord.publisher}
              />

              {/* Publication Year */}
              <InfoRow
                icon={<Calendar className="h-5 w-5" />}
                label="발행년"
                value={currentRecord.pub_year}
              />

              {/* Publication Place */}
              {currentRecord.pub_place && (
                <InfoRow
                  icon={<Layers className="h-5 w-5" />}
                  label="발행지"
                  value={currentRecord.pub_place}
                />
              )}

              {/* Description */}
              {currentRecord.description && (
                <div className="pt-4 border-t">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    도서 설명
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {currentRecord.description}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* MARC Fields */}
          {currentRecord.marc_fields && currentRecord.marc_fields.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Hash className="h-5 w-5 text-primary" />
                  MARC 필드
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {currentRecord.marc_fields.map((field: MARCField, index: number) => (
                    <MARCFieldCard key={index} field={field} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Record ID */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">레코드 ID</CardTitle>
            </CardHeader>
            <CardContent>
              <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                {currentRecord.id}
              </code>
            </CardContent>
          </Card>

          {/* Physical Description */}
          {(currentRecord.pages || currentRecord.size) && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">형식 정보</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {currentRecord.pages && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">페이지</span>
                    <span>{currentRecord.pages}</span>
                  </div>
                )}
                {currentRecord.size && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">크기</span>
                    <span>{currentRecord.size}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Subjects */}
          {currentRecord.subject && currentRecord.subject.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">주제어</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {currentRecord.subject.map((subject: string, index: number) => (
                    <Badge key={index} variant="outline">
                      {subject}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Notes */}
          {currentRecord.notes && currentRecord.notes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">비고</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  {currentRecord.notes.map((note: string, index: number) => (
                    <li key={index} className="flex items-start gap-2">
                      <span className="text-muted-foreground">•</span>
                      <span className="text-muted-foreground">{note}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

/**
 * Info Row Component
 */
function InfoRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="text-muted-foreground flex-shrink-0 mt-0.5">{icon}</div>
      <div className="flex-1">
        <p className="text-sm text-muted-foreground mb-1">{label}</p>
        <p className="font-medium">{value}</p>
      </div>
    </div>
  )
}

/**
 * MARC Field Card Component
 */
function MARCFieldCard({ field }: { field: MARCField }) {
  return (
    <div className="border rounded-lg p-4 bg-muted/30">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-mono font-bold text-lg">
          <span className="text-primary">{field.tag}</span>
          <span className="text-muted-foreground text-sm ml-2">
            [{field.indicators}]
          </span>
        </h4>
      </div>
      <div className="space-y-2">
        {field.subfields.map((subfield, index) => (
          <div key={index} className="flex items-start gap-2 text-sm">
            <span className="font-mono text-muted-foreground">
              ${subfield.code}
            </span>
            <span className="flex-1">{subfield.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
