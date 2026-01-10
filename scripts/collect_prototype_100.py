#!/usr/bin/env python3
"""
100개 KORMARC 레코드 수집 프로토타입 스크립트

목표:
- 10개 KDC 분류에서 각 10개씩 총 100개 레코드 수집
- 국립중앙도서관 웹사이트 스크래핑 (Playwright headless mode)
- TOON 식별자 생성 및 SQLite 저장

실행 방법:
    python scripts/collect_prototype_100.py

출력:
- 데이터베이스: data/kormarc_prototype_100.db
- 콘솔 진행 상황 출력

예상 소요 시간:
- 약 5-10분 (Playwright headless mode로 백그라운드 수집)
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import yaml

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# ruff: noqa: E402
from kormarc.db import KORMARCDatabase
from kormarc.kormarc_builder import BookInfo, KORMARCBuilder
from kormarc.scraper import NationalLibraryScraper


async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("KORMARC 레코드 수집 프로토타입 (100개)")
    print("=" * 60)
    print()

    # 1. KDC 분류 로드
    kdc_file = project_root / "data" / "kdc_100_classifications.yaml"
    print(f"📚 KDC 분류 파일 로드: {kdc_file}")

    if not kdc_file.exists():
        print(f"❌ 파일이 존재하지 않습니다: {kdc_file}")
        return

    with open(kdc_file, encoding="utf-8") as f:
        kdc_data = yaml.safe_load(f)

    # 2. 10개 KDC 분류 선택
    # 각 주류(class_0 ~ class_9)에서 1개씩 선택
    all_kdcs = []

    for class_key in sorted(kdc_data["kdc_classifications"].keys()):
        classifications = kdc_data["kdc_classifications"][class_key]
        if classifications:
            # 각 주류에서 첫 번째 분류 선택
            all_kdcs.append(classifications[0])

    # 10개로 제한
    selected_kdcs = all_kdcs[:10]

    print(f"✓ 선택된 KDC 분류 ({len(selected_kdcs)}개):")
    for kdc in selected_kdcs:
        print(f"  - {kdc['code']}: {kdc['name']}")
    print()

    # 3. 컴포넌트 초기화
    print("🔧 컴포넌트 초기화 중...")

    # Scraper 초기화 (headless mode, 약간의 slow_mo로 안정성 확보)
    scraper = NationalLibraryScraper(headless=True, slow_mo=100)
    await scraper.initialize()

    # KORMARC 빌더 초기화
    builder = KORMARCBuilder()

    # 데이터베이스 초기화
    db_path = project_root / "data" / "kormarc_prototype_100.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    db = KORMARCDatabase(db_path)
    await db.initialize()

    print(f"✓ 데이터베이스: {db_path}")
    print()

    try:
        # 4. 레코드 수집
        print("📖 레코드 수집 시작...")
        print()

        total_collected = 0
        total_target = 100
        records_per_kdc = 10

        collection_results = {}

        for idx, kdc in enumerate(selected_kdcs, 1):
            code = kdc["code"]
            name = kdc["name"]
            keywords = kdc["keywords"]

            print(f"[{idx}/{len(selected_kdcs)}] {code} - {name}")
            print(f"  키워드: {', '.join(keywords[:3])}")

            collected_count = 0

            # 각 키워드로 시도
            for keyword in keywords:
                if collected_count >= records_per_kdc:
                    break

                try:
                    # 웹 스크래핑
                    results = await scraper.search_by_keyword(
                        keyword=keyword,
                        max_pages=1,
                        max_records=records_per_kdc - collected_count,
                    )

                    if not results:
                        print(f"    ⊘ '{keyword}': 결과 없음")
                        continue

                    # 결과 처리
                    for book_data in results:
                        if collected_count >= records_per_kdc:
                            break

                        try:
                            # BookInfo 생성
                            book_info = BookInfo(
                                isbn=book_data.get("isbn") or f"unknown_{total_collected}",
                                title=book_data.get("title") or "제목 없음",
                                author=book_data.get("author"),
                                publisher=book_data.get("publisher"),
                                pub_year=book_data.get("pub_year"),
                                pages=book_data.get("pages"),
                                kdc=code,
                                category="book",
                            )

                            # TOON 생성 및 레코드 빌드
                            record, toon_id = builder.build_with_toon(book_info)
                            toon_dict = builder.build_toon_dict(book_info)

                            # 데이터베이스 저장
                            await db.save_record(
                                toon_id=toon_id,
                                record_data=toon_dict,
                                data_source="national_library_scraper",
                            )

                            collected_count += 1
                            total_collected += 1

                            # 제목 출력 (최대 30자)
                            title_display = book_info.title[:30]
                            if len(book_info.title) > 30:
                                title_display += "..."

                            print(f"    ✓ {total_collected:3d}/{total_target}: {title_display}")

                        except Exception as e:
                            print(f"    ✗ 레코드 처리 실패: {e}")
                            continue

                    print(f"    → '{keyword}': {len(results)}건 수집")

                except Exception as e:
                    print(f"    ✗ '{keyword}' 검색 실패: {e}")
                    continue

            # KDC별 결과 저장
            collection_results[code] = collected_count

            print(f"  완료: {collected_count}/{records_per_kdc}건")
            print()

            # KDC 간 지연 (서버 부하 방지)
            if idx < len(selected_kdcs):  # 마지막 KDC가 아닌 경우
                await asyncio.sleep(2)

            # 목표 달성 시 중단
            if total_collected >= total_target:
                print(f"✓ 목표 달성: {total_collected}건 수집 완료")
                break

        # 5. 최종 리포트
        print()
        print("=" * 60)
        print("수집 완료 리포트")
        print("=" * 60)
        print()

        print(f"총 수집 레코드: {total_collected}건")
        print(f"목표 달성률: {total_collected / total_target * 100:.1f}%")
        print()

        print("KDC별 수집 현황:")
        for code, count in collection_results.items():
            kdc_info = next((k for k in selected_kdcs if k["code"] == code), None)
            name = kdc_info["name"] if kdc_info else "알 수 없음"
            print(f"  {code} ({name}): {count}건")

        print()
        print(f"데이터베이스: {db_path}")

        # 데이터베이스 통계
        total_in_db = await db.count_records()
        print(f"데이터베이스 총 레코드: {total_in_db}건")

    finally:
        # 6. 정리
        await scraper.close()
        await db.close()

        print()
        print("✓ 수집 완료")


if __name__ == "__main__":
    # 시작 시간 기록
    start_time = datetime.now()

    # 비동기 실행
    asyncio.run(main())

    # 종료 시간 출력
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print()
    print(f"실행 시간: {duration:.2f}초")
