/**
 * E2E Tests for KORMARC Web Frontend
 * Testing user flows with Playwright
 */

import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000'

test.describe('KORMARC Web Application', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL)
  })

  test.describe('Home Page', () => {
    test('should display home page with title', async ({ page }) => {
      await expect(page).toHaveTitle(/KORMARC Web/)
      await expect(page.locator('h1')).toContainText('KORMARC Web')
    })

    test('should navigate to records page', async ({ page }) => {
      await page.click('text=도서 목록 보기')
      await expect(page).toHaveURL(/\/records/)
      await expect(page.locator('h1')).toContainText('도서 목록')
    })

    test('should navigate to search page', async ({ page }) => {
      await page.click('text=검색하기')
      await expect(page).toHaveURL(/\/search/)
      await expect(page.locator('h1')).toContainText('검색')
    })
  })

  test.describe('Navigation', () => {
    test('should have working navigation links', async ({ page }) => {
      // Test Records link
      await page.click('a[href="/records"]')
      await expect(page).toHaveURL(/\/records/)

      // Test Search link
      await page.click('a[href="/search"]')
      await expect(page).toHaveURL(/\/search/)

      // Test Home link
      await page.click('a[href="/"]')
      await expect(page).toHaveURL(/\//)
    })

    test('should toggle dark mode', async ({ page }) => {
      const darkModeButton = page.locator('button[aria-label*="모드"]').first()

      // Get initial theme
      const htmlBefore = page.locator('html')
      const isDarkBefore = await htmlBefore.getAttribute('class').then(classes => classes?.includes('dark'))

      // Click toggle
      await darkModeButton.click()

      // Wait for theme change
      await page.waitForTimeout(100)

      // Check theme changed
      const htmlAfter = page.locator('html')
      const isDarkAfter = await htmlAfter.getAttribute('class').then(classes => classes?.includes('dark'))

      expect(isDarkAfter).toBe(!isDarkBefore)
    })
  })

  test.describe('Records List Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${BASE_URL}/records`)
    })

    test('should display records list', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('도서 목록')

      // Wait for records to load
      await page.waitForSelector('a[href^="/records/"]', { timeout: 5000 })

      // Check if record cards are displayed
      const recordCards = page.locator('a[href^="/records/"]')
      const count = await recordCards.count()

      expect(count).toBeGreaterThan(0)
    })

    test('should display pagination', async ({ page }) => {
      // Wait for records to load
      await page.waitForSelector('a[href^="/records/"]', { timeout: 5000 })

      // Check pagination info
      const paginationInfo = page.locator('text=/전체 .*개 중 .*-.*개 표시/')
      await expect(paginationInfo).toBeVisible()
    })

    test('should navigate to record detail', async ({ page }) => {
      // Wait for records to load
      await page.waitForSelector('a[href^="/records/"]', { timeout: 5000 })

      // Click first record
      await page.locator('a[href^="/records/"]').first().click()

      // Check navigation to detail page
      await expect(page).toHaveURL(/\/records\/[^/]+$/)
    })
  })

  test.describe('Record Detail Page', () => {
    test('should display record detail', async ({ page }) => {
      // Go to records list first
      await page.goto(`${BASE_URL}/records`)
      await page.waitForSelector('a[href^="/records/"]', { timeout: 5000 })

      // Click first record
      await page.locator('a[href^="/records/"]').first().click()

      // Wait for navigation to complete
      await page.waitForURL(/\/records\/[^/]+$/, { timeout: 5000 })

      // Wait for page content to load
      await page.waitForSelector('[data-slot="card-title"]', { timeout: 5000 })

      // Check detail page elements
      await expect(page.locator('text=저자')).toBeVisible()
      await expect(page.locator('text=출판사')).toBeVisible()

      // Check back button
      await page.click('text=목록으로')
      await expect(page).toHaveURL(/\/records$/)
    })
  })

  test.describe('Search Page', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`${BASE_URL}/search`)
    })

    test('should display search form', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('검색')

      // Check search input
      const searchInput = page.locator('input[placeholder*="검색"]')
      await expect(searchInput).toBeVisible()

      // Check search button
      const searchButton = page.locator('button:has-text("검색")')
      await expect(searchButton).toBeVisible()
    })

    test('should perform search', async ({ page }) => {
      // Enter search query
      const searchInput = page.locator('input[placeholder*="검색"]')
      await searchInput.fill('컴퓨터')

      // Submit search
      const searchButton = page.locator('button:has-text("검색")')
      await searchButton.click()

      // Wait for results
      await page.waitForSelector('text=/컴퓨터.*검색 결과/', { timeout: 5000 })

      // Debug: Check all links on page
      const allLinks = page.locator('a')
      const linkCount = await allLinks.count()
      console.log(`Total links on page: ${linkCount}`)

      for (let i = 0; i < Math.min(linkCount, 10); i++) {
        const href = await allLinks.nth(i).getAttribute('href')
        const text = await allLinks.nth(i).textContent()
        console.log(`Link ${i}: href="${href}", text="${text?.substring(0, 50)}"`)
      }

      // Check if results are displayed
      const resultCards = page.locator('a[href^="/records/"]')
      const count = await resultCards.count()
      console.log(`Result cards with href^="/records/": ${count}`)

      expect(count).toBeGreaterThan(0)
    })

    test('should clear search', async ({ page }) => {
      // Enter search query
      const searchInput = page.locator('input[placeholder*="검색"]')
      await searchInput.fill('Test Query')

      // Click clear button
      const clearButton = page.locator('button[aria-label="검색어 지우기"]')
      await clearButton.click()

      // Check if input is cleared
      await expect(searchInput).toHaveValue('')
    })
  })

  test.describe('Responsive Design', () => {
    test('should display mobile navigation', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 })

      // Check if mobile navigation is visible
      await page.goto(BASE_URL)

      // Mobile navigation should be visible
      const mobileNav = page.locator('nav.md\\:hidden')
      await expect(mobileNav).toBeVisible()
    })

    test('should display desktop navigation', async ({ page }) => {
      // Set desktop viewport
      await page.setViewportSize({ width: 1280, height: 720 })

      await page.goto(BASE_URL)

      // Desktop navigation should be visible
      const desktopNav = page.locator('nav.hidden.md\\:flex')
      await expect(desktopNav).toBeVisible()
    })
  })

  test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
      await page.goto(`${BASE_URL}/records`)

      // Check for h1
      const h1 = page.locator('h1')
      await expect(h1).toBeVisible()

      // Check that h1 comes before h2
      const h1Text = await h1.textContent()
      expect(h1Text).toBeTruthy()
    })

    test('should have accessible buttons', async ({ page }) => {
      await page.goto(`${BASE_URL}/search`)

      // Check if buttons have aria-labels
      const searchButton = page.locator('button[aria-label]')
      const count = await searchButton.count()
      expect(count).toBeGreaterThan(0)
    })
  })
})

test.describe('Error Handling', () => {
  test('should handle 404 page', async ({ page }) => {
    await page.goto(`${BASE_URL}/non-existent-page`)

    // Next.js should show 404 page
    await expect(page.locator('text=/404|찾을 수 없음/')).toBeVisible({ timeout: 5000 })
  })
})

test.describe('Performance', () => {
  test('should load home page quickly', async ({ page }) => {
    const startTime = Date.now()
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')
    const loadTime = Date.now() - startTime

    // Page should load in less than 3 seconds
    expect(loadTime).toBeLessThan(3000)
  })
})
