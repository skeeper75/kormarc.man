/**
 * Zod validation schemas and custom validators for KORMARC Frontend
 * ISBN validation with Luhn checksum algorithm
 */

import { z } from 'zod';
import type { BookInfo, ISBNValidationResult } from './types';

/**
 * Luhn checksum algorithm for ISBN-13 validation
 * @param isbn - 13-digit ISBN string
 * @returns true if checksum is valid
 */
export function validateISBNSummary(isbn: string): boolean {
  // Remove any non-digit characters
  const digits = isbn.replace(/\D/g, '');

  // Must be exactly 13 digits
  if (digits.length !== 13) {
    return false
  }

  // Calculate Luhn checksum
  let sum = 0
  for (let i = 0; i < 13; i++) {
    const digit = parseInt(digits[i], 10)
    // Multiply by 1 for odd positions, 3 for even positions
    sum += (i % 2 === 0) ? digit : digit * 3
  }

  // Check if sum is divisible by 10
  return sum % 10 === 0
}

/**
 * Validate ISBN format and checksum
 * @param isbn - ISBN string to validate
 * @returns ISBNValidationResult with detailed error information
 */
export function validateISBN(isbn: string): ISBNValidationResult {
  // Remove hyphens and spaces
  const cleaned = isbn.replace(/[-\s]/g, '')

  // Check length
  if (cleaned.length !== 13) {
    return {
      isValid: false,
      message: 'ISBN은 13자리여야 합니다',
      errorType: 'length',
    }
  }

  // Check if all digits
  if (!/^\d{13}$/.test(cleaned)) {
    return {
      isValid: false,
      message: 'ISBN은 숫자로만 구성되어야 합니다',
      errorType: 'format',
    }
  }

  // Check Luhn checksum
  if (!validateISBNSummary(cleaned)) {
    return {
      isValid: false,
      message: 'ISBN 체크섬이 올바르지 않습니다',
      errorType: 'checksum',
    }
  }

  return {
    isValid: true,
    message: '유효한 ISBN입니다',
  }
}

/**
 * Custom Zod refiner for ISBN validation
 */
export const isbnSchema = z.string().min(1, 'ISBN을 입력해주세요').refine(
  (value) => validateISBN(value).isValid,
  (value) => {
    const result = validateISBN(value)
    return { message: result.message }
  }
)

/**
 * Zod schema for BookInfo form validation
 * Aligns with Pydantic BookInfoBase from SPEC-WEB-001 backend
 */
export const bookInfoSchema = z.object({
  isbn: isbnSchema,
  title: z.string().min(1, '제목을 입력해주세요').max(500, '제목은 500자 이하여야 합니다'),
  author: z.string().min(1, '저자를 입력해주세요').max(200, '저자명은 200자 이하여야 합니다'),
  publisher: z.string().min(1, '출판사를 입력해주세요').max(200, '출판사는 200자 이하여야 합니다'),
  publicationYear: z
    .number({ invalid_type_error: '발행년은 숫자여야 합니다' })
    .int('발행년은 정수여야 합니다')
    .min(1000, '유효한 발행년을 입력해주세요')
    .max(new Date().getFullYear() + 10, '발행년이 미래여야 합니다'),
  edition: z.string().max(100, '판차는 100자 이하여야 합니다').optional(),
  seriesName: z.string().max(200, '총서명은 200자 이하여야 합니다').optional(),
})

// Type inference from schema
export type BookInfoFormData = z.infer<typeof bookInfoSchema>

/**
 * Validate BookInfo data against schema
 * @param data - Partial BookInfo data to validate
 * @returns Zod validation result
 */
export function validateBookInfo(data: unknown) {
  return bookInfoSchema.safeParse(data)
}

/**
 * Get error message for a specific field
 * @param field - Field name
 * @param error - Zod error
 * @returns Error message or undefined
 */
export function getFieldError(
  field: keyof BookInfo,
  error: z.ZodError | null
): string | undefined {
  if (!error) return undefined

  const fieldError = error.issues.find((issue) =>
    issue.path.includes(field)
  )

  return fieldError?.message
}

/**
 * Real-time validation for ISBN input
 * Debounced validation function
 */
export function createISBNValidator(debounceMs = 500) {
  let timeoutId: ReturnType<typeof setTimeout> | null = null

  return (isbn: string, callback: (result: ISBNValidationResult) => void) => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    timeoutId = setTimeout(() => {
      const result = validateISBN(isbn)
      callback(result)
      timeoutId = null
    }, debounceMs)
  }
}

/**
 * Check if all required fields are present
 * @param data - BookInfo data
 * @returns true if all required fields have values
 */
export function hasRequiredFields(data: Partial<BookInfo>): boolean {
  return !!(
    data.isbn &&
    data.title &&
    data.author &&
    data.publisher &&
    data.publicationYear
  )
}

/**
 * Get empty BookInfo form state
 */
export function getEmptyBookInfo(): BookInfoFormData {
  return {
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publicationYear: new Date().getFullYear(),
    edition: '',
    seriesName: '',
  }
}
