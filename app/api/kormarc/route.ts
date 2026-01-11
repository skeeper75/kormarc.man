import type { BookInfo } from '@lib/validators'
import type { PreviewData } from '@lib/api-client'

/**
 * POST /api/kormarc/build
 * 책 정보를 받아서 백엔드 API에 전달하고 KORMARC 데이터를 반환
 *
 * @param request 클라이언트 요청
 * @returns KORMARC 생성 결과를 포함한 Response
 *
 * @example
 * curl -X POST http://localhost:3000/api/kormarc/build \
 *   -H "Content-Type: application/json" \
 *   -d '{"isbn": "...", "title": "...", ...}'
 */
export async function POST(request: Request): Promise<Response> {
  try {
    const data = (await request.json()) as BookInfo

    // 백엔드 API 호출
    // 환경변수에서 백엔드 URL 가져오기 (기본값: localhost:8000)
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/kormarc/build`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      return Response.json(
        { error: 'Backend error', status: response.status },
        { status: response.status }
      )
    }

    const result = (await response.json()) as PreviewData
    return Response.json(result)
  } catch (error) {
    console.error('API route error:', error)
    return Response.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Internal server error',
      },
      { status: 500 }
    )
  }
}
