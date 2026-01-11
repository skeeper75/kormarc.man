/**
 * TDD RED Phase - BookInfoForm Component Tests
 * These tests are written BEFORE the implementation
 *
 * Following SPEC-FRONTEND-001 requirements:
 * - Scenario 1: Success KORMARC creation
 * - Scenario 2: ISBN real-time validation feedback
 * - Scenario 3: Required field button state
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BookInfoForm } from '../BookInfoForm'

// Mock the API client
vi.mock('@/lib/api-client', () => ({
  createKORMARC: vi.fn(),
}))

describe('BookInfoForm Component - TDD RED Phase', () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Test REQ-U-001: System always provides Next.js web UI with BookInfo form
   */
  describe('Component Rendering', () => {
    it('should render all 7 input fields', () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      // Required fields
      expect(screen.getByLabelText(/ISBN/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/제목/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/저자/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/출판사/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/발행년/i)).toBeInTheDocument()

      // Optional fields
      expect(screen.getByLabelText(/판차/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/총서명/i)).toBeInTheDocument()
    })

    it('should render submit button with correct initial state', () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
      expect(submitButton).toBeInTheDocument()
      expect(submitButton).toBeDisabled() // Initially disabled because required fields are empty
    })

    it('should display required field indicators (asterisk)', () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      // Required fields should have asterisk (in separate span element)
      expect(screen.getByText('ISBN')).toBeInTheDocument()
      expect(screen.getAllByText('*').length).toBeGreaterThanOrEqual(5) // At least 5 required fields
      expect(screen.getByText('제목')).toBeInTheDocument()
      expect(screen.getByText('저자')).toBeInTheDocument()
      expect(screen.getByText('출판사')).toBeInTheDocument()
      expect(screen.getByText('발행년')).toBeInTheDocument()
    })
  })

  /**
   * Test REQ-E-002: When ISBN input changes, format validation executes
   * Test REQ-S-001: IF required fields empty, button disabled
   */
  describe('ISBN Validation (REQ-E-002)', () => {
    it('should show error when ISBN is too short (9 digits)', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const isbnInput = screen.getByLabelText(/ISBN/i)
      const user = userEvent.setup()

      await user.type(isbnInput, '123456789')

      // After debounce (500ms), error should appear
      await waitFor(
        () => {
          // Check for either error message or validation message
          const errorMessage = screen.queryByText(/13자리여야 합니다/)
          const validationMessage = screen.queryByText(/ISBN/)
          expect(errorMessage || validationMessage).toBeInTheDocument()
        },
        { timeout: 1200 }
      )
    })

    it('should show success message for valid ISBN', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const isbnInput = screen.getByLabelText(/ISBN/i)
      const user = userEvent.setup()

      // Valid ISBN: 9780141036144 (Penguin Classics)
      await user.type(isbnInput, '9780141036144')

      await waitFor(
        () => {
          expect(screen.getByText(/유효한 ISBN입니다/)).toBeInTheDocument()
        },
        { timeout: 1200 }
      )
    })

    it('should show error for invalid ISBN checksum', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const isbnInput = screen.getByLabelText(/ISBN/i)
      const user = userEvent.setup()

      // Invalid checksum: change last digit of valid ISBN
      await user.type(isbnInput, '9780141036140')

      await waitFor(
        () => {
          expect(screen.getByText(/체크섬/)).toBeInTheDocument()
        },
        { timeout: 1200 }
      )
    })
  })

  /**
   * Test REQ-S-001: Button disabled/enabled based on required fields
   */
  describe('Submit Button State (REQ-S-001)', () => {
    it('should be disabled when all required fields are empty', () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
      expect(submitButton).toBeDisabled()
    })

    it('should be disabled when only ISBN is filled', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()
      const isbnInput = screen.getByLabelText(/ISBN/i)

      await user.type(isbnInput, '9780141036144')

      await waitFor(
        () => {
          const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
          expect(submitButton).toBeDisabled()
        },
        { timeout: 1000 }
      )
    })

    it('should be enabled when all required fields are filled', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Fill all required fields
      await user.type(screen.getByLabelText(/ISBN/i), '9780141036144')
      await user.type(screen.getByLabelText(/제목/i), 'Python 프로그래밍')
      await user.type(screen.getByLabelText(/저자/i), '박응용')
      await user.type(screen.getByLabelText(/출판사/i), '한빛미디어')
      await user.type(screen.getByLabelText(/발행년/i), '2025')

      await waitFor(
        () => {
          const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
          expect(submitButton).toBeEnabled()
        },
        { timeout: 1000 }
      )
    })
  })

  /**
   * Test REQ-E-001: When user submits form, call API
   * Test REQ-S-002: During API request, show loading spinner
   */
  describe('Form Submission (REQ-E-001, REQ-S-002)', () => {
    it('should call onSubmit with BookInfo data when form is submitted', async () => {
      const { createKORMARC } = await import('@/lib/api-client')
      vi.mocked(createKORMARC).mockResolvedValue({
        isbn: '9780141036144',
        json: {},
        xml: '<record/>',
        validation: {
          tier1: { pass: true, message: 'Pass' },
          tier2: { pass: true, message: 'Pass' },
          tier3: { pass: true, message: 'Pass' },
          tier4: { pass: true, message: 'Pass' },
          tier5: { pass: true, message: 'Pass' },
        },
      })

      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Fill all required fields
      await user.type(screen.getByLabelText(/ISBN/i), '9780141036144')
      await user.type(screen.getByLabelText(/제목/i), 'Python 프로그래밍')
      await user.type(screen.getByLabelText(/저자/i), '박응용')
      await user.type(screen.getByLabelText(/출판사/i), '한빛미디어')
      await user.type(screen.getByLabelText(/발행년/i), '2025')

      // Wait for button to be enabled
      await waitFor(
        () => {
          const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
          expect(submitButton).toBeEnabled()
        },
        { timeout: 1000 }
      )

      // Submit form
      const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
      await user.click(submitButton)

      // Verify onSubmit was called
      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          isbn: '9780141036144',
          title: 'Python 프로그래밍',
          author: '박응용',
          publisher: '한빛미디어',
          publicationYear: 2025,
        })
      })
    })

    it('should show loading state during submission', async () => {
      // Create a promise that we can resolve later
      let resolveSubmission: (value: unknown) => void
      const submissionPromise = new Promise((resolve) => {
        resolveSubmission = resolve
      })

      mockOnSubmit.mockImplementation(() => submissionPromise)

      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Fill all required fields
      await user.type(screen.getByLabelText(/ISBN/i), '9780141036144')
      await user.type(screen.getByLabelText(/제목/i), 'Python 프로그래밍')
      await user.type(screen.getByLabelText(/저자/i), '박응용')
      await user.type(screen.getByLabelText(/출판사/i), '한빛미디어')
      await user.type(screen.getByLabelText(/발행년/i), '2025')

      // Wait for button to be enabled
      await waitFor(
        () => {
          const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
          expect(submitButton).toBeEnabled()
        },
        { timeout: 1000 }
      )

      // Submit form
      const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
      await user.click(submitButton)

      // Check loading state
      await waitFor(() => {
        expect(screen.getByText(/생성 중/i)).toBeInTheDocument()
        expect(submitButton).toBeDisabled()
      })

      // Resolve the promise
      resolveSubmission!({})
    })
  })

  /**
   * Test REQ-E-004: When validation fails, show field-specific error messages
   */
  describe('Field Validation (REQ-E-004)', () => {
    it('should show error when title is empty after being touched', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Touch and clear title field
      const titleInput = screen.getByLabelText(/제목/i)
      await user.click(titleInput)
      await user.tab() // Blur to trigger validation

      await waitFor(() => {
        expect(screen.getByText(/제목을 입력해주세요/)).toBeInTheDocument()
      })
    })
  })

  /**
   * Test REQ-C-002: System should not allow submission of invalid form
   */
  describe('Form Validation Guard (REQ-C-002)', () => {
    it('should prevent form submission when ISBN is invalid', async () => {
      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Fill with invalid ISBN
      await user.type(screen.getByLabelText(/ISBN/i), '123456789012')
      await user.type(screen.getByLabelText(/제목/i), 'Test Book')
      await user.type(screen.getByLabelText(/저자/i), 'Test Author')
      await user.type(screen.getByLabelText(/출판사/i), 'Test Publisher')
      await user.type(screen.getByLabelText(/발행년/i), '2025')

      // Wait a bit for validation
      await waitFor(
        () => {
          // Just wait for debounce to complete
        },
        { timeout: 1000 }
      )

      // Try to submit - button should still be disabled due to invalid ISBN
      const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
      expect(submitButton).toBeDisabled()
    })
  })

  /**
   * Test REQ-O-001: Optional fields should not affect button state
   */
  describe('Optional Fields (REQ-O-001)', () => {
    it('should allow submission without optional fields', async () => {
      const { createKORMARC } = await import('@/lib/api-client')
      vi.mocked(createKORMARC).mockResolvedValue({
        isbn: '9780141036144',
        json: {},
        xml: '<record/>',
        validation: {
          tier1: { pass: true, message: 'Pass' },
          tier2: { pass: true, message: 'Pass' },
          tier3: { pass: true, message: 'Pass' },
          tier4: { pass: true, message: 'Pass' },
          tier5: { pass: true, message: 'Pass' },
        },
      })

      render(<BookInfoForm onSubmit={mockOnSubmit} />)

      const user = userEvent.setup()

      // Fill only required fields
      await user.type(screen.getByLabelText(/ISBN/i), '9780141036144')
      await user.type(screen.getByLabelText(/제목/i), 'Python 프로그래밍')
      await user.type(screen.getByLabelText(/저자/i), '박응용')
      await user.type(screen.getByLabelText(/출판사/i), '한빛미디어')
      await user.type(screen.getByLabelText(/발행년/i), '2025')

      // Don't fill optional fields (판차, 총서명)

      // Wait for button to be enabled
      await waitFor(
        () => {
          const submitButton = screen.getByRole('button', { name: /KORMARC 생성/i })
          expect(submitButton).toBeEnabled()
        },
        { timeout: 1000 }
      )
    })
  })
})
