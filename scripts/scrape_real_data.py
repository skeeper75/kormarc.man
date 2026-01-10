"""
실제 KORMARC 데이터 스크래핑 스크립트

국립도서관(National Library of Korea)에서 실제 KORMARC 데이터를 스크래핑합니다.
Playwright를 사용하여 headless 브라우징을 수행합니다.

사용법:
    python scripts/scrape_real_data.py --category general --max-pages 10
    python scripts/scrape_real_data.py --category academic --max-pages 5
    python scripts/scrape_real_data.py --all --max-pages 20

카테고리:
    - general: 일반 도서
    - academic: 학술지
    - serial: 연속 간행물
    - comic: 만화
    - all: 모든 카테고리
"""

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kormarc.parser.kormarc_parser import KORMARCParser
from kormarc.toon_generator import TOONGenerator, determine_record_type, toon_to_json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(project_root / "logs" / "scraping.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ScrapingConfig:
    """스크래핑 설정"""

    category: str
    """카테고리 (general, academic, serial, comic, all)"""

    max_pages: int = 10
    """최대 스크래핑 페이지 수"""

    output_dir: Path = field(default_factory=lambda: project_root / "data" / "isbns")
    """출력 디렉토리"""

    headless: bool = True
    """Headless 모드"""

    timeout: int = 30000
    """페이지 타임아웃 (ms)"""

    delay: float = 1.0
    """요청 간 지연 (초)"""


@dataclass
class ScrapingStats:
    """스크래핑 통계"""

    start_time: datetime = field(default_factory=datetime.now)
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    isbns_found: int = 0

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "start_time": self.start_time.isoformat(),
            "duration_seconds": duration,
            "total_records": self.total_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "isbns_found": self.isbns_found,
            "success_rate": (
                self.successful_records / self.total_records * 100 if self.total_records > 0 else 0
            ),
        }


class KORMARCScraper:
    """
    KORMARC 데이터 스크래퍼

    Playwright를 사용하여 국립도서관에서 KORMARC 데이터를 수집합니다.
    """

    BASE_URL = "https://www.nl.go.kr"
    SEARCH_URL = f"{BASE_URL}/seoji/contents/S50100000000.do"

    def __init__(self, config: ScrapingConfig):
        """
        스크래퍼 초기화

        Args:
            config: 스크래핑 설정
        """
        self.config = config
        self.stats = ScrapingStats()
        self.parser = KORMARCParser()
        self.toon_generator = TOONGenerator()

        # 출력 디렉토리 생성
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (project_root / "logs").mkdir(parents=True, exist_ok=True)

    async def init_browser(self):
        """브라우저 초기화"""
        try:
            from playwright.async_api import async_playwright

            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.config.headless)
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.timeout)

            logger.info("브라우저 초기화 완료")
        except ImportError:
            logger.error("Playwright가 설치되지 않았습니다.")
            logger.error("설치 명령: pip install playwright && playwright install chromium")
            raise

    async def close_browser(self):
        """브라우저 종료"""
        if hasattr(self, "context"):
            await self.context.close()
        if hasattr(self, "browser"):
            await self.browser.close()
        if hasattr(self, "playwright"):
            await self.playwright.stop()
        logger.info("브라우저 종료 완료")

    async def search_records(self, category: str, page_num: int = 1) -> list[str]:
        """
        레코드 검색

        Args:
            category: 카테고리
            page_num: 페이지 번호

        Returns:
            ISBN 목록
        """
        logger.info(f"카테고리 '{category}' 페이지 {page_num} 검색 시작...")

        try:
            # 검색 페이지로 이동
            search_params = self._get_search_params(category)
            url = f"{self.SEARCH_URL}?{search_params}"

            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")

            # ISBN 추출
            isbns = await self.page.evaluate(
                """
                () => {
                    const isbns = [];
                    // 검색 결과에서 ISBN 추출 (실제 페이지 구조에 맞게 조정 필요)
                    const elements = document.querySelectorAll('[data-isbn]');
                    elements.forEach(el => {
                        isbns.push(el.getAttribute('data-isbn'));
                    });
                    return isbns;
                }
            """
            )

            logger.info(f"페이지 {page_num}에서 {len(isbns)}개 ISBN 발견")
            self.stats.isbns_found += len(isbns)

            return isbns

        except Exception as e:
            logger.error(f"검색 실패 (페이지 {page_num}): {e}")
            return []

    def _get_search_params(self, category: str) -> str:
        """
        카테고리별 검색 파라미터 반환

        Args:
            category: 카테고리

        Returns:
            URL 쿼리 파라미터
        """
        # TODO: 실제 국립도서관 검색 API 파라미터로 업데이트 필요
        params = {
            "general": "category=book",
            "academic": "category=academic",
            "serial": "category=serial",
            "comic": "category=comic",
        }
        return params.get(category, "category=all")

    async def fetch_kormarc_data(self, isbn: str) -> str | None:
        """
        ISBN으로 KORMARC 데이터 가져오기

        Args:
            isbn: ISBN

        Returns:
            KORMARC 데이터 문자열 (실패 시 None)
        """
        logger.info(f"ISBN {isbn} 데이터 가져오기...")

        try:
            # KORMARC 상세 페이지로 이동
            detail_url = f"{self.BASE_URL}/kormarc/{isbn}"
            await self.page.goto(detail_url)
            await self.page.wait_for_load_state("networkidle")

            # KORMARC 데이터 추출
            kormarc_data = await self.page.evaluate(
                """
                () => {
                    // 실제 페이지 구조에 맞게 KORMARC 데이터 추출
                    const kormarcElement = document.querySelector('[data-kormarc]');
                    return kormarcElement ? kormarcElement.getAttribute('data-kormarc') : null;
                }
            """
            )

            if kormarc_data:
                logger.info(f"ISBN {isbn}: KORMARC 데이터 가져오기 성공")
                self.stats.successful_records += 1
            else:
                logger.warning(f"ISBN {isbn}: KORMARC 데이터 없음")
                self.stats.failed_records += 1

            self.stats.total_records += 1
            return kormarc_data

        except Exception as e:
            logger.error(f"ISBN {isbn} 데이터 가져오기 실패: {e}")
            self.stats.total_records += 1
            self.stats.failed_records += 1
            return None

    def save_to_json(self, data: list[dict], category: str):
        """
        JSON 파일로 저장

        Args:
            data: 저장할 데이터
            category: 카테고리
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scraped_{category}_{timestamp}.json"
        filepath = self.config.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"데이터 저장 완료: {filepath} ({len(data)}개 레코드)")

    async def scrape_category(self, category: str):
        """
        카테고리별 스크래핑

        Args:
            category: 카테고리
        """
        logger.info(f"카테고리 '{category}' 스크래핑 시작...")
        category_stats = ScrapingStats()
        scraped_data = []

        try:
            for page in range(1, self.config.max_pages + 1):
                # ISBN 검색
                isbns = await self.search_records(category, page)

                if not isbns:
                    logger.warning(f"페이지 {page}: ISBN 없음, 다음 페이지로...")
                    continue

                # 각 ISBN별 KORMARC 데이터 가져오기
                for isbn in isbns:
                    kormarc_data = await self.fetch_kormarc_data(isbn)

                    if kormarc_data:
                        try:
                            # KORMARC 파싱
                            record = self.parser.parse(kormarc_data)

                            # TOON 생성
                            record_type = determine_record_type(record)
                            toon_id = self.toon_generator.generate(record_type)

                            # JSON 변환
                            json_data = toon_to_json(record, toon_id)
                            json_data["scraped_at"] = datetime.now().isoformat()
                            json_data["data_source"] = "National Library of Korea"
                            json_data["category"] = category

                            scraped_data.append(json_data)
                            category_stats.successful_records += 1

                        except Exception as e:
                            logger.error(f"ISBN {isbn} 파싱 실패: {e}")
                            category_stats.failed_records += 1

                    # 요청 간 지연
                    await asyncio.sleep(self.config.delay)

                # 페이지별 저장
                if scraped_data:
                    self.save_to_json(scraped_data, category)

                category_stats.total_records += len(isbns)

        except Exception as e:
            logger.error(f"카테고리 '{category}' 스크래핑 실패: {e}")

        finally:
            logger.info(f"카테고리 '{category}' 스크래핑 완료")
            logger.info(f"통계: {category_stats.to_dict()}")

            self.stats.total_records += category_stats.total_records
            self.stats.successful_records += category_stats.successful_records
            self.stats.failed_records += category_stats.failed_records

    async def run(self):
        """스크래핑 실행"""
        logger.info("스크래핑 시작...")
        logger.info(f"설정: {self.config}")

        try:
            await self.init_browser()

            categories = (
                ["general", "academic", "serial", "comic"]
                if self.config.category == "all"
                else [self.config.category]
            )

            for category in categories:
                await self.scrape_category(category)

            # 최종 통계 저장
            stats_file = (
                self.config.output_dir
                / f"scraping_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"스크래핑 완료: {stats_file}")
            logger.info(f"최종 통계: {self.stats.to_dict()}")

        except Exception as e:
            logger.error(f"스크래핑 실패: {e}")
            raise

        finally:
            await self.close_browser()


async def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="국립도서관 KORMARC 데이터 스크래핑",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--category",
        choices=["general", "academic", "serial", "comic", "all"],
        default="general",
        help="카테고리 (기본값: general)",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="최대 스크래핑 페이지 수 (기본값: 10)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Headless 모드 (기본값: True)",
    )

    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Headless 모드 비활성화",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="요청 간 지연 시간 (초, 기본값: 1.0)",
    )

    args = parser.parse_args()

    config = ScrapingConfig(
        category=args.category,
        max_pages=args.max_pages,
        headless=args.headless,
        delay=args.delay,
    )

    scraper = KORMARCScraper(config)
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
