'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { bookInfoSchema, BookInfo } from '@lib/validators'
import { useState } from 'react'

/** API 엔드포인트 상수 */
const API_ENDPOINT = '/api/kormarc/build'

/** 폼 필드 설정 인터페이스 */
interface FormFieldConfig {
  name: keyof BookInfo
  label: string
  placeholder: string
  type: string
}

/** 폼 필드 설정 배열 */
const FORM_FIELDS: FormFieldConfig[] = [
  {
    name: 'isbn',
    label: 'ISBN',
    placeholder: '9788954687065',
    type: 'text',
  },
  {
    name: 'title',
    label: '제목',
    placeholder: '한국 도서관 자동화',
    type: 'text',
  },
  {
    name: 'author',
    label: '저자',
    placeholder: '홍길동',
    type: 'text',
  },
  {
    name: 'publisher',
    label: '출판사',
    placeholder: '출판사',
    type: 'text',
  },
  {
    name: 'publicationYear',
    label: '발행년',
    placeholder: '2024',
    type: 'number',
  },
]

/**
 * BookInfoForm 컴포넌트
 *
 * 도서 정보를 입력받아 KORMARC를 생성하기 위한 폼입니다.
 * React Hook Form과 Zod를 이용한 클라이언트 검증을 수행합니다.
 */
export function BookInfoForm() {
  const [loading, setLoading] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<BookInfo>({
    resolver: zodResolver(bookInfoSchema),
    mode: 'onChange',
  })

  /**
   * 폼 제출 핸들러
   *
   * 검증된 도서 정보를 API로 전송하여 KORMARC를 생성합니다.
   * @param data - 검증된 도서 정보
   */
  const onSubmit = async (data: BookInfo) => {
    setLoading(true)
    try {
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('KORMARC 생성 실패')
      }

      // 성공 처리
      const result = await response.json()
      console.log('KORMARC created:', result)
    } catch (error) {
      console.error('Error creating KORMARC:', error)
    } finally {
      setLoading(false)
    }
  }

  /**
   * 폼 필드 렌더링 함수
   * @param field - 폼 필드 설정
   */
  const renderFormField = (field: FormFieldConfig) => {
    const fieldName = field.name
    const fieldError = errors[fieldName]

    return (
      <div key={fieldName}>
        <label htmlFor={fieldName} className="block font-medium text-gray-700">
          {field.label}
        </label>
        <input
          {...register(
            fieldName,
            fieldName === 'publicationYear' ? { valueAsNumber: true } : undefined
          )}
          id={fieldName}
          type={field.type}
          placeholder={field.placeholder}
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
        {fieldError && (
          <span className="mt-1 text-sm text-red-600">{fieldError.message}</span>
        )}
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {FORM_FIELDS.map(renderFormField)}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!isValid || loading}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'KORMARC 생성 중...' : 'KORMARC 생성'}
      </button>
    </form>
  )
}
