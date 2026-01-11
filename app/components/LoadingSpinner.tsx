'use client'

/**
 * LoadingSpinner 컴포넌트
 * KORMARC 생성 중일 때 로딩 상태를 표시하는 스피너
 *
 * @param loading 로딩 상태 (true일 때만 표시)
 * @example
 * <LoadingSpinner loading={isLoading} />
 */
export function LoadingSpinner({ loading }: { loading: boolean }) {
  if (!loading) return null

  return (
    <div
      role="status"
      className="flex items-center gap-2 py-4"
    >
      <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full" />
      <span className="text-gray-700 font-medium">KORMARC 생성 중...</span>
    </div>
  )
}
