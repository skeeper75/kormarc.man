import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'
import { ThemeProvider } from '@/components/providers/ThemeProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'KORMARC Web - KORMARC 레코드 검색 및 관리',
  description: 'KORMARC 레코드를 검색하고 관리하는 웹 인터페이스. 100개의 프로토타입 레코드와 SQLite FTS5 기반 전문 검색을 제공합니다.',
  keywords: ['KORMARC', '도서관', 'MARC', '검색', '도서 목록'],
  authors: [{ name: 'KORMARC Team' }],
  openGraph: {
    title: 'KORMARC Web',
    description: 'KORMARC 레코드를 검색하고 관리하는 웹 인터페이스',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
