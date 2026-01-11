import type { BookInfo } from './validators'

/** 프리뷰 데이터 인터페이스 */
export interface PreviewData {
  kormarc: string
  json: string
  validationTiers: ValidationTier[]
}

/** 검증 티어 인터페이스 */
export interface ValidationTier {
  level: 1 | 2 | 3 | 4 | 5
  status: 'pending' | 'passed' | 'failed'
}

/**
 * KORMARC 생성 API 호출
 * POST /api/kormarc/build 엔드포인트로 책 정보를 전송하고 KORMARC 데이터를 반환
 *
 * @param data 책 정보 데이터
 * @returns KORMARC 생성 결과
 * @throws {Error} API 호출 실패 또는 서버 에러
 *
 * @example
 * const result = await buildKORMARC({
 *   isbn: '9788954687065',
 *   title: 'KORMARC 가이드',
 *   author: '한국 저자',
 *   publisher: '한국 출판사',
 *   publicationYear: 2024,
 *   description: '책 설명',
 *   classification: 'KDC-3',
 * })
 * console.log(result.kormarc) // KORMARC XML 데이터
 */
export async function buildKORMARC(data: BookInfo): Promise<PreviewData> {
  const response = await fetch('/api/kormarc/build', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }

  return response.json()
}
