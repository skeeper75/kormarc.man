#!/usr/bin/env python3
"""
간단한 스크래퍼 테스트 - HTML 구조 확인
"""

import asyncio

from kormarc.scraper import NationalLibraryScraper


async def test_html_structure():
    """HTML 구조 확인"""
    print("=" * 80)
    print("HTML 구조 확인 테스트")
    print("=" * 80)

    async with NationalLibraryScraper(headless=False, slow_mo=1000) as scraper:
        # 메인 페이지 접속
        print("\n1. 메인 페이지 접속")
        await scraper._page.goto("https://www.nl.go.kr/seoji/", timeout=60000)
        await asyncio.sleep(3)

        # 검색 폼 찾기
        print("\n2. 검색 폼 찾기")
        search_input = await scraper._page.query_selector('input[name="schStr"]')
        if search_input:
            print("   ✓ 검색 입력란 발견: input[name='schStr']")

            # 검색어 입력
            await search_input.fill("파이썬")
            await asyncio.sleep(1)

            # 검색 버튼 찾기 (여러 선택자 시도)
            button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                "button.btn_search",
                "a.btn_search",
                'button:has-text("검색")',
                ".search_btn",
                "#searchBtn",
            ]

            search_button = None
            for selector in button_selectors:
                search_button = await scraper._page.query_selector(selector)
                if search_button:
                    print(f"   ✓ 검색 버튼 발견: {selector}")
                    break

            if search_button:
                print("\n3. 검색 실행")
                await search_button.click()
                await asyncio.sleep(5)

                # 현재 URL 확인
                current_url = scraper._page.url
                print(f"   현재 URL: {current_url}")

                # 페이지 타이틀 확인
                title = await scraper._page.title()
                print(f"   페이지 제목: {title}")

                # HTML 일부 저장
                html = await scraper._page.content()
                with open("search_result_page.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("   HTML 저장: search_result_page.html")

                # 스크린샷 저장
                await scraper._page.screenshot(path="search_result_page.png")
                print("   스크린샷 저장: search_result_page.png")

            else:
                print("   ✗ 검색 버튼을 찾을 수 없습니다")
                # Enter 키로 검색 시도
                print("\n3. Enter 키로 검색 시도")
                await search_input.press("Enter")
                await asyncio.sleep(5)

                # 현재 URL 확인
                current_url = scraper._page.url
                print(f"   현재 URL: {current_url}")

                # HTML 저장
                html = await scraper._page.content()
                with open("search_result_page.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("   HTML 저장: search_result_page.html")

                # 스크린샷 저장
                await scraper._page.screenshot(path="search_result_page.png")
                print("   스크린샷 저장: search_result_page.png")

        else:
            print("   ✗ 검색 입력란을 찾을 수 없습니다")

        # 사용자가 브라우저 확인할 시간
        print("\n브라우저를 확인하세요. 10초 후 종료...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(test_html_structure())
