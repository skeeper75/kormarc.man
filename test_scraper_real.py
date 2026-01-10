#!/usr/bin/env python3
"""
국립중앙도서관 스크래퍼 실제 테스트

실제 웹사이트(https://www.nl.go.kr/seoji/)에 접속하여 스크래퍼를 테스트합니다.
"""

import asyncio

from kormarc.scraper import NationalLibraryScraper


async def test_search():
    """검색 기능 테스트"""
    print("=" * 80)
    print("국립중앙도서관 스크래퍼 실제 테스트")
    print("=" * 80)

    # 스크래퍼 초기화 (브라우저 표시)
    async with NationalLibraryScraper(headless=False, slow_mo=500) as scraper:
        print("\n[테스트 1] 키워드 검색: '파이썬'")
        print("-" * 80)

        try:
            results = await scraper.search_by_keyword("파이썬", max_pages=1, max_records=5)

            print(f"\n검색 결과: {len(results)}건\n")

            for i, record in enumerate(results, 1):
                print(f"[{i}] {record.get('title', '제목 없음')}")
                print(f"    저자: {record.get('author', 'N/A')}")
                print(f"    출판사: {record.get('publisher', 'N/A')}")
                print(f"    발행년: {record.get('pub_year', 'N/A')}")
                print(f"    ISBN: {record.get('isbn', 'N/A')}")
                print(f"    제어번호: {record.get('control_number', 'N/A')}")
                print(f"    URL: {record.get('detail_url', 'N/A')}")
                if record.get("raw_text"):
                    print(f"    원본 텍스트: {record['raw_text'][:100]}...")
                print()

            if len(results) > 0:
                print("✅ 검색 성공!")
            else:
                print("❌ 검색 결과 없음 - 선택자 확인 필요")

        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
            import traceback

            traceback.print_exc()

        # 사용자가 브라우저 확인할 시간 제공
        print("\n브라우저를 확인하세요. 10초 후 종료됩니다...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    # asyncio 실행
    asyncio.run(test_search())
