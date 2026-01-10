"""
국립중앙도서관 웹사이트 스크래퍼

Playwright를 사용하여 국립중앙도서관 웹사이트에서 도서 정보를 스크래핑합니다.

Target: https://www.nl.go.kr/seoji/ (국립중앙도서관 서지정보유통지원시스템)
"""

import asyncio
import re
from typing import Any
from urllib.parse import quote

from playwright.async_api import async_playwright


class NationalLibraryScraper:
    """
    국립중앙도서관 웹사이트 스크래퍼

    Playwright를 사용하여 웹사이트에서 도서 정보를 스크래핑합니다.

    Example:
        >>> scraper = NationalLibraryScraper()
        >>> await scraper.initialize()
        >>> results = await scraper.search_by_keyword("파이썬", max_pages=1)
        >>> await scraper.close()
    """

    # 국립중앙도서관 서지정보 URL (실제 웹사이트 구조 반영)
    BASE_URL = "https://www.nl.go.kr/seoji"
    SEARCH_URL = f"{BASE_URL}/contents/S80100000000.do"  # 통합검색 페이지
    DETAIL_URL = f"{BASE_URL}/contents/S80101000000.do"  # 상세정보 페이지

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        """
        스크래퍼 초기화

        Args:
            headless: 헤드리스 모드 (True=백그라운드, False=브라우저 표시)
            slow_mo: 작업 간 지연 (ms)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser = None
        self._page = None

    async def initialize(self) -> None:
        """스크래퍼 초기화"""
        self._playwright = await async_playwright().start()

        # 브라우저 옵션 추가 (자동화 감지 회피)
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )

        # Context 생성 (User-Agent 및 viewport 설정)
        context = await self._browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ko-KR",
        )

        self._page = await context.new_page()

        # JavaScript로 webdriver 속성 제거
        await self._page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def close(self) -> None:
        """스크래퍼 종료"""
        if self._page:
            await self._page.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def __aenter__(self):
        """Async context manager 진입"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager 퇴출"""
        await self.close()

    async def search_by_keyword(
        self,
        keyword: str,
        max_pages: int = 1,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """
        키워드로 도서 검색

        Args:
            keyword: 검색어
            max_pages: 최대 스크래핑 페이지 수
            max_records: 최대 수집 레코드 수

        Returns:
            검색 결과 리스트
        """
        results = []

        try:
            # 먼저 메인 페이지 접속 (세션 확립)
            print(f"메인 페이지 접속: {self.BASE_URL}")
            await self._page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)

            # 검색 폼에서 직접 검색 (Enter 키 사용)
            print(f"검색어 입력: {keyword}")
            search_input = await self._page.query_selector('input[name="schStr"]')
            if not search_input:
                print("검색 입력란을 찾을 수 없습니다.")
                return results

            await search_input.fill(keyword)
            await asyncio.sleep(1)

            # Enter 키로 검색 실행
            print("검색 실행 (Enter)")
            await search_input.press("Enter")
            await asyncio.sleep(5)

            # 페이지 정보 출력
            current_url = self._page.url
            print(f"현재 URL: {current_url}")

            for page_num in range(1, max_pages + 1):
                print(f"페이지 {page_num} 스크래핑 중...")

                # 현재 페이지에서 레코드 추출
                page_results = await self._extract_search_results()

                if not page_results:
                    print(f"페이지 {page_num}에서 결과를 찾을 수 없습니다.")
                    break

                results.extend(page_results)
                print(f"현재까지 {len(results)}건 수집")

                # 목표 도달 시 중단
                if len(results) >= max_records:
                    break

                # 다음 페이지 클릭
                if page_num < max_pages:
                    has_next = await self._click_next_page()
                    if not has_next:
                        print("다음 페이지가 없습니다.")
                        break

                    # 페이지 로딩 대기
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
            import traceback

            traceback.print_exc()

        return results[:max_records]

    async def search_by_isbn(self, isbn: str) -> dict[str, Any] | None:
        """
        ISBN으로 도서 검색

        Args:
            isbn: ISBN (10 또는 13자리)

        Returns:
            도서 정보 또는 None
        """
        try:
            # ISBN 검색 (통합검색 사용)
            search_url = f"{self.SEARCH_URL}?schType=simple&schStr={quote(isbn)}"
            print(f"ISBN 검색 URL: {search_url}")

            await self._page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # 첫 번째 결과 클릭
            first_result = await self._page.query_selector("a.title, .result_item a, .bookList a")
            if first_result:
                await first_result.click()
                await self._page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)

                # 상세 정보 추출
                return await self._extract_detail_page()

        except Exception as e:
            print(f"ISBN 검색 실패 ({isbn}): {e}")
            import traceback

            traceback.print_exc()

        return None

    async def _extract_search_results(self) -> list[dict[str, Any]]:
        """
        검색 결과 페이지에서 레코드 추출 (실제 서지정보 웹사이트 구조 반영)

        Returns:
            레코드 리스트
        """
        records = []

        try:
            # 검색 결과 컨테이너 확인 (실제 HTML 구조 기반)
            result_container = await self._page.query_selector(
                "#resultList_div, .resultList, #content_body"
            )

            if not result_container:
                print("검색 결과 컨테이너를 찾을 수 없습니다.")
                # 디버깅: 페이지 스크린샷 저장
                await self._page.screenshot(path="debug_search_page.png")
                return records

            # 검색 결과 항목 선택 (실제 구조: .resultData)
            result_items = await self._page.query_selector_all(".resultData")

            if not result_items:
                print("검색 결과 항목을 찾을 수 없습니다. 전체 텍스트 파싱 시도...")
                # 대체 방법: 전체 텍스트에서 정보 추출
                text_content = await self._page.inner_text("#content_body, body")
                records = self._parse_text_results(text_content)
                return records

            print(f"검색 결과 항목 {len(result_items)}개 발견")

            for idx, item in enumerate(result_items[:100]):  # 페이지당 최대 100개
                try:
                    # 항목 전체 텍스트 추출
                    item_text = await item.inner_text()

                    # 제목 추출 (실제 구조: .tit a)
                    title_elem = await item.query_selector(".tit a")
                    title = ""
                    href = ""
                    onclick_value = ""

                    if title_elem:
                        title = await title_elem.inner_text()
                        href = await title_elem.get_attribute("href") or ""
                        onclick_value = await title_elem.get_attribute("onclick") or ""

                    if not title.strip():
                        continue

                    # onclick에서 ISBN과 제어번호 추출
                    # 예: fn_goView('9791127047788','230336289,')
                    import re

                    isbn = ""
                    control_number = ""
                    onclick_match = re.search(r"fn_goView\('([^']+)','([^']+)'", onclick_value)
                    if onclick_match:
                        isbn = onclick_match.group(1)
                        control_number = onclick_match.group(2).replace(",", "").strip()

                    # dot-list에서 메타데이터 추출
                    dot_list = await item.query_selector(".dot-list")
                    author = ""
                    publisher = ""
                    isbn_full = ""

                    if dot_list:
                        list_items = await dot_list.query_selector_all("li")
                        for li in list_items:
                            li_text = await li.inner_text()
                            if "저자" in li_text:
                                author = li_text.replace("저자", "").replace(":", "").strip()
                            elif "발행처" in li_text:
                                publisher = li_text.replace("발행처", "").replace(":", "").strip()
                            elif "ISBN" in li_text:
                                isbn_full = li_text.replace("ISBN", "").replace(":", "").strip()

                    # 발행년 추출 (텍스트에서)
                    pub_year = ""
                    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", item_text)
                    if year_match:
                        pub_year = year_match.group(1)

                    record = {
                        "title": title.strip(),
                        "author": author,
                        "publisher": publisher,
                        "pub_year": pub_year,
                        "isbn": isbn or isbn_full.split()[0] if isbn_full else "",  # ISBN만 추출
                        "control_number": control_number,
                        "detail_url": href,
                        "detail_id": control_number or self._extract_id_from_url(href),
                        "raw_text": item_text[:200],  # 디버깅용
                    }

                    records.append(record)
                    print(f"  [{idx + 1}] {title[:50]}...")

                except Exception as e:
                    print(f"레코드 {idx + 1} 추출 오류: {e}")
                    continue

        except Exception as e:
            print(f"검색 결과 추출 실패: {e}")
            import traceback

            traceback.print_exc()

        return records

    def _extract_metadata_from_text(self, text: str) -> dict[str, str]:
        """
        텍스트에서 메타데이터 추출 (정규표현식 사용)

        Args:
            text: 검색 결과 항목 텍스트

        Returns:
            메타데이터 딕셔너리
        """
        metadata = {}

        # 저자 추출
        author_patterns = [
            r"저자[:\s]*(.+?)(?:\n|발행|출판|ISBN)",
            r"지은이[:\s]*(.+?)(?:\n|발행|출판)",
            r"著者[:\s]*(.+?)(?:\n|発行)",
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["author"] = match.group(1).strip()
                break

        # 발행처 추출
        publisher_patterns = [
            r"발행처[:\s]*(.+?)(?:\n|발행년|ISBN)",
            r"발행사[:\s]*(.+?)(?:\n|발행년)",
            r"출판사[:\s]*(.+?)(?:\n|출판년)",
            r"発行[:\s]*(.+?)(?:\n|ISBN)",
        ]
        for pattern in publisher_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["publisher"] = match.group(1).strip()
                break

        # 발행년 추출
        year_match = re.search(r"발행년[:\s]*(\d{4})|출판년[:\s]*(\d{4})", text)
        if year_match:
            metadata["pub_year"] = year_match.group(1) or year_match.group(2)
        else:
            # 연도만 추출 (4자리 숫자)
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
            if year_match:
                metadata["pub_year"] = year_match.group(1)

        # ISBN 추출
        isbn_match = re.search(r"ISBN[:\s]*([\d\-X]+)", text, re.IGNORECASE)
        if isbn_match:
            metadata["isbn"] = self._clean_isbn(isbn_match.group(1))
        else:
            # ISBN 없이 13자리 숫자
            metadata["isbn"] = self._extract_isbn_from_text(text)

        # 제어번호 추출
        control_match = re.search(r"제어번호[:\s]*(\w+)", text)
        if control_match:
            metadata["control_number"] = control_match.group(1).strip()

        return metadata

    def _parse_text_results(self, text: str) -> list[dict[str, Any]]:
        """
        전체 텍스트에서 검색 결과 파싱 (대체 방법)

        Args:
            text: 페이지 전체 텍스트

        Returns:
            레코드 리스트
        """
        records = []

        # 간단한 휴리스틱: 연속된 줄을 하나의 레코드로 간주
        lines = text.split("\n")
        current_record = []

        for line in lines:
            line = line.strip()
            if not line:
                if current_record:
                    # 레코드 완성
                    record_text = "\n".join(current_record)
                    if len(record_text) > 20:  # 최소 길이 체크
                        metadata = self._extract_metadata_from_text(record_text)
                        if metadata.get("isbn") or metadata.get("author"):
                            records.append(
                                {
                                    "title": current_record[0][:100],
                                    **metadata,
                                    "raw_text": record_text[:200],
                                }
                            )
                    current_record = []
            else:
                current_record.append(line)

        return records[:10]  # 최대 10개

    async def _click_next_page(self) -> bool:
        """
        다음 페이지 클릭 (서지정보 페이징 구조 반영)

        Returns:
            다음 페이지 존재 여부
        """
        try:
            # 다음 페이지 버튼 선택자 (여러 패턴 시도)
            next_selectors = [
                'a:has-text("다음")',
                'a:has-text(">")',
                "a.paging-next",
                ".nextPage",
                ".pageBtn.next",
                'a[title="다음"]',
            ]

            for selector in next_selectors:
                try:
                    next_button = await self._page.query_selector(selector)
                    if next_button:
                        # disabled 체크
                        is_disabled = await next_button.get_attribute("disabled")
                        class_name = await next_button.get_attribute("class") or ""

                        if not is_disabled and "disabled" not in class_name:
                            print(f"다음 페이지 버튼 클릭: {selector}")
                            await next_button.click()
                            await self._page.wait_for_load_state("networkidle", timeout=10000)
                            return True
                except Exception:
                    continue

        except Exception as e:
            print(f"다음 페이지 클릭 실패: {e}")

        return False

    async def _extract_detail_page(self) -> dict[str, Any]:
        """
        상세 페이지에서 레코드 정보 추출 (실제 서지정보 상세 페이지 구조 반영)

        Returns:
            레코드 데이터
        """
        try:
            # 상세 정보 대기 (타임아웃 짧게)
            try:
                await self._page.wait_for_selector(
                    "#content_body, .detailView, .bookDetail, .detail_info", timeout=5000
                )
            except Exception:
                print("상세 페이지 로딩 타임아웃")

            # 페이지 전체 텍스트 추출 (대체 방법)
            page_text = await self._page.inner_text("#content_body, body")

            # 텍스트에서 메타데이터 추출
            metadata = self._extract_metadata_from_text(page_text)

            # DOM에서 추가 정보 시도
            # 제목
            title_elem = await self._page.query_selector(".title, .bookTitle, h2, h3")
            title = await title_elem.inner_text() if title_elem else metadata.get("title", "")

            # 저자 (메타데이터 우선)
            author = metadata.get("author", "")

            # 발행처 (메타데이터 우선)
            publisher = metadata.get("publisher", "")

            # 발행년 (메타데이터 우선)
            pub_year = metadata.get("pub_year", "")

            # 페이지수 추출
            pages = None
            pages_match = re.search(r"페이지[:\s]*(\d+)|(\d+)\s*p", page_text, re.IGNORECASE)
            if pages_match:
                pages = int(pages_match.group(1) or pages_match.group(2))

            # ISBN (메타데이터 우선)
            isbn = metadata.get("isbn", "")

            # KDC 분류
            kdc = None
            kdc_match = re.search(r"KDC[:\s]*(\d{3})|분류[:\s]*(\d{3})", page_text)
            if kdc_match:
                kdc = kdc_match.group(1) or kdc_match.group(2)

            # URL에서 ID 추출
            url = self._page.url
            detail_id = self._extract_id_from_url(url)

            return {
                "title": title.strip() if title else "",
                "author": author.strip() if author else "",
                "publisher": publisher.strip() if publisher else "",
                "pub_year": pub_year,
                "pages": pages,
                "isbn": isbn,
                "kdc": kdc,
                "detail_id": detail_id,
                "detail_url": url,
                "raw_text": page_text[:500],  # 디버깅용
            }

        except Exception as e:
            print(f"상세 페이지 추출 실패: {e}")
            import traceback

            traceback.print_exc()
            return {}

    def _extract_isbn_from_text(self, text: str) -> str:
        """텍스트에서 ISBN 추출"""
        # ISBN-13 (13자리 숫자)
        isbn13_match = re.search(r"\d{13}", text)
        if isbn13_match:
            return isbn13_match.group()

        # ISBN-10 (10자리 숫자 또는 X로 끝남)
        isbn10_match = re.search(r"\d{9}[\dXx]", text)
        if isbn10_match:
            return isbn10_match.group()

        return ""

    def _clean_isbn(self, isbn: str) -> str:
        """ISBN 정제 (하이픈, 공백 제거)"""
        return isbn.replace("-", "").replace(" ", "").strip()

    def _extract_year(self, year_text: str) -> str:
        """년도 파싱 (YYYY 형식)"""
        year_match = re.search(r"\d{4}", year_text)
        return year_match.group() if year_match else ""

    def _extract_id_from_url(self, url: str) -> str:
        """URL에서 도서 ID 추출"""
        # 일반적인 패턴: ?isbn=XXX 또는 ?key=XXX
        import urllib.parse

        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)

        # isbn 파라미터
        if "isbn" in params:
            return params["isbn"][0]

        # key 파라미터
        if "key" in params:
            return params["key"][0]

        # 마지막 경로 세그먼트
        path_parts = parsed.path.split("/")
        return path_parts[-1] if path_parts else ""


class BookCollectorPlaywright:
    """
    Playwright 기반 대규모 도서 수집기

    국립도서관 웹사이트를 스크래핑하여 도서 데이터를 수집합니다.
    """

    def __init__(
        self,
        headless: bool = True,
        delay: float = 1.0,
    ):
        """
        수집기 초기화

        Args:
            headless: 헤드리스 모드
            delay: 요청 간 지연 시간 (초)
        """
        self.headless = headless
        self.delay = delay
        self.scraper: NationalLibraryScraper | None = None
        self.collected_records: list[dict[str, Any]] = []

    async def initialize(self) -> None:
        """수집기 초기화"""
        self.scraper = NationalLibraryScraper(headless=self.headless)
        await self.scraper.initialize()

    async def close(self) -> None:
        """수집기 종료"""
        if self.scraper:
            await self.scraper.close()

    async def collect_by_keyword(
        self,
        keyword: str,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """
        키워드로 도서 수집

        Args:
            keyword: 검색어
            max_records: 최대 수집 개수

        Returns:
            수집된 레코드 리스트
        """
        if self.scraper is None:
            raise RuntimeError("Collector not initialized")

        # 검색 (최대 5 페이지)
        results = await self.scraper.search_by_keyword(
            keyword=keyword,
            max_pages=5,
            max_records=max_records,
        )

        self.collected_records.extend(results)

        return results

    async def collect_by_kdc(
        self,
        kdc: str,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """
        KDC 분류로 도서 수집

        Args:
            kdc: KDC 분류코드 (예: 005, 813)
            max_records: 최대 수집 개수

        Returns:
            수집된 레코드 리스트
        """
        if self.scraper is None:
            raise RuntimeError("Collector not initialized")

        # KDC별 검색어
        kdc_keywords = {
            "0": ["백과사전", "사전"],
            "1": ["철학", "심리"],
            "2": ["종교", "불교"],
            "3": ["경제", "정치"],
            "4": ["수학", "물리"],
            "5": ["컴퓨터", "프로그래밍"],
            "6": ["미술", "음악"],
            "7": ["한국어", "영어"],
            "8": ["소설", "시"],
            "9": ["역사", "전기"],
        }

        keywords = kdc_keywords.get(kdc[0], ["도서"])

        results = []

        for keyword in keywords:
            if len(results) >= max_records:
                break

            batch = await self.scraper.search_by_keyword(
                keyword=keyword,
                max_pages=2,
                max_records=max_records - len(results),
            )

            results.extend(batch)

            # API 속도 제한 준수
            await asyncio.sleep(self.delay)

        self.collected_records.extend(results)

        return results

    async def save_to_database(
        self,
        db_path: str = "kormarc.db",
        data_source: str = "national_library_web",
    ) -> int:
        """
        수집된 레코드를 데이터베이스에 저장

        Args:
            db_path: 데이터베이스 파일 경로
            data_source: 데이터 소스 표시

        Returns:
            저장된 레코드 수
        """
        from kormarc.db import KORMARCDatabase
        from kormarc.kormarc_builder import BookInfo, KORMARCBuilder

        if not self.collected_records:
            print("저장할 레코드가 없습니다.")
            return 0

        db = KORMARCDatabase(db_path)
        await db.initialize()

        builder = KORMARCBuilder()
        saved_count = 0

        for scraped_record in self.collected_records:
            try:
                # 스크래핑 데이터를 BookInfo로 변환
                book = BookInfo(
                    isbn=scraped_record.get("isbn", f"unknown_{saved_count}"),
                    title=scraped_record.get("title", "제목 없음"),
                    author=scraped_record.get("author"),
                    publisher=scraped_record.get("publisher"),
                    pub_year=scraped_record.get("pub_year"),
                    pages=scraped_record.get("pages"),
                    kdc=scraped_record.get("kdc"),
                    category="book",
                )

                # TOON JSON 생성
                toon_dict = builder.build_toon_dict(book)

                # 데이터베이스 저장
                await db.save_record(
                    toon_id=toon_dict["toon_id"],
                    record_data=toon_dict,
                    scraped_at=data_source,
                    data_source=data_source,
                )

                saved_count += 1

                if saved_count % 10 == 0:
                    print(f"저장 진행: {saved_count}/{len(self.collected_records)} 건")

            except Exception as e:
                print(f"저장 실패: {scraped_record.get('isbn', 'unknown')} - {e}")
                continue

        await db.close()

        print(f"총 {saved_count}건 저장 완료")
        return saved_count


# 모듈 레벨 테스트
if __name__ == "__main__":
    import asyncio

    async def test_scraper():
        """스크래퍼 테스트"""
        async with NationalLibraryScraper(headless=False) as scraper:
            # 키워드 검색 테스트 (소규모)
            results = await scraper.search_by_keyword("파이썬", max_pages=1, max_records=5)

            print(f"검색 결과: {len(results)}건")
            for i, record in enumerate(results):
                print(f"{i + 1}. {record.get('title')} - {record.get('isbn')}")

    # asyncio.run(test_scraper())
    print("스크래퍼 테스트 (브라우저 표시로 실행 시 주석 해제)")
