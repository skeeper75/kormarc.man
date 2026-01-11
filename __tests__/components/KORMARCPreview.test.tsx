import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { KORMARCPreview, type PreviewData } from '@components/KORMARCPreview'

const mockData: PreviewData = {
  json: '{"status": "success", "data": {"isbn": "9788954687065"}}',
  kormarc: '<record><leader>00000cam  2200000 i 4500</leader></record>',
  validationTiers: [],
}

describe('KORMARCPreview', () => {
  it('should display JSON and KORMARC tabs', () => {
    render(<KORMARCPreview data={mockData} />)

    expect(screen.getByRole('tab', { name: /JSON/i })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: /KORMARC/i })).toBeInTheDocument()
  })

  it('should display JSON content by default', () => {
    render(<KORMARCPreview data={mockData} />)

    expect(screen.getByText(mockData.json)).toBeInTheDocument()
  })

  it('should switch to KORMARC when clicking KORMARC tab', async () => {
    const user = userEvent.setup()
    const { container } = render(<KORMARCPreview data={mockData} />)

    const kormarcTab = screen.getByRole('tab', { name: /KORMARC/i })
    await user.click(kormarcTab)

    const preElement = container.querySelector('pre')
    expect(preElement?.textContent).toBe(mockData.kormarc)
  })

  it('should switch back to JSON when clicking JSON tab', async () => {
    const user = userEvent.setup()
    const { container } = render(<KORMARCPreview data={mockData} />)

    const kormarcTab = screen.getByRole('tab', { name: /KORMARC/i })
    await user.click(kormarcTab)
    let preElement = container.querySelector('pre')
    expect(preElement?.textContent).toBe(mockData.kormarc)

    const jsonTab = screen.getByRole('tab', { name: /JSON/i })
    await user.click(jsonTab)
    preElement = container.querySelector('pre')
    expect(preElement?.textContent).toBe(mockData.json)
  })

  it('should have JSON tab active initially', () => {
    render(<KORMARCPreview data={mockData} />)

    const jsonTab = screen.getByRole('tab', { name: /JSON/i })
    expect(jsonTab).toHaveAttribute('aria-selected', 'true')
  })

  it('should highlight active tab visually', async () => {
    const user = userEvent.setup()
    render(<KORMARCPreview data={mockData} />)

    const kormarcTab = screen.getByRole('tab', { name: /KORMARC/i })
    await user.click(kormarcTab)

    expect(kormarcTab).toHaveAttribute('aria-selected', 'true')
  })

  it('should display content in a code block style', () => {
    render(<KORMARCPreview data={mockData} />)

    const preElement = screen.getByRole('region')
    expect(preElement).toBeInTheDocument()
    expect(preElement.tagName).toBe('PRE')
  })

  it('should handle empty strings gracefully', () => {
    const emptyData: PreviewData = {
      json: '',
      kormarc: '',
      validationTiers: [],
    }

    render(<KORMARCPreview data={emptyData} />)
    expect(screen.getByRole('tab', { name: /JSON/i })).toBeInTheDocument()
  })
})
