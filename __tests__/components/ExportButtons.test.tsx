import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ExportButtons, type PreviewData } from '@components/ExportButtons'

const mockData: PreviewData = {
  json: '{"status": "success", "data": {"isbn": "9788954687065"}}',
  kormarc: '<record><leader>00000cam  2200000 i 4500</leader></record>',
  validationTiers: [],
}

// Mock navigator.clipboard
const mockClipboard = {
  writeText: vi.fn(),
}

Object.assign(navigator, {
  clipboard: mockClipboard,
})

// Mock URL.createObjectURL
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')

describe('ExportButtons', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockClipboard.writeText.mockResolvedValue(undefined)
  })

  it('should display JSON download button', () => {
    render(<ExportButtons data={mockData} />)
    expect(screen.getByRole('button', { name: /JSON.*다운로드/i })).toBeInTheDocument()
  })

  it('should display JSON copy button', () => {
    render(<ExportButtons data={mockData} />)
    expect(screen.getByRole('button', { name: /JSON.*복사/i })).toBeInTheDocument()
  })

  it('should display KORMARC download button', () => {
    render(<ExportButtons data={mockData} />)
    expect(screen.getByRole('button', { name: /KORMARC.*다운로드/i })).toBeInTheDocument()
  })

  it('should display KORMARC copy button', () => {
    render(<ExportButtons data={mockData} />)
    expect(screen.getByRole('button', { name: /KORMARC.*복사/i })).toBeInTheDocument()
  })

  it('should have copy buttons that are clickable', async () => {
    const user = userEvent.setup()
    render(<ExportButtons data={mockData} />)

    const copyJsonBtn = screen.getByRole('button', { name: /JSON.*복사/i })
    const copyKormarcBtn = screen.getByRole('button', { name: /KORMARC.*복사/i })

    // Buttons should be enabled and clickable
    expect(copyJsonBtn).toBeEnabled()
    expect(copyKormarcBtn).toBeEnabled()

    await user.click(copyJsonBtn)
    await user.click(copyKormarcBtn)

    // If no error thrown, click was successful
    expect(copyJsonBtn).toBeInTheDocument()
    expect(copyKormarcBtn).toBeInTheDocument()
  })

  it('should have proper button styling', () => {
    render(<ExportButtons data={mockData} />)

    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBe(4)
    buttons.forEach((button) => {
      expect(button).toHaveClass('btn')
    })
  })

  it('should display all four buttons in correct order', () => {
    render(<ExportButtons data={mockData} />)

    const buttons = screen.getAllByRole('button')
    expect(buttons[0]).toHaveTextContent('JSON 다운로드')
    expect(buttons[1]).toHaveTextContent('JSON 복사')
    expect(buttons[2]).toHaveTextContent('KORMARC 다운로드')
    expect(buttons[3]).toHaveTextContent('KORMARC 복사')
  })
})
