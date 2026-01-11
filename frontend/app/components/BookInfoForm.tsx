/**
 * BookInfoForm Component - GREEN Phase Implementation
 *
 * TDD Implementation for SPEC-FRONTEND-001
 * All tests should pass after this implementation
 *
 * Requirements covered:
 * - REQ-U-001: Next.js web UI with BookInfo form (7 fields)
 * - REQ-E-002: ISBN real-time validation with 500ms debounce
 * - REQ-S-001: Button disabled when required fields empty
 * - REQ-E-001: Form submission calls API
 * - REQ-S-002: Loading state during API request
 * - REQ-E-004: Field-specific error messages
 * - REQ-C-002: Prevent invalid form submission
 * - REQ-O-001: Optional fields don't affect validation
 */

'use client'

import { useState, useCallback, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { bookInfoSchema, type BookInfoFormData, validateISBN, createISBNValidator } from '@/lib/validation'
import type { BookInfo, BookInfoFormProps } from '@/lib/types'

/**
 * BookInfoForm Component
 *
 * Provides form for entering book information to generate KORMARC records
 */
export function BookInfoForm({ onSubmit, isLoading = false, initialData }: BookInfoFormProps) {
  // Form state with React Hook Form + Zod validation
  const {
    register,
    handleSubmit,
    formState: { errors, touchedFields },
    watch,
    trigger,
  } = useForm<BookInfoFormData>({
    resolver: zodResolver(bookInfoSchema),
    defaultValues: {
      isbn: initialData?.isbn || '',
      title: initialData?.title || '',
      author: initialData?.author || '',
      publisher: initialData?.publisher || '',
      publicationYear: initialData?.publicationYear || new Date().getFullYear(),
      edition: initialData?.edition || '',
      seriesName: initialData?.seriesName || '',
    },
    mode: 'onBlur', // Validate on field blur
  })

  // Watch all fields for validation
  const watchedFields = watch()

  // ISBN validation state
  const [isbnValidation, setIsbnValidation] = useState<{
    isValid: boolean
    message: string
  }>({
    isValid: false,
    message: '',
  })

  // Create debounced ISBN validator
  const validateISBNDebounced = useCallback(
    createISBNValidator(500),
    []
  )

  // Watch ISBN field for real-time validation
  const isbnValue = watch('isbn')

  useEffect(() => {
    if (!isbnValue) {
      setIsbnValidation({ isValid: false, message: '' })
      return
    }

    // Only validate if we have 13 digits
    if (/^\d{13}$/.test(isbnValue)) {
      validateISBNDebounced(isbnValue, (result) => {
        setIsbnValidation({
          isValid: result.isValid,
          message: result.message,
        })
      })
    } else if (isbnValue.length >= 10) {
      // Show error for wrong length
      const result = validateISBN(isbnValue)
      setIsbnValidation({
        isValid: result.isValid,
        message: result.message,
      })
    } else {
      // Clear validation for short input
      setIsbnValidation({ isValid: false, message: '' })
    }
  }, [isbnValue, validateISBNDebounced])

  // Check if all required fields are filled
  const hasRequiredFields = !!(
    watchedFields.isbn &&
    watchedFields.title &&
    watchedFields.author &&
    watchedFields.publisher &&
    watchedFields.publicationYear
  )

  // Check if form is valid (Zod validation)
  const isFormValid = Object.keys(errors).length === 0 && hasRequiredFields

  // Form submission handler
  const onFormSubmit = useCallback(
    async (data: BookInfoFormData) => {
      try {
        await onSubmit(data as BookInfo)
      } catch (error) {
        console.error('Form submission error:', error)
        throw error
      }
    },
    [onSubmit]
  )

  // Get input border color based on validation state
  const getInputBorderColor = (fieldName: keyof BookInfoFormData) => {
    // Special handling for ISBN
    if (fieldName === 'isbn') {
      if (isbnValidation.message) {
        return isbnValidation.isValid ? 'border-green-500' : 'border-red-500'
      }
      if (errors.isbn) return 'border-red-500'
      return 'border-gray-300'
    }

    // Standard field handling
    if (errors[fieldName]) return 'border-red-500'
    if (touchedFields[fieldName] && !errors[fieldName]) return 'border-green-500'
    return 'border-gray-300'
  }

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      {/* ISBN Field - Required */}
      <div className="space-y-2">
        <Label htmlFor="isbn">
          ISBN <span className="text-red-500">*</span>
        </Label>
        <Input
          id="isbn"
          type="text"
          inputMode="numeric"
          placeholder="978..."
          className={getInputBorderColor('isbn')}
          disabled={isLoading}
          {...register('isbn')}
          aria-invalid={!!errors.isbn || !isbnValidation.isValid}
          aria-describedby={
            errors.isbn
              ? 'isbn-error'
              : isbnValidation.message
                ? 'isbn-validation'
                : undefined
          }
        />
        {/* ISBN Validation Message */}
        {isbnValidation.message && (
          <p
            id="isbn-validation"
            className={`text-sm ${isbnValidation.isValid ? 'text-green-600' : 'text-red-500'}`}
            role="alert"
          >
            {isbnValidation.message}
          </p>
        )}
        {/* ISBN Error Message */}
        {errors.isbn && !isbnValidation.message && (
          <p id="isbn-error" className="text-sm text-red-500" role="alert">
            {errors.isbn.message}
          </p>
        )}
      </div>

      {/* Title Field - Required */}
      <div className="space-y-2">
        <Label htmlFor="title">
          제목 <span className="text-red-500">*</span>
        </Label>
        <Input
          id="title"
          type="text"
          placeholder="도서명을 입력하세요"
          className={getInputBorderColor('title')}
          disabled={isLoading}
          {...register('title')}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        {errors.title && (
          <p id="title-error" className="text-sm text-red-500" role="alert">
            {errors.title.message}
          </p>
        )}
      </div>

      {/* Author Field - Required */}
      <div className="space-y-2">
        <Label htmlFor="author">
          저자 <span className="text-red-500">*</span>
        </Label>
        <Input
          id="author"
          type="text"
          placeholder="저자명을 입력하세요"
          className={getInputBorderColor('author')}
          disabled={isLoading}
          {...register('author')}
          aria-invalid={!!errors.author}
          aria-describedby={errors.author ? 'author-error' : undefined}
        />
        {errors.author && (
          <p id="author-error" className="text-sm text-red-500" role="alert">
            {errors.author.message}
          </p>
        )}
      </div>

      {/* Publisher Field - Required */}
      <div className="space-y-2">
        <Label htmlFor="publisher">
          출판사 <span className="text-red-500">*</span>
        </Label>
        <Input
          id="publisher"
          type="text"
          placeholder="출판사를 입력하세요"
          className={getInputBorderColor('publisher')}
          disabled={isLoading}
          {...register('publisher')}
          aria-invalid={!!errors.publisher}
          aria-describedby={errors.publisher ? 'publisher-error' : undefined}
        />
        {errors.publisher && (
          <p id="publisher-error" className="text-sm text-red-500" role="alert">
            {errors.publisher.message}
          </p>
        )}
      </div>

      {/* Publication Year Field - Required */}
      <div className="space-y-2">
        <Label htmlFor="publicationYear">
          발행년 <span className="text-red-500">*</span>
        </Label>
        <Input
          id="publicationYear"
          type="number"
          placeholder="2025"
          className={getInputBorderColor('publicationYear')}
          disabled={isLoading}
          {...register('publicationYear', { valueAsNumber: true })}
          aria-invalid={!!errors.publicationYear}
          aria-describedby={errors.publicationYear ? 'publicationYear-error' : undefined}
        />
        {errors.publicationYear && (
          <p id="publicationYear-error" className="text-sm text-red-500" role="alert">
            {errors.publicationYear.message}
          </p>
        )}
      </div>

      {/* Edition Field - Optional */}
      <div className="space-y-2">
        <Label htmlFor="edition">판차 (선택)</Label>
        <Input
          id="edition"
          type="text"
          placeholder="개정판, 초판 등"
          className={getInputBorderColor('edition')}
          disabled={isLoading}
          {...register('edition')}
          aria-invalid={!!errors.edition}
          aria-describedby={errors.edition ? 'edition-error' : undefined}
        />
        {errors.edition && (
          <p id="edition-error" className="text-sm text-red-500" role="alert">
            {errors.edition.message}
          </p>
        )}
      </div>

      {/* Series Name Field - Optional */}
      <div className="space-y-2">
        <Label htmlFor="seriesName">총서명 (선택)</Label>
        <Input
          id="seriesName"
          type="text"
          placeholder="시리즈명을 입력하세요"
          className={getInputBorderColor('seriesName')}
          disabled={isLoading}
          {...register('seriesName')}
          aria-invalid={!!errors.seriesName}
          aria-describedby={errors.seriesName ? 'seriesName-error' : undefined}
        />
        {errors.seriesName && (
          <p id="seriesName-error" className="text-sm text-red-500" role="alert">
            {errors.seriesName.message}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={!isFormValid || isLoading}
        className="w-full"
        title={!isFormValid ? '필수 필드를 모두 입력해주세요' : undefined}
      >
        {isLoading ? '생성 중...' : 'KORMARC 생성'}
      </Button>
    </form>
  )
}
