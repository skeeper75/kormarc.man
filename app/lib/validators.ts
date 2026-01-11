import { z } from 'zod'

/** ISBN-13 형식 정규표현식 */
const ISBN_PATTERN = /^\d{13}$/

/** ISBN-13에서 체크섬 계산 기준 홀수 자리 가중치 */
const ODD_POSITION_WEIGHT = 1
/** ISBN-13에서 체크섬 계산 기준 짝수 자리 가중치 */
const EVEN_POSITION_WEIGHT = 3
/** 체크섬 계산 기준 모듈로 */
const CHECKSUM_MODULO = 10

/**
 * ISBN-13 유효성 검사 함수
 *
 * ISBN-13은 13자리 숫자로 구성되며, 마지막 자리는 체크섬입니다.
 * 체크섬은 다음과 같이 계산됩니다:
 * 1. 처음 12자리를 순서대로 가중치(1, 3, 1, 3, ...)와 곱함
 * 2. 합을 10으로 나눈 나머지를 구함
 * 3. 10에서 나머지를 뺀 값(또는 0이면 0)이 체크섬
 *
 * @param isbn - 검증할 ISBN 문자열
 * @returns ISBN이 유효하면 true, 그렇지 않으면 false
 */
export function validateISBN(isbn: string): boolean {
  // ISBN-13은 정확히 13자리 숫자여야 함
  if (!ISBN_PATTERN.test(isbn)) {
    return false
  }

  // 체크섬 검증
  let sum = 0
  for (let i = 0; i < 12; i++) {
    const digit = parseInt(isbn[i], 10)
    const multiplier = i % 2 === 0 ? ODD_POSITION_WEIGHT : EVEN_POSITION_WEIGHT
    sum += digit * multiplier
  }

  const checkDigit = (CHECKSUM_MODULO - (sum % CHECKSUM_MODULO)) % CHECKSUM_MODULO
  return checkDigit === parseInt(isbn[12], 10)
}

/** 발행년도의 최소값 */
const MIN_PUBLICATION_YEAR = 1900

/**
 * 현재 연도를 동적으로 계산하는 함수
 * @returns 현재 연도
 */
const getCurrentYear = (): number => new Date().getFullYear()

/**
 * 도서 정보 Zod 스키마
 *
 * KORMARC 생성에 필요한 기본 도서 정보를 정의합니다.
 * - isbn: ISBN-13 형식의 13자리 숫자 (유효한 체크섬 필수)
 * - title: 도서 제목 (필수)
 * - author: 저자명 (필수)
 * - publisher: 출판사명 (필수)
 * - publicationYear: 발행년도 (1900년 이상, 현재년도 이하)
 *
 * strict() 옵션으로 인해 정의되지 않은 필드는 거부됩니다.
 */
export const bookInfoSchema = z.object({
  isbn: z.string()
    .min(1, 'ISBN은 필수입니다')
    .refine(validateISBN, 'ISBN-13 형식이 아니거나 체크섬이 유효하지 않습니다'),
  title: z.string().min(1, '제목은 필수입니다'),
  author: z.string().min(1, '저자는 필수입니다'),
  publisher: z.string().min(1, '출판사는 필수입니다'),
  publicationYear: z.number()
    .min(MIN_PUBLICATION_YEAR, `발행년도는 ${MIN_PUBLICATION_YEAR}년 이상이어야 합니다`)
    .max(getCurrentYear(), `발행년도는 ${getCurrentYear()}년 이하여야 합니다`),
}).strict()

/**
 * BookInfo 타입
 *
 * 도서 정보 스키마로부터 생성되는 TypeScript 타입
 * 폼 입력과 API 요청/응답에 사용됩니다.
 */
export type BookInfo = z.infer<typeof bookInfoSchema>
