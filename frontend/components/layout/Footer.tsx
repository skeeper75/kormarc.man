/**
 * Footer Component - Site footer with links
 */

import Link from 'next/link'
import { BookOpen } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="w-full border-t bg-background">
      <div className="container mx-auto px-4 py-6 md:py-8">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <BookOpen className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium text-muted-foreground">
              KORMARC
            </span>
          </Link>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-4 text-sm text-muted-foreground">
            <Link
              href="/"
              className="hover:text-foreground transition-colors"
            >
              홈
            </Link>
            <span>|</span>
            <Link
              href="/records"
              className="hover:text-foreground transition-colors"
            >
              도서 목록
            </Link>
            <span>|</span>
            <Link
              href="/search"
              className="hover:text-foreground transition-colors"
            >
              검색
            </Link>
          </div>

          {/* Copyright */}
          <p className="text-xs text-muted-foreground">
            &copy; {currentYear} KORMARC. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
