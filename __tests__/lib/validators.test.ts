import { describe, it, expect } from 'vitest'
import { validateISBN, bookInfoSchema } from '@lib/validators'

describe('validateISBN', () => {
  it('should validate correct ISBN-13', () => {
    expect(validateISBN('9788954687065')).toBe(true)
  })

  it('should validate another correct ISBN-13', () => {
    expect(validateISBN('9781491927281')).toBe(true)
  })

  it('should reject invalid ISBN with wrong checksum', () => {
    expect(validateISBN('9788954687064')).toBe(false)
  })

  it('should reject ISBN with incorrect length', () => {
    expect(validateISBN('12345')).toBe(false)
  })

  it('should reject ISBN with non-numeric characters', () => {
    expect(validateISBN('978895468706X')).toBe(false)
  })

  it('should reject empty string', () => {
    expect(validateISBN('')).toBe(false)
  })

  it('should reject ISBN-10 format', () => {
    expect(validateISBN('0306406152')).toBe(false)
  })
})

describe('bookInfoSchema', () => {
  const validData = {
    isbn: '9788954687065',
    title: '한국 도서관 자동화',
    author: '홍길동',
    publisher: '출판사',
    publicationYear: 2024,
  }

  it('should validate complete book info', () => {
    expect(() => bookInfoSchema.parse(validData)).not.toThrow()
  })

  it('should return correct type for valid data', () => {
    const result = bookInfoSchema.parse(validData)
    expect(result.isbn).toBe('9788954687065')
    expect(result.title).toBe('한국 도서관 자동화')
    expect(result.author).toBe('홍길동')
    expect(result.publisher).toBe('출판사')
    expect(result.publicationYear).toBe(2024)
  })

  it('should reject missing isbn', () => {
    const invalidData = { ...validData, isbn: '' }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject missing title', () => {
    const invalidData = { ...validData, title: '' }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject missing author', () => {
    const invalidData = { ...validData, author: '' }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject missing publisher', () => {
    const invalidData = { ...validData, publisher: '' }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject year below minimum', () => {
    const invalidData = { ...validData, publicationYear: 1800 }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject year above current year', () => {
    const currentYear = new Date().getFullYear()
    const invalidData = { ...validData, publicationYear: currentYear + 1 }
    expect(() => bookInfoSchema.parse(invalidData)).toThrow()
  })

  it('should reject extra fields', () => {
    const dataWithExtra = {
      ...validData,
      extraField: 'should be rejected',
    }
    expect(() => bookInfoSchema.parse(dataWithExtra)).toThrow()
  })
})
