import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { LoadingSpinner } from '@components/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('should show spinner when loading is true', () => {
    const { container } = render(<LoadingSpinner loading={true} />)

    const spinner = container.querySelector('[role="status"]')
    expect(spinner).toBeInTheDocument()
  })

  it('should hide spinner when loading is false', () => {
    const { container } = render(<LoadingSpinner loading={false} />)

    const spinner = container.querySelector('[role="status"]')
    expect(spinner).not.toBeInTheDocument()
  })

  it('should display loading message when loading is true', () => {
    const { getByText } = render(<LoadingSpinner loading={true} />)

    expect(getByText(/KORMARC 생성 중/i)).toBeInTheDocument()
  })

  it('should have animated spinner element', () => {
    const { container } = render(<LoadingSpinner loading={true} />)

    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('should return empty when not loading', () => {
    const { container } = render(<LoadingSpinner loading={false} />)

    expect(container.firstChild).toBeNull()
  })

  it('should show spinner with correct styling', () => {
    const { container } = render(<LoadingSpinner loading={true} />)

    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toHaveClass('animate-spin')
    expect(spinner).toHaveClass('w-5')
    expect(spinner).toHaveClass('h-5')
  })

  it('should display loading text next to spinner', () => {
    const { container } = render(<LoadingSpinner loading={true} />)

    const textSpan = container.querySelector('span')
    expect(textSpan?.textContent).toMatch(/KORMARC 생성 중/)
  })
})
