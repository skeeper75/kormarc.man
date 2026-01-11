'use client'

import type { PreviewData } from '@lib/api-client'

export type { PreviewData }

/**
 * ExportButtons 컴포넌트
 * KORMARC 데이터를 JSON 또는 XML로 다운로드하거나 클립보드에 복사하는 버튼
 *
 * @param data 다운로드 또는 복사할 프리뷰 데이터
 * @example
 * const data = {
 *   json: '{"status": "success"}',
 *   xml: '<record>...</record>'
 * }
 * <ExportButtons data={data} />
 */
export function ExportButtons({ data }: { data: PreviewData }) {
  /**
   * 파일 다운로드 처리
   * @param format 다운로드할 형식 ('json' 또는 'kormarc')
   */
  const handleDownload = (format: 'json' | 'kormarc') => {
    const content = format === 'json' ? data.json : data.kormarc
    const fileExtension = format === 'json' ? 'json' : 'xml'
    const blob = new Blob([content], { type: `application/${fileExtension}` })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `KORMARC_${new Date().toISOString()}.${fileExtension}`
    link.click()
  }

  /**
   * 클립보드에 복사 처리
   * @param format 복사할 형식 ('json' 또는 'kormarc')
   */
  const handleCopy = async (format: 'json' | 'kormarc') => {
    const content = format === 'json' ? data.json : data.kormarc
    await navigator.clipboard.writeText(content)
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button
        onClick={() => handleDownload('json')}
        className="btn btn-primary"
      >
        JSON 다운로드
      </button>
      <button
        onClick={() => handleCopy('json')}
        className="btn btn-secondary"
      >
        JSON 복사
      </button>
      <button
        onClick={() => handleDownload('kormarc')}
        className="btn btn-primary"
      >
        KORMARC 다운로드
      </button>
      <button
        onClick={() => handleCopy('kormarc')}
        className="btn btn-secondary"
      >
        KORMARC 복사
      </button>
    </div>
  )
}
