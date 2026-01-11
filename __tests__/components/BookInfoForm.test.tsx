import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BookInfoForm } from '@components/BookInfoForm'

describe('BookInfoForm Component', () => {
  it('should render form with all input fields', () => {
    render(<BookInfoForm />)

    expect(screen.getByLabelText(/isbn/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/제목/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/저자/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/출판사/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/발행년/i)).toBeInTheDocument()
  })

  it('should render submit button', () => {
    render(<BookInfoForm />)

    expect(screen.getByRole('button', { name: /생성/i })).toBeInTheDocument()
  })

  it('should disable submit button initially', () => {
    render(<BookInfoForm />)

    const submitButton = screen.getByRole('button', { name: /생성/i })
    expect(submitButton).toBeDisabled()
  })

  it('should disable submit button when required fields are empty', async () => {
    const user = userEvent.setup()
    render(<BookInfoForm />)

    const submitButton = screen.getByRole('button', { name: /생성/i })
    expect(submitButton).toBeDisabled()

    // Try to type in one field
    const titleInput = screen.getByLabelText(/제목/i)
    await user.type(titleInput, 'Test Title')

    // Button should still be disabled since other required fields are empty
    expect(submitButton).toBeDisabled()
  })

  it('should enable submit button when all required fields are filled', async () => {
    const user = userEvent.setup()
    render(<BookInfoForm />)

    const isbnInput = screen.getByLabelText(/isbn/i)
    const titleInput = screen.getByLabelText(/제목/i)
    const authorInput = screen.getByLabelText(/저자/i)
    const publisherInput = screen.getByLabelText(/출판사/i)
    const yearInput = screen.getByLabelText(/발행년/i)

    await user.type(isbnInput, '9788954687065')
    await user.type(titleInput, '한국 도서관 자동화')
    await user.type(authorInput, '홍길동')
    await user.type(publisherInput, '출판사')
    await user.type(yearInput, '2024')

    const submitButton = screen.getByRole('button', { name: /생성/i })

    await waitFor(() => {
      expect(submitButton).toBeEnabled()
    })
  })

  it('should show error message for invalid ISBN', async () => {
    const user = userEvent.setup()
    render(<BookInfoForm />)

    const isbnInput = screen.getByLabelText(/isbn/i)
    await user.type(isbnInput, '12345')

    // Trigger validation
    await user.click(screen.getByRole('button', { name: /생성/i }))

    await waitFor(() => {
      expect(screen.getByText(/isbn/i, { selector: 'span' })).toBeInTheDocument()
    })
  })

  it('should show error message for empty title', async () => {
    const user = userEvent.setup()
    render(<BookInfoForm />)

    const titleInput = screen.getByLabelText(/제목/i) as HTMLInputElement

    // Fill and then clear
    await user.type(titleInput, 'Test')
    await user.clear(titleInput)

    // Trigger validation by clicking submit
    const submitButton = screen.getByRole('button', { name: /생성/i })

    await waitFor(() => {
      expect(submitButton).toBeDisabled()
    })
  })

  it('should display loading state while submitting', async () => {
    const user = userEvent.setup()

    // Mock fetch
    global.fetch = vi.fn(() =>
      new Promise(resolve => {
        setTimeout(() => {
          resolve(new Response(JSON.stringify({ success: true })))
        }, 100)
      })
    )

    render(<BookInfoForm />)

    const isbnInput = screen.getByLabelText(/isbn/i)
    const titleInput = screen.getByLabelText(/제목/i)
    const authorInput = screen.getByLabelText(/저자/i)
    const publisherInput = screen.getByLabelText(/출판사/i)
    const yearInput = screen.getByLabelText(/발행년/i)

    await user.type(isbnInput, '9788954687065')
    await user.type(titleInput, '한국 도서관 자동화')
    await user.type(authorInput, '홍길동')
    await user.type(publisherInput, '출판사')
    await user.type(yearInput, '2024')

    const submitButton = screen.getByRole('button', { name: /생성/i })

    await waitFor(() => {
      expect(submitButton).toBeEnabled()
    })

    await user.click(submitButton)

    // Check for loading text
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /생성 중/i })).toBeInTheDocument()
    })
  })

  it('should call API with correct data when form is submitted', async () => {
    const user = userEvent.setup()

    const mockFetch = vi.fn(() =>
      Promise.resolve(new Response(JSON.stringify({ success: true })))
    )
    global.fetch = mockFetch

    render(<BookInfoForm />)

    const isbnInput = screen.getByLabelText(/isbn/i)
    const titleInput = screen.getByLabelText(/제목/i)
    const authorInput = screen.getByLabelText(/저자/i)
    const publisherInput = screen.getByLabelText(/출판사/i)
    const yearInput = screen.getByLabelText(/발행년/i)

    const testData = {
      isbn: '9788954687065',
      title: '한국 도서관 자동화',
      author: '홍길동',
      publisher: '출판사',
      year: '2024',
    }

    await user.type(isbnInput, testData.isbn)
    await user.type(titleInput, testData.title)
    await user.type(authorInput, testData.author)
    await user.type(publisherInput, testData.publisher)
    await user.type(yearInput, testData.year)

    const submitButton = screen.getByRole('button', { name: /생성/i })

    await waitFor(() => {
      expect(submitButton).toBeEnabled()
    })

    await user.click(submitButton)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/kormarc/build',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining(testData.isbn),
        })
      )
    })
  })
})
