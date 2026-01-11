'use client'

import { BookInfoForm } from '@components/BookInfoForm'

/**
 * 메인 홈 페이지
 * KORMARC 생성기의 메인 인터페이스
 * - 책 정보 폼 입력
 * - KORMARC 생성
 * - 결과 미리보기 및 다운로드
 */
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* 헤더 */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-4xl font-bold text-gray-900">KORMARC 생성기</h1>
          <p className="text-gray-600 mt-2">
            한국 도서관 자동화 자료형식(KORMARC) 레코드를 생성합니다
          </p>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {/* 폼 섹션 */}
        <section className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-6">책 정보 입력</h2>
          <BookInfoForm />
        </section>

        {/* 초기 상태 메시지 */}
        <section className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">
            책 정보를 입력하고 &quot;KORMARC 생성&quot; 버튼을 클릭하세요
          </p>
        </section>
      </main>

      {/* 푸터 */}
      <footer className="bg-gray-800 text-white mt-16">
        <div className="max-w-4xl mx-auto px-4 py-8 text-center">
          <p className="text-gray-400">
            KORMARC 생성기 v1.0.0 | Korean Library Automation Data Format
          </p>
        </div>
      </footer>
    </div>
  )
}
