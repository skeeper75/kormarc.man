/**
 * Home Page - Landing page for KORMARC Web
 */

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, Search, List, Github } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
          KORMARC Web
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          KORMARC 레코드를 검색하고 관리하는 웹 인터페이스
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/records">
              <List className="mr-2 h-5 w-5" />
              도서 목록 보기
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/search">
              <Search className="mr-2 h-5 w-5" />
              검색하기
            </Link>
          </Button>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          주요 기능
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <Card>
            <CardHeader>
              <BookOpen className="h-12 w-12 text-primary mb-4" />
              <CardTitle>도서 목록 조회</CardTitle>
              <CardDescription>
                100개의 프로토타입 KORMARC 레코드를 탐색하고
                상세 정보를 확인하세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild variant="ghost" className="w-full">
                <Link href="/records">더보기</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Feature 2 */}
          <Card>
            <CardHeader>
              <Search className="h-12 w-12 text-primary mb-4" />
              <CardTitle>전문 검색</CardTitle>
              <CardDescription>
                SQLite FTS5 기반의 빠른 전문 검색으로
                원하는 도서를 찾아보세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild variant="ghost" className="w-full">
                <Link href="/search">검색하기</Link>
              </Button>
            </CardContent>
          </Card>

          {/* Feature 3 */}
          <Card>
            <CardHeader>
              <Github className="h-12 w-12 text-primary mb-4" />
              <CardTitle>오픈 소스</CardTitle>
              <CardDescription>
                KORMARC Web은 오픈 소스 프로젝트로
                누구나 기여할 수 있습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                asChild
                variant="ghost"
                className="w-full"
              >
                <a
                  href="https://github.com/kormarc/kormarc.man"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub 보기
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <p className="text-4xl font-bold text-primary">100+</p>
            <p className="text-muted-foreground">레코드</p>
          </div>
          <div>
            <p className="text-4xl font-bold text-primary">FTS5</p>
            <p className="text-muted-foreground">검색 엔진</p>
          </div>
          <div>
            <p className="text-4xl font-bold text-primary">REST</p>
            <p className="text-muted-foreground">API</p>
          </div>
          <div>
            <p className="text-4xl font-bold text-primary">24/7</p>
            <p className="text-muted-foreground">접근성</p>
          </div>
        </div>
      </section>
    </div>
  )
}
