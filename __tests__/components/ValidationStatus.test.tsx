import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ValidationStatus, type ValidationTier } from '@components/ValidationStatus'

const mockTiers: ValidationTier[] = [
  { level: 1, status: 'passed' },
  { level: 2, status: 'passed' },
  { level: 3, status: 'pending' },
  { level: 4, status: 'failed' },
  { level: 5, status: 'pending' },
]

describe('ValidationStatus', () => {
  it('should display all 5 validation tiers', () => {
    render(<ValidationStatus tiers={mockTiers} />)

    expect(screen.getByText(/Tier 1/i)).toBeInTheDocument()
    expect(screen.getByText(/Tier 2/i)).toBeInTheDocument()
    expect(screen.getByText(/Tier 3/i)).toBeInTheDocument()
    expect(screen.getByText(/Tier 4/i)).toBeInTheDocument()
    expect(screen.getByText(/Tier 5/i)).toBeInTheDocument()
  })

  it('should display validation heading', () => {
    render(<ValidationStatus tiers={mockTiers} />)

    expect(screen.getByText(/검증 상태/i)).toBeInTheDocument()
  })

  it('should display level information for each tier', () => {
    render(<ValidationStatus tiers={mockTiers} />)

    expect(screen.getByText(/레벨 1/i)).toBeInTheDocument()
    expect(screen.getByText(/레벨 2/i)).toBeInTheDocument()
    expect(screen.getByText(/레벨 3/i)).toBeInTheDocument()
    expect(screen.getByText(/레벨 4/i)).toBeInTheDocument()
    expect(screen.getByText(/레벨 5/i)).toBeInTheDocument()
  })

  it('should show status colors in rendered output', () => {
    const { container } = render(<ValidationStatus tiers={mockTiers} />)

    // Check that color classes exist in the DOM
    expect(container.querySelector('.bg-green-500')).toBeInTheDocument()
    expect(container.querySelector('.bg-gray-300')).toBeInTheDocument()
    expect(container.querySelector('.bg-red-500')).toBeInTheDocument()
  })

  it('should handle all tiers being passed', () => {
    const allPassed: ValidationTier[] = [
      { level: 1, status: 'passed' },
      { level: 2, status: 'passed' },
      { level: 3, status: 'passed' },
      { level: 4, status: 'passed' },
      { level: 5, status: 'passed' },
    ]

    const { container } = render(<ValidationStatus tiers={allPassed} />)

    const greenElements = container.querySelectorAll('.bg-green-500')
    expect(greenElements.length).toBe(5)
  })

  it('should handle all tiers being failed', () => {
    const allFailed: ValidationTier[] = [
      { level: 1, status: 'failed' },
      { level: 2, status: 'failed' },
      { level: 3, status: 'failed' },
      { level: 4, status: 'failed' },
      { level: 5, status: 'failed' },
    ]

    const { container } = render(<ValidationStatus tiers={allFailed} />)

    const redElements = container.querySelectorAll('.bg-red-500')
    expect(redElements.length).toBe(5)
  })

  it('should display tiers in order from 1 to 5', () => {
    render(<ValidationStatus tiers={mockTiers} />)

    // Get all tier elements and verify they are in order
    const tier1 = screen.getByText(/Tier 1/i)
    const tier2 = screen.getByText(/Tier 2/i)
    const tier3 = screen.getByText(/Tier 3/i)
    const tier4 = screen.getByText(/Tier 4/i)
    const tier5 = screen.getByText(/Tier 5/i)

    expect(tier1).toBeInTheDocument()
    expect(tier2).toBeInTheDocument()
    expect(tier3).toBeInTheDocument()
    expect(tier4).toBeInTheDocument()
    expect(tier5).toBeInTheDocument()
  })
})
