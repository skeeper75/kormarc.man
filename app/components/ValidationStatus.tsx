'use client'

/**
 * 검증 티어 정의
 * KORMARC 검증의 5가지 단계를 나타냅니다
 */
export interface ValidationTier {
  /** 티어 레벨 (1-5) */
  level: 1 | 2 | 3 | 4 | 5
  /** 검증 상태 */
  status: 'pending' | 'passed' | 'failed'
}

/**
 * ValidationStatus 컴포넌트
 * KORMARC 검증의 5가지 티어 상태를 시각적으로 표시합니다
 *
 * @param tiers 5개의 검증 티어 배열
 * @example
 * const tiers = [
 *   { level: 1, status: 'passed' },
 *   { level: 2, status: 'passed' },
 *   { level: 3, status: 'pending' },
 *   { level: 4, status: 'failed' },
 *   { level: 5, status: 'pending' },
 * ]
 * <ValidationStatus tiers={tiers} />
 */
export function ValidationStatus({ tiers }: { tiers: ValidationTier[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'bg-green-500'
      case 'failed':
        return 'bg-red-500'
      case 'pending':
      default:
        return 'bg-gray-300'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'passed':
        return '통과'
      case 'failed':
        return '실패'
      case 'pending':
      default:
        return '대기 중'
    }
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">검증 상태</h3>
      {tiers.map((tier) => (
        <div key={tier.level} className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${getStatusColor(tier.status)}`}
          >
            Tier {tier.level}
          </div>
          <div className="flex-1">
            <p className="font-medium">레벨 {tier.level}</p>
            <p className="text-sm text-gray-600">
              상태: {getStatusText(tier.status)}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
