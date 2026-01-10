#!/usr/bin/env python
"""
대규모 KORMARC 도서 데이터 수집 스크립트

Playwright로 국립도서관 웹사이트를 스크래핑하여
5000권 이상의 도서 데이터를 수집하고 SQLite 데이터베이스에 저장합니다.

Usage:
    python scripts/collect_books.py --target 5000 --db-path data/kormarc_5000.db

Options:
    --target: 수집 목표 권수 (기본값: 5000)
    --db-path: 데이터베이스 경로 (기본값: data/kormarc_books.db)
    --kdc: 특정 KDC만 수집 (없으면 전체 분류)
    --delay: 요청 간 지연 시간 (기본값: 2.0초)
    --headless: 헤드리스 모드 (기본값: True, False면 브라우저 표시)
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# src 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kormarc.scraper import BookCollectorPlaywright

# KDC 분류별 검색어
KDC_KEYWORDS = {
    "0": ["백과사전", "사전", "연감", "일반"],
    "1": ["철학", "심리학", "윤리", "논리"],
    "2": ["종교", "불교", "기독교", "이슬람"],
    "3": ["경제", "경영", "교육", "정치", "사회", "법"],
    "4": ["수학", "물리", "화학", "생물", "지구", "천문"],
    "5": ["컴퓨터", "프로그래밍", "소프트웨어", "인공지능", "데이터"],
    "6": ["미술", "음악", "건축", "사진", "디자인"],
    "7": ["한국어", "영어", "문법", "어학"],
    "8": ["소설", "시", "에세이", "만화", "문학"],
    "9": ["역사", "한국사", "세계사", "전기", "지리"],
}


async def collect_by_keywords(
    collector: BookCollectorPlaywright,
    target_count: int,
    kdc_filter: str | None = None,
) -> int:
    """
    키워드별 도서 수집

    Args:
        collector: BookCollectorPlaywright 인스턴스
        target_count: 목표 수집 권수
        kdc_filter: 특정 KDC만 수집 (선택)

    Returns:
        실제 수집된 권수
    """
    collected = 0
    start_time = datetime.now()

    print(f"\n{'=' * 60}")
    print(f"도서 수집 시작 (Playwright): 목표 {target_count}권")
    print(f"시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}\n")

    # 전체 분야 수집 또는 특정 KDC만 수집
    kdc_codes = [kdc_filter] if kdc_filter else list(KDC_KEYWORDS.keys())

    for kdc in kdc_codes:
        if collected >= target_count:
            break

        keywords = KDC_KEYWORDS.get(kdc, [])

        for keyword in keywords:
            if collected >= target_count:
                break

            # 남은 목표량
            remaining = target_count - collected
            batch_size = min(50, remaining)  # 배치당 50권 (웹 스크래핑은 더 느림)

            print(f"\n[KDC {kdc}] 키워드 '{keyword}' 검색 ({batch_size}권 목표)")

            try:
                records = await collector.collect_by_keyword(
                    keyword=keyword,
                    max_records=batch_size,
                )

                collected += len(records)

                elapsed = (datetime.now() - start_time).total_seconds()
                rate = collected / elapsed if elapsed > 0 else 0

                print(f"  → {len(records)}권 수집 완료 (누계: {collected}권, {rate:.1f}권/초)")

            except Exception as e:
                print(f"  ⚠ 오류 발생: {e}")
                continue

    # 경과 시간
    elapsed = datetime.now() - start_time
    elapsed_sec = elapsed.total_seconds()

    print(f"\n{'=' * 60}")
    print("수집 완료")
    print(f"총 수집량: {collected}권")
    print(f"소요 시간: {elapsed_sec:.1f}초 ({elapsed_sec / 60:.1f}분)")
    print(f"평균 속도: {collected / elapsed_sec:.1f}권/초")
    print(f"{'=' * 60}\n")

    return collected


async def collect_by_kdc_range(
    collector: BookCollectorPlaywright,
    target_count: int,
    kdc_prefix: str = "0",
) -> int:
    """
    KDC 범위별 도서 수집

    Args:
        collector: BookCollectorPlaywright 인스턴스
        target_count: 목표 수집 권수
        kdc_prefix: KDC 접두사 (0-9)

    Returns:
        실제 수집된 권수
    """
    collected = 0
    start_time = datetime.now()

    print(f"\n[KDC {kdc_prefix}00] 분야 도서 수집 시작: 목표 {target_count}권")

    # 세부 KDC 코드 (예: 000~099)
    for i in range(10):  # KDC 범위 축소 (0-9만 검색)
        if collected >= target_count:
            break

        kdc = f"{kdc_prefix}{i}"
        remaining = target_count - collected
        batch_size = min(20, remaining)  # 배치당 20권

        try:
            records = await collector.collect_by_kdc(kdc=kdc, max_records=batch_size)
            collected += len(records)

            print(f"[KDC {kdc}] {len(records)}권 수집 (누계: {collected}권)")

            # 웹 스크래핑은 더 긴 지연 필요
            await asyncio.sleep(collector.delay)

        except Exception as e:
            print(f"[KDC {kdc}] 오류: {e}")
            continue

    elapsed_sec = (datetime.now() - start_time).total_seconds()
    print(f"\n[KDC {kdc_prefix}00] 수집 완료: {collected}권 ({elapsed_sec:.1f}초)")

    return collected


async def save_to_db(
    collector: BookCollectorPlaywright,
    db_path: str,
) -> int:
    """
    수집된 레코드를 데이터베이스에 저장

    Args:
        collector: BookCollectorPlaywright 인스턴스
        db_path: 데이터베이스 경로

    Returns:
        저장된 레코드 수
    """
    print(f"\n{'=' * 60}")
    print(f"데이터베이스 저장 시작: {db_path}")
    print(f"{'=' * 60}\n")

    saved = await collector.save_to_database(
        db_path=db_path,
        data_source="national_library_web",
    )

    print(f"\n{'=' * 60}")
    print(f"저장 완료: {saved}건 → {db_path}")
    print(f"{'=' * 60}\n")

    return saved


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Playwright 기반 대규모 KORMARC 도서 데이터 수집",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # 5000권 수집 (전체 분야, 헤드리스 모드)
    python scripts/collect_books.py --target 5000

    # 100권 수집 (브라우저 표시로 테스트)
    python scripts/collect_books.py --target 100 --no-headless

    # 특정 KDC만 수집 (기술과학)
    python scripts/collect_books.py --target 100 --kdc 5

    # 데이터베이스 경로 지정
    python scripts/collect_books.py --target 1000 --db-path data/my_books.db

    # 요청 간 지연 시간 조정 (웹 스크래핑은 더 긴 지연 권장)
    python scripts/collect_books.py --target 500 --delay 3.0
        """,
    )

    parser.add_argument(
        "--target",
        type=int,
        default=5000,
        help="수집 목표 권수 (기본값: 5000)",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="data/kormarc_books.db",
        help="데이터베이스 경로 (기본값: data/kormarc_books.db)",
    )

    parser.add_argument(
        "--kdc",
        type=str,
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        help="특정 KDC만 수집 (0-9, 없으면 전체)",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="요청 간 지연 시간 in seconds (기본값: 2.0, 웹 스크래핑은 긴 지연 권장)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="헤드리스 모드 (기본값: True, --no-headless로 브라우저 표시)",
    )

    args = parser.parse_args()

    # headless 처리
    headless = not args.no_headless if hasattr(args, "no_headless") else args.headless

    # 데이터베이스 디렉토리 생성
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 수집기 초기화
    collector = BookCollectorPlaywright(
        headless=headless,
        delay=args.delay,
    )

    try:
        await collector.initialize()

        # 데이터 수집
        if args.kdc:
            # 특정 KDC만 수집
            collected = await collect_by_kdc_range(
                collector,
                target_count=args.target,
                kdc_prefix=args.kdc,
            )
        else:
            # 전체 분야 수집
            collected = await collect_by_keywords(
                collector,
                target_count=args.target,
                kdc_filter=None,
            )

        if collected == 0:
            print("⚠ 수집된 데이터가 없습니다.")
            return

        # 데이터베이스 저장
        saved = await save_to_db(collector, str(db_path))

        print("\n✅ 작업 완료!")
        print(f"   수집: {collected}권")
        print(f"   저장: {saved}건")
        print(f"   DB: {db_path}")

    except KeyboardInterrupt:
        print("\n\n⚠ 사용자 중단: 부분 저장 데이터를 확인하세요.")
        return

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return

    finally:
        await collector.close()


if __name__ == "__main__":
    asyncio.run(main())
