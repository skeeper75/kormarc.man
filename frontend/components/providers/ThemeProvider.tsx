/**
 * Theme Provider - Dark mode support
 * Manages theme state and applies dark mode class to document
 */

'use client'

import { useEffect } from 'react'
import { useRecordsStore } from '@/lib/store'

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme } = useRecordsStore()

  useEffect(() => {
    // Get root element
    const root = document.documentElement

    // Determine effective theme
    const effectiveTheme =
      theme === 'system'
        ? window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light'
        : theme

    // Apply dark mode class
    if (effectiveTheme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    // Listen for system theme changes when using 'system' theme
    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = () => {
        if (mediaQuery.matches) {
          root.classList.add('dark')
        } else {
          root.classList.remove('dark')
        }
      }

      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
  }, [theme])

  return <>{children}</>
}
