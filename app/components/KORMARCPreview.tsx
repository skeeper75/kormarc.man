'use client'

import { useState } from 'react'
import type { PreviewData } from '@lib/api-client'

export type { PreviewData }

/**
 * KORMARCPreview 컴포넌트
 * KORMARC 데이터를 JSON과 XML 형식으로 미리보기하는 탭 인터페이스
 *
 * @param data 표시할 프리뷰 데이터 (JSON, XML)
 * @example
 * const data = {
 *   json: '{"status": "success"}',
 *   xml: '<record>...</record>'
 * }
 * <KORMARCPreview data={data} />
 */
export function KORMARCPreview({ data }: { data: PreviewData }) {
  const [activeTab, setActiveTab] = useState<'json' | 'kormarc'>('json')

  return (
    <div className="space-y-4">
      {/* 탭 버튼 */}
      <div className="flex gap-2 border-b border-gray-300">
        <button
          role="tab"
          aria-selected={activeTab === 'json'}
          onClick={() => setActiveTab('json')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'json'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          JSON
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'kormarc'}
          onClick={() => setActiveTab('kormarc')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'kormarc'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          KORMARC
        </button>
      </div>

      {/* 콘텐츠 영역 */}
      <pre
        role="region"
        className="bg-gray-100 p-4 rounded overflow-auto max-h-96 border border-gray-300 text-sm font-mono"
      >
        {activeTab === 'json' ? data.json : data.kormarc}
      </pre>
    </div>
  )
}
