#!/usr/bin/env python3
"""
KORMARC Database v1 → v2 마이그레이션 스크립트

기존 데이터베이스를 v2 스키마로 마이그레이션합니다.
- 정규화된 필드 추출 (title, author, publisher, pub_year, kdc_code)
- Leader 필드 추출
- FTS5 전문 검색 테이블 생성
- 카테고리 분할 테이블 제거
"""

import argparse
import asyncio
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kormarc.db import KORMARCDatabase


class DatabaseMigrator:
    """데이터베이스 마이그레이션 클래스"""

    def __init__(self, old_db_path: str, new_db_path: str):
        """
        마이그레이션 초기화

        Args:
            old_db_path: 기존 데이터베이스 경로
            new_db_path: 새 데이터베이스 경로
        """
        self.old_db_path = Path(old_db_path)
        self.new_db_path = Path(new_db_path)

        if not self.old_db_path.exists():
            raise FileNotFoundError(f"기존 데이터베이스를 찾을 수 없습니다: {old_db_path}")

    async def migrate(self, dry_run: bool = False) -> dict:
        """
        마이그레이션 실행

        Args:
            dry_run: True면 실제 저장 없이 검증만 수행

        Returns:
            마이그레이션 통계
        """
        print("=== KORMARC Database v1 → v2 마이그레이션 ===")
        print(f"기존 DB: {self.old_db_path}")
        print(f"새 DB: {self.new_db_path}")
        print(f"Dry run: {dry_run}")
        print()

        # 통계 초기화
        stats = {
            "total_records": 0,
            "migrated_records": 0,
            "failed_records": 0,
            "errors": [],
        }

        # 기존 DB에서 레코드 읽기
        old_conn = sqlite3.connect(self.old_db_path)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()

        # 전체 레코드 수 확인
        old_cursor.execute("SELECT COUNT(*) FROM kormarc_records")
        stats["total_records"] = old_cursor.fetchone()[0]
        print(f"총 레코드 수: {stats['total_records']}")

        # 새 DB 초기화 (dry_run이 아닌 경우)
        if not dry_run:
            new_db = KORMARCDatabase(self.new_db_path)
            await new_db.initialize()
        else:
            new_db = None

        # 레코드별 마이그레이션
        old_cursor.execute("SELECT * FROM kormarc_records")

        for row in old_cursor:
            try:
                # 기존 레코드 데이터 구성
                record_data = {
                    "timestamp": row["created_at"],
                    "type": row["record_type"],
                    "isbn": row["isbn"],
                    "raw_kormarc": row["raw_kormarc"],
                    "parsed": json.loads(row["parsed_data"]),
                }

                if dry_run:
                    # Dry run: 검증만 수행
                    self._validate_record(record_data)
                else:
                    # 실제 저장
                    await new_db.save_record(
                        toon_id=row["toon_id"],
                        record_data=record_data,
                        scraped_at=row["scraped_at"],
                        data_source=row["data_source"],
                    )

                stats["migrated_records"] += 1

                # 진행 상황 출력
                if stats["migrated_records"] % 100 == 0:
                    print(
                        f"진행: {stats['migrated_records']}/{stats['total_records']} 레코드 마이그레이션 완료"
                    )

            except Exception as e:
                stats["failed_records"] += 1
                error_msg = f"TOON ID {row['toon_id']}: {str(e)}"
                stats["errors"].append(error_msg)
                print(f"⚠️  오류: {error_msg}")

        # 정리
        old_conn.close()
        if new_db:
            await new_db.close()

        # 마이그레이션 결과 출력
        print()
        print("=== 마이그레이션 완료 ===")
        print(f"총 레코드: {stats['total_records']}")
        print(f"성공: {stats['migrated_records']}")
        print(f"실패: {stats['failed_records']}")

        if stats["errors"]:
            print()
            print("오류 목록:")
            for error in stats["errors"][:10]:  # 최대 10개만 출력
                print(f"  - {error}")
            if len(stats["errors"]) > 10:
                print(f"  ... 외 {len(stats['errors']) - 10}개")

        return stats

    def _validate_record(self, record_data: dict) -> None:
        """
        레코드 검증

        Args:
            record_data: 레코드 데이터

        Raises:
            ValueError: 필수 필드 누락 시
        """
        required_fields = ["timestamp", "type", "isbn", "raw_kormarc", "parsed"]
        for field in required_fields:
            if field not in record_data:
                raise ValueError(f"필수 필드 누락: {field}")

        # parsed 구조 검증
        parsed = record_data["parsed"]
        if "leader" not in parsed:
            raise ValueError("parsed.leader 필드 누락")
        if "data_fields" not in parsed:
            raise ValueError("parsed.data_fields 필드 누락")

    async def validate_migration(self) -> bool:
        """
        마이그레이션 검증

        새 데이터베이스가 올바르게 생성되었는지 확인

        Returns:
            검증 성공 여부
        """
        print()
        print("=== 마이그레이션 검증 ===")

        if not self.new_db_path.exists():
            print("❌ 새 데이터베이스 파일이 없습니다.")
            return False

        # 새 DB 연결
        new_db = KORMARCDatabase(self.new_db_path)
        await new_db.initialize()

        try:
            # 레코드 수 확인
            old_conn = sqlite3.connect(self.old_db_path)
            old_cursor = old_conn.cursor()
            old_cursor.execute("SELECT COUNT(*) FROM kormarc_records")
            old_count = old_cursor.fetchone()[0]
            old_conn.close()

            new_count = await new_db.count_records()

            print(f"기존 DB 레코드 수: {old_count}")
            print(f"새 DB 레코드 수: {new_count}")

            if old_count != new_count:
                print("❌ 레코드 수가 일치하지 않습니다.")
                return False

            # 스키마 검증
            conn = sqlite3.connect(self.new_db_path)
            cursor = conn.cursor()

            # 테이블 존재 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            required_tables = {"kormarc_records", "kormarc_fts"}
            if not required_tables.issubset(tables):
                print(f"❌ 필수 테이블 누락: {required_tables - tables}")
                return False

            # 컬럼 확인
            cursor.execute("PRAGMA table_info(kormarc_records)")
            columns = {row[1] for row in cursor.fetchall()}

            required_columns = {
                "toon_id",
                "timestamp_ms",
                "created_at",
                "record_type",
                "isbn",
                "title",
                "author",
                "publisher",
                "pub_year",
                "kdc_code",
                "record_length",
                "record_status",
                "raw_kormarc",
                "parsed_data",
                "scraped_at",
                "data_source",
            }

            if not required_columns.issubset(columns):
                print(f"❌ 필수 컬럼 누락: {required_columns - columns}")
                return False

            # 인덱스 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = {row[0] for row in cursor.fetchall()}

            required_indexes = {
                "idx_timestamp",
                "idx_type",
                "idx_isbn",
                "idx_kdc_year",
                "idx_publisher_year",
                "idx_type_year",
                "idx_title",
                "idx_author",
            }

            if not required_indexes.issubset(indexes):
                print(f"⚠️  일부 인덱스 누락: {required_indexes - indexes}")

            conn.close()

            print("✅ 마이그레이션 검증 성공")
            return True

        finally:
            await new_db.close()


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="KORMARC Database v1 → v2 마이그레이션")
    parser.add_argument("old_db", help="기존 데이터베이스 경로")
    parser.add_argument("new_db", help="새 데이터베이스 경로")
    parser.add_argument("--dry-run", action="store_true", help="실제 저장 없이 검증만 수행")
    parser.add_argument("--validate", action="store_true", help="마이그레이션 후 검증 수행")

    args = parser.parse_args()

    # 마이그레이션 실행
    migrator = DatabaseMigrator(args.old_db, args.new_db)

    try:
        start_time = datetime.now()

        stats = await migrator.migrate(dry_run=args.dry_run)

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n소요 시간: {elapsed:.2f}초")

        # 검증
        if args.validate and not args.dry_run:
            is_valid = await migrator.validate_migration()
            if not is_valid:
                sys.exit(1)

        # 실패한 레코드가 있으면 에러 코드 반환
        if stats["failed_records"] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 마이그레이션 실패: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
