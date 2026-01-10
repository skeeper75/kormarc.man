"""
Batch Validator - 배치 검증 시스템

여러 레코드를 일괄 검증하는 기능 제공
"""

import json
from pathlib import Path
from typing import Any

import aiosqlite

from kormarc.models.record import Record
from kormarc.validators.nowon_validator import NowonValidator
from kormarc.validators.semantic_validator import SemanticValidator
from kormarc.validators.structure_validator import (
    StructureValidator,
    ValidationResult,
)


class BatchValidator:
    """
    배치 검증기

    SQLite 데이터베이스에서 레코드를 읽어 일괄 검증합니다.
    """

    def __init__(self, db_path: str | Path) -> None:
        """
        배치 검증기 초기화

        Args:
            db_path: SQLite 데이터베이스 경로
        """
        self.db_path = Path(db_path)
        self.structure_validator = StructureValidator()
        self.semantic_validator = SemanticValidator()
        self.nowon_validator = NowonValidator()

    async def validate_all(
        self, limit: int | None = None, tiers: list[int] | None = None
    ) -> dict[str, list[ValidationResult]]:
        """
        모든 레코드 검증

        Args:
            limit: 검증할 최대 레코드 수 (None이면 전체)
            tiers: 검증할 Tier 목록 (None이면 전체)

        Returns:
            dict[toon_id, list[ValidationResult]]: TOON ID별 검증 결과
        """
        if tiers is None:
            tiers = [1, 2, 3]  # Tier 1 (Structure), Tier 2 (Semantic), Tier 3 (Nowon)

        results: dict[str, list[ValidationResult]] = {}

        async with aiosqlite.connect(self.db_path) as conn:
            # 레코드 조회
            query = "SELECT toon_id, parsed_data FROM kormarc_records"
            if limit:
                query += f" LIMIT {limit}"

            async with conn.execute(query) as cursor:
                async for row in cursor:
                    toon_id, parsed_data = row

                    try:
                        # JSON에서 Record 객체 복원
                        record_dict = json.loads(parsed_data)

                        # 데이터베이스 스키마가 다른 경우 변환
                        # indicators -> indicator1, indicator2로 분리
                        if "data_fields" in record_dict:
                            for df in record_dict["data_fields"]:
                                if "indicators" in df and "indicator1" not in df:
                                    indicators = df.pop("indicators")
                                    df["indicator1"] = indicators[0] if len(indicators) > 0 else " "
                                    df["indicator2"] = indicators[1] if len(indicators) > 1 else " "

                        record = Record.model_validate(record_dict)

                        # 검증 실행
                        validation_results: list[ValidationResult] = []

                        if 1 in tiers:
                            # Tier 1: Structure Validation
                            result = self.structure_validator.validate_record(record)
                            validation_results.append(result)

                        if 2 in tiers:
                            # Tier 2: Semantic Validation
                            result = self.semantic_validator.validate_record(record)
                            validation_results.append(result)

                        if 3 in tiers:
                            # Tier 3: Nowon Validation
                            result = self.nowon_validator.validate_record(record)
                            validation_results.append(result)

                        results[toon_id] = validation_results

                    except Exception:
                        # 복원 실패한 레코드는 스킵 (조용히)
                        continue

        return results

    def generate_report(self, results: dict[str, list[ValidationResult]]) -> dict[str, Any]:
        """
        검증 결과 보고서 생성

        Args:
            results: 검증 결과

        Returns:
            dict: 검증 보고서
        """
        total_records = len(results)
        passed_records = 0
        failed_records = 0
        errors_by_tier: dict[int, int] = {1: 0, 2: 0, 3: 0}
        warnings_by_tier: dict[int, int] = {1: 0, 2: 0, 3: 0}

        for toon_id, validation_results in results.items():
            record_passed = True

            for result in validation_results:
                if not result.passed:
                    record_passed = False
                    errors_by_tier[result.tier] += len(result.errors)

                warnings_by_tier[result.tier] += len(result.warnings)

            if record_passed:
                passed_records += 1
            else:
                failed_records += 1

        return {
            "total_records": total_records,
            "passed_records": passed_records,
            "failed_records": failed_records,
            "pass_rate": (
                round(passed_records / total_records * 100, 2) if total_records > 0 else 0
            ),
            "errors_by_tier": errors_by_tier,
            "warnings_by_tier": warnings_by_tier,
        }

    def print_report(self, report: dict[str, Any]) -> None:
        """
        검증 보고서 출력

        Args:
            report: 검증 보고서
        """
        print("\n" + "=" * 60)
        print("KORMARC 배치 검증 보고서")
        print("=" * 60)
        print(f"총 레코드 수: {report['total_records']}")
        print(f"통과: {report['passed_records']}")
        print(f"실패: {report['failed_records']}")
        print(f"통과율: {report['pass_rate']}%")
        print("\nTier별 오류:")
        for tier, count in report["errors_by_tier"].items():
            print(f"  Tier {tier}: {count}개")
        print("\nTier별 경고:")
        for tier, count in report["warnings_by_tier"].items():
            print(f"  Tier {tier}: {count}개")
        print("=" * 60 + "\n")
