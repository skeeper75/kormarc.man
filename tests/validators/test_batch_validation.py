"""
Batch Validation 테스트

100개 레코드 배치 검증 기능 테스트
"""

from pathlib import Path

import pytest
from kormarc.validators.batch_validator import BatchValidator


class TestBatchValidation:
    """배치 검증 테스트"""

    @pytest.mark.asyncio
    async def test_validate_batch_100_records(self) -> None:
        """100개 레코드 배치 검증 - 정상 케이스"""
        # Arrange: 100개 레코드 데이터베이스
        db_path = Path("data/kormarc_prototype_100.db")

        if not db_path.exists():
            pytest.skip(f"Database not found: {db_path}")

        # Act: 배치 검증 실행
        validator = BatchValidator(str(db_path))
        results = await validator.validate_all(limit=100)

        # Assert: 검증 결과 확인
        assert len(results) > 0
        assert len(results) <= 100

        # 각 결과는 ValidationResult 객체 리스트
        for toon_id, validation_results in results.items():
            assert isinstance(toon_id, str)
            assert isinstance(validation_results, list)

    @pytest.mark.asyncio
    async def test_generate_validation_report(self) -> None:
        """검증 보고서 생성 테스트"""
        # Arrange: 100개 레코드 데이터베이스
        db_path = Path("data/kormarc_prototype_100.db")

        if not db_path.exists():
            pytest.skip(f"Database not found: {db_path}")

        # Act: 배치 검증 및 보고서 생성
        validator = BatchValidator(str(db_path))
        results = await validator.validate_all(limit=10)  # 10개만 테스트
        report = validator.generate_report(results)

        # Assert: 보고서 구조 확인
        assert "total_records" in report
        assert "passed_records" in report
        assert "failed_records" in report
        assert "errors_by_tier" in report
        assert report["total_records"] == len(results)

    @pytest.mark.asyncio
    async def test_tier_filtering(self) -> None:
        """Tier별 필터링 테스트"""
        # Arrange: 100개 레코드 데이터베이스
        db_path = Path("data/kormarc_prototype_100.db")

        if not db_path.exists():
            pytest.skip(f"Database not found: {db_path}")

        # Act: Tier 1만 검증
        validator = BatchValidator(str(db_path))
        results = await validator.validate_all(limit=5, tiers=[1])

        # Assert: Tier 1 검증만 수행됨
        for toon_id, validation_results in results.items():
            for result in validation_results:
                assert result.tier == 1
