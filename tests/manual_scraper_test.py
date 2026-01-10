"""
실제 국립중앙도서관 웹사이트 스크래핑 테스트

이 스크립트는 NationalLibraryScraper가 실제로 작동하는지 검증합니다.
"""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from kormarc.scraper import NationalLibraryScraper


async def test_real_scraping():
    """실제 스크래핑 테스트"""
    print("=" * 60)
    print("국립중앙도서관 스크래퍼 실제 테스트")
    print("=" * 60)

    try:
        async with NationalLibraryScraper(headless=True) as scraper:
            # 테스트 1: 키워드 검색
            print("\n[테스트 1] 키워드 검색: '파이썬'")
            print("-" * 60)

            try:
                results = await scraper.search_by_keyword("파이썬", max_pages=1, max_records=5)

                print(f"✓ 검색 결과: {len(results)}개")

                if results:
                    print("\n첫 번째 결과:")
                    first = results[0]
                    print(f"  제목: {first.get('title', 'N/A')}")
                    print(f"  저자: {first.get('author', 'N/A')}")
                    print(f"  발행처: {first.get('publisher', 'N/A')}")
                    print(f"  발행년: {first.get('pub_year', 'N/A')}")
                    print(f"  ISBN: {first.get('isbn', 'N/A')}")

                    if len(results) > 1:
                        print(f"\n추가 결과: {len(results) - 1}개")
                else:
                    print("⚠️  검색 결과가 없습니다.")
            except Exception as e:
                print(f"❌ 키워드 검색 실패: {e}")
                import traceback

                traceback.print_exc()

            # 테스트 2: ISBN 검색
            print("\n[테스트 2] ISBN 검색: '9788960777330'")
            print("-" * 60)

            try:
                book = await scraper.search_by_isbn("9788960777330")

                if book:
                    print("✓ ISBN 검색 성공")
                    print(f"  제목: {book.get('title', 'N/A')}")
                    print(f"  저자: {book.get('author', 'N/A')}")
                    print(f"  ISBN: {book.get('isbn', 'N/A')}")
                    print(f"  발행처: {book.get('publisher', 'N/A')}")
                else:
                    print("⚠️  ISBN 검색 결과가 없습니다.")
            except Exception as e:
                print(f"❌ ISBN 검색 실패: {e}")
                import traceback

                traceback.print_exc()

        print("\n" + "=" * 60)
        print("테스트 완료")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 스크래퍼 초기화 실패: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_real_scraping())
