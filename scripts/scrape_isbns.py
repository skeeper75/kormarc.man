"""ISBN scraper for National Library of Korea using Playwright.

This module scrapes ISBNs and KORMARC data from the National Library of Korea
website across multiple categories: general books, academic journals, serials, and comics.
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from playwright.async_api import Browser, Page, async_playwright

# National Library of Korea search URLs
NLP_SEARCH_URL = "https://www.nl.go.kr/seoji/contents/SearchResult.do"
# Alternative: KORMARC service URL
KORMARC_URL = "https://www.nl.go.kr/kormarc/"

# Categories to scrape
CATEGORIES = {
    "general": "도서 전체",
    "academic": "학술지",
    "serial": "연속간행물",
    "comic": "만화",
}


async def create_browser(headless: bool = True) -> tuple[Browser, Page]:
    """Create a browser instance with Playwright.

    Args:
        headless: Whether to run browser in headless mode

    Returns:
        Tuple of (browser, page)
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page()

    # Set user agent to avoid detection
    await page.set_extra_http_headers(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )

    return browser, page


async def search_isbns_by_category(
    page: Page,
    category: str,
    keyword: str = "",
    max_results: int = 1250,
    delay_seconds: float = 1.0,
) -> list[str]:
    """Search for ISBNs by category.

    Args:
        page: Playwright page instance
        category: Category to search (general, academic, serial, comic)
        keyword: Search keyword (optional)
        max_results: Maximum number of results to retrieve
        delay_seconds: Delay between requests to avoid rate limiting

    Returns:
        List of ISBNs
    """
    isbns = []
    page_num = 1

    print(f"Searching category: {category}")

    while len(isbns) < max_results:
        try:
            # Navigate to search page
            search_url = f"{NLP_SEARCH_URL}?category={category}&keyword={keyword}&page={page_num}"
            await page.goto(search_url, wait_until="networkidle")

            # Wait for results to load
            await asyncio.sleep(delay_seconds)

            # Extract ISBNs from page
            page_isbns = await page.evaluate(
                """
                () => {
                    const isbns = [];
                    // Look for ISBN in various possible locations
                    const selectors = [
                        '.isbn',
                        '.ISBN',
                        '[data-isbn]',
                        'td:contains("ISBN")',
                        '.book-info:contains("ISBN")',
                    ];

                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(el => {
                            const text = el.textContent || '';
                            // Extract ISBN pattern (10 or 13 digits)
                            const match = text.match(/\\b(?:ISBN[-\\s]?)?(?:97[89][-\\s]?)?(\\d{1,5}[-\\s]?\\d{1,7}[-\\s]?\\d{1,6}[-\\s]?\\d)\\b/);
                            if (match) {
                                const isbn = match[1].replace(/[-\\s]/g, '');
                                if (isbn.length === 10 || isbn.length === 13) {
                                    isbns.push(isbn);
                                }
                            }
                        });
                    }

                    // Also try to find links to detail pages
                    const detailLinks = document.querySelectorAll('a[href*="detail"]');
                    detailLinks.forEach(link => {
                        const href = link.getAttribute('href');
                        const match = href?.match(/isbn[=:]([^&]+)/);
                        if (match) {
                            const isbn = match[1].replace(/[-\\s]/g, '');
                            if (isbn.length === 10 || isbn.length === 13) {
                                isbns.push(isbn);
                            }
                        }
                    });

                    return [...new Set(isbns)];  // Remove duplicates
                }
            """
            )

            isbns.extend(page_isbns)
            print(f"  Page {page_num}: Found {len(page_isbns)} ISBNs (Total: {len(isbns)})")

            # Check if there's a next page
            has_next = await page.evaluate(
                """
                () => {
                    const nextButton = document.querySelector('.next:not(.disabled), .paging .next, a[rel="next"]');
                    return nextButton !== null && !nextButton.classList.contains('disabled');
                }
            """
            )

            if not has_next:
                print("  No more pages available")
                break

            page_num += 1

        except Exception as e:
            print(f"  Error on page {page_num}: {e}")
            break

    return isbns[:max_results]


async def fetch_kormarc_data(page: Page, isbn: str) -> dict[str, Any] | None:
    """Fetch KORMARC data for a specific ISBN.

    Args:
        page: Playwright page instance
        isbn: ISBN to fetch data for

    Returns:
        KORMARC data dictionary or None if not found
    """
    try:
        # Navigate to KORMARC detail page
        detail_url = f"{KORMARC_URL}detail?isbn={isbn}"
        await page.goto(detail_url, wait_until="networkidle")

        # Extract KORMARC data
        kormarc_data = await page.evaluate(
            """
            () => {
                // Try to find KORMARC data in various formats
                const kormarcText = document.querySelector('.kormarc, #kormarc, pre, code');
                if (kormarcText) {
                    return {
                        raw: kormarcText.textContent,
                        format: 'text'
                    };
                }

                // Try to parse from table fields
                const fields = {};
                const fieldRows = document.querySelectorAll('table tr');
                fieldRows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const tag = cells[0].textContent.trim();
                        const value = cells[1].textContent.trim();
                        if (tag && value) {
                            fields[tag] = value;
                        }
                    }
                });

                if (Object.keys(fields).length > 0) {
                    return {
                        fields: fields,
                        format: 'fields'
                    };
                }

                return null;
            }
        """
        )

        return kormarc_data

    except Exception as e:
        print(f"    Error fetching KORMARC for {isbn}: {e}")
        return None


async def scrape_category(
    category: str,
    output_dir: Path,
    target_count: int = 1250,
    headless: bool = True,
) -> dict[str, Any]:
    """Scrape ISBNs and KORMARC data for a category.

    Args:
        category: Category to scrape
        output_dir: Directory to save results
        target_count: Target number of records
        headless: Whether to run browser in headless mode

    Returns:
        Results dictionary with counts and statistics
    """
    browser, page = await create_browser(headless=headless)

    try:
        # Search for ISBNs
        isbns = await search_isbns_by_category(
            page, category, max_results=target_count, delay_seconds=2.0
        )

        print(f"Found {len(isbns)} ISBNs for {category}")

        # Fetch KORMARC data for each ISBN
        results = []
        for i, isbn in enumerate(isbns):
            print(f"  Fetching KORMARC {i + 1}/{len(isbns)}: {isbn}")

            kormarc_data = await fetch_kormarc_data(page, isbn)
            if kormarc_data:
                results.append(
                    {
                        "isbn": isbn,
                        "category": category,
                        "kormarc": kormarc_data,
                    }
                )

            # Delay to avoid rate limiting
            await asyncio.sleep(1.0)

        # Save results
        output_file = output_dir / f"{category}_isbns.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return {
            "category": category,
            "target_count": target_count,
            "isbn_count": len(isbns),
            "kormarc_count": len(results),
            "output_file": str(output_file),
        }

    finally:
        await browser.close()


async def scrape_all_categories(
    output_dir: Path,
    target_per_category: int = 1250,
    headless: bool = True,
    concurrent_categories: int = 2,
) -> dict[str, Any]:
    """Scrape all categories.

    Args:
        output_dir: Directory to save results
        target_per_category: Target number of records per category
        headless: Whether to run browser in headless mode
        concurrent_categories: Number of categories to scrape concurrently

    Returns:
        Overall results dictionary
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    categories = list(CATEGORIES.keys())
    results = {}

    # Process categories in batches
    for i in range(0, len(categories), concurrent_categories):
        batch = categories[i : i + concurrent_categories]

        # Scrape categories concurrently
        tasks = [scrape_category(cat, output_dir, target_per_category, headless) for cat in batch]

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for cat, result in zip(batch, batch_results):
            if isinstance(result, Exception):
                print(f"Error scraping {cat}: {result}")
                results[cat] = {"error": str(result)}
            else:
                results[cat] = result

    # Save summary
    summary_file = output_dir / "scraping_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


async def main():
    """Main entry point for ISBN scraping."""
    import argparse

    parser = argparse.ArgumentParser(description="Scrape ISBNs from National Library of Korea")
    parser.add_argument(
        "--category",
        choices=list(CATEGORIES.keys()) + ["all"],
        default="all",
        help="Category to scrape",
    )
    parser.add_argument("--output", type=Path, default=Path("data/isbns"), help="Output directory")
    parser.add_argument("--count", type=int, default=1250, help="Target records per category")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser")

    args = parser.parse_args()

    if args.category == "all":
        results = await scrape_all_categories(args.output, args.count, args.headless)
    else:
        result = await scrape_category(args.category, args.output, args.count, args.headless)
        results = {args.category: result}

    # Print summary
    print("\n" + "=" * 60)
    print("Scraping Summary")
    print("=" * 60)
    for category, result in results.items():
        if "error" in result:
            print(f"{category}: ERROR - {result['error']}")
        else:
            print(f"{category}: {result['kormarc_count']}/{result['target_count']} records")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
