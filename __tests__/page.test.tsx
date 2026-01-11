import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import HomePage from '../app/page'

// Mock the API client
vi.mock('@lib/api-client', () => ({
  buildKORMARC: vi.fn(async () => ({
    json: '{"status": "success"}',
    xml: '<record/>',
    validationTiers: [
      { level: 1, status: 'passed' },
      { level: 2, status: 'passed' },
      { level: 3, status: 'passed' },
      { level: 4, status: 'passed' },
      { level: 5, status: 'passed' },
    ],
  })),
}))

describe('Home Page', () => {
  it('should render page title', () => {
    render(<HomePage />)
    expect(screen.getAllByText(/KORMARC 생성기/i).length).toBeGreaterThan(0)
  })

  it('should render section headings', () => {
    render(<HomePage />)
    expect(screen.getByText(/책 정보 입력/i)).toBeInTheDocument()
  })

  it('should display initial instruction message', () => {
    render(<HomePage />)
    expect(
      screen.getByText(/책 정보를 입력하고.*KORMARC 생성.*버튼을 클릭하세요/i)
    ).toBeInTheDocument()
  })

  it('should render input fields', () => {
    render(<HomePage />)
    const inputs = screen.getAllByRole('textbox')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('should have submit button', () => {
    render(<HomePage />)
    expect(screen.getByRole('button', { name: /생성/i })).toBeInTheDocument()
  })

  it('should render footer with version info', () => {
    render(<HomePage />)
    expect(screen.getByText(/v1.0.0/i)).toBeInTheDocument()
  })

  it('should have header with description', () => {
    render(<HomePage />)
    expect(
      screen.getByText(
        /한국 도서관 자동화 자료형식\(KORMARC\) 레코드를 생성합니다/i
      )
    ).toBeInTheDocument()
  })

  it('should render multiple headings', () => {
    render(<HomePage />)

    const headings = screen.getAllByRole('heading')
    expect(headings.length).toBeGreaterThan(0)
  })
})
