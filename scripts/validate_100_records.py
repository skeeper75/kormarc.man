#!/usr/bin/env python3
"""
100개 레코드 검증 스크립트

KORMARC 레코드 100개를 검증하고 결과를 출력합니다.
"""

import asyncio
from pathlib import Path

from kormarc.validators.batch_validator import BatchValidator


async def main() -> None:
    """메인 실행 함수"""
    # 데이터베이스 경로
    db_path = Path(__file__).parent.parent / "data" / "kormarc_prototype_100.db"

    if not db_path.exists():
        print(f"❌ 데이터베이스를 찾을 수 없습니다: {db_path}")
        return

    print(f"📂 데이터베이스: {db_path}")
    print("🔍 검증 시작...\n")

    # 배치 검증 실행
    validator = BatchValidator(db_path)
    results = await validator.validate_all(limit=100)

    # 보고서 생성 및 출력
    report = validator.generate_report(results)
    validator.print_report(report)

    # 상세 오류 출력 (처음 5개만)
    print("상세 오류 (처음 5개):")
    print("-" * 60)

    error_count = 0
    for toon_id, validation_results in results.items():
        if error_count >= 5:
            break

        for result in validation_results:
            if not result.passed:
                print(f"\n📌 TOON ID: {toon_id}")
                print(f"   Tier: {result.tier} ({result.validator_name})")

                for error in result.errors:
                    print(f"   ❌ [{error.field_tag or 'N/A'}] {error.message}")
                    if error.suggestion:
                        print(f"      💡 {error.suggestion}")

                for warning in result.warnings:
                    print(f"   ⚠️  [{warning.field_tag or 'N/A'}] {warning.message}")

                error_count += 1

    print("\n✅ 검증 완료!")


if __name__ == "__main__":
    asyncio.run(main())
