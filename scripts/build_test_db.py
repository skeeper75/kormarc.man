"""Build test database from scraped KORMARC data.

This script processes scraped ISBN and KORMARC data, parses it using
KORMARCParser, converts to TOON/ULID format, and stores in SQLite database.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.db_schema import (
    bulk_insert_records,
    create_schema,
    get_connection,
    get_statistics,
)


async def load_scraped_data(data_dir: Path) -> list[tuple[str, str, str]]:
    """Load scraped data from JSON files.

    Args:
        data_dir: Directory containing scraped data files

    Returns:
        List of (isbn, category, raw_kormarc) tuples
    """
    records = []

    # Find all JSON files in data directory
    json_files = list(data_dir.glob("*_isbns.json"))

    for json_file in json_files:
        print(f"Loading {json_file.name}...")

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        # Extract category from filename
        category = json_file.stem.replace("_isbns", "")

        for item in data:
            isbn = item.get("isbn", "")
            kormarc_data = item.get("kormarc", {})

            # Convert KORMARC data to text format
            if kormarc_data.get("format") == "text":
                raw_kormarc = kormarc_data.get("raw", "")
            elif kormarc_data.get("format") == "fields":
                # Build KORMARC text format from fields
                raw_kormarc = build_kormarc_from_fields(kormarc_data.get("fields", {}))
            else:
                # Generate minimal KORMARC record
                raw_kormarc = generate_minimal_kormarc(isbn, category)

            records.append((isbn, category, raw_kormarc))

    print(f"Loaded {len(records)} records from {len(json_files)} files")
    return records


def build_kormarc_from_fields(fields: dict) -> str:
    """Build KORMARC text format from field dictionary.

    Args:
        fields: Dictionary of field tag to value mappings

    Returns:
        KORMARC text format string
    """
    lines = []

    # Leader (default)
    leader = "00714cam  2200205 a 4500"
    lines.append(leader)

    # Add fields in tag order
    for tag in sorted(fields.keys()):
        value = fields[tag]
        if tag.isdigit() and int(tag) <= 9:
            # Control field
            lines.append(f"{tag.zfill(3)}  {value}")
        else:
            # Data field - assume simple format
            lines.append(f"{tag.zfill(3)}  |a{value}")

    return "\n".join(lines)


def generate_minimal_kormarc(isbn: str, category: str) -> str:
    """Generate minimal KORMARC record when full data is not available.

    Args:
        isbn: ISBN identifier
        category: Record category

    Returns:
        Minimal KORMARC text format
    """
    return f"""00714cam  2200205 a 4500
001 TEST{isbn}
020  |a{isbn}
245 10|aTest Record for {isbn}|bCategory: {category}
260  |a서울|b국립도서관|c{datetime.now().year}
300  |a1 p.|b삽화|c24 cm
650  0|aKORMARC|x{category}
"""


async def build_database(
    input_dir: Path,
    output_db: Path,
    target_records: int = 5000,
    batch_size: int = 500,
) -> dict:
    """Build test database from scraped data.

    Args:
        input_dir: Directory containing scraped data
        output_db: Path to output SQLite database
        target_records: Target number of records to insert
        batch_size: Number of records to process per batch

    Returns:
        Statistics dictionary
    """
    print("=" * 60)
    print("Building KORMARC Test Database")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output database: {output_db}")
    print(f"Target records: {target_records}")
    print(f"Batch size: {batch_size}")
    print("=" * 60)

    # Load scraped data
    records = await load_scraped_data(input_dir)

    if len(records) == 0:
        print("No records found. Generating synthetic data...")

        # Generate synthetic records
        records = generate_synthetic_records(target_records)
        print(f"Generated {len(records)} synthetic records")

    # Limit to target count
    records = records[:target_records]

    # Create database schema
    print("\nCreating database schema...")
    await create_schema(output_db)

    # Get database connection
    conn = await get_connection(output_db)

    # Insert records in batches
    print(f"\nInserting {len(records)} records in batches of {batch_size}...")
    inserted_count = 0
    failed_count = 0

    import time

    start_time = time.time()

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(records) + batch_size - 1) // batch_size

        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} records)...")

        try:
            count = await bulk_insert_records(conn, batch)
            inserted_count += count
            print(f"    Inserted {count} records")

        except Exception as e:
            print(f"    Error in batch {batch_num}: {e}")
            failed_count += len(batch)

    await conn.close()

    duration = time.time() - start_time

    # Get final statistics
    print("\nGathering statistics...")
    conn = await get_connection(output_db)
    stats = await get_statistics(conn)
    await conn.close()

    # Print summary
    print("\n" + "=" * 60)
    print("Database Build Summary")
    print("=" * 60)
    print(f"Total records: {stats['total_records']}")
    print(f"Inserted: {inserted_count}")
    print(f"Failed: {failed_count}")
    print(f"Duration: {duration:.2f}s")
    print(f"Speed: {inserted_count / duration:.2f} records/sec")
    print("\nRecords by category:")
    for category, count in stats["category_counts"].items():
        print(f"  {category}: {count}")
    print(f"\nDatabase size: {stats['database_size_bytes'] / 1024 / 1024:.2f} MB")
    print("=" * 60)

    return {
        "total_records": stats["total_records"],
        "inserted": inserted_count,
        "failed": failed_count,
        "duration_seconds": duration,
        "category_counts": stats["category_counts"],
        "database_size_mb": stats["database_size_bytes"] / 1024 / 1024,
    }


def generate_synthetic_records(count: int) -> list[tuple[str, str, str]]:
    """Generate synthetic KORMARC records for testing.

    Args:
        count: Number of records to generate

    Returns:
        List of (isbn, category, raw_kormarc) tuples
    """
    categories = ["general", "academic", "serial", "comic"]
    records = []

    for i in range(count):
        category = categories[i % len(categories)]
        isbn = f"978{8956789012 + i:010d}"

        # Generate varied KORMARC records
        record = f"""00714cam  2200205 a 4500
001 SYNTH{i:010d}
020  |a{isbn}
040  |aKER|cKER
041 0 |akor
050 00 |a{810 + i % 100}|b.{i % 1000}
082 04 |a{800 + i % 100}|221
100 1 |a저자명{i % 100}|g(Author)
245 10|a합성 테스트 도서 제목 {i}|b부제목이 포함된 레코드|c책임 정보
250  |a{1 + i % 5}판
260  |a서울|b테스트 출판사{i % 50}|c{2020 + i % 6}
300  |a{100 + i % 500} p.|b삽화|c{20 + i % 10} cm
440  0 |a시리즈 이름{i % 20}|v{i % 10}
500  |a일반 주석 정보가 포함된 레코드입니다
600 10|a주제명{i % 100}|x세부 주제|x역사|v{i % 5}
650  0|aKORMARC|x카탈로그|x데이터 처리|z한국
700 1 |a공저자{i % 30}|e편저
990  |a로컬 데이터{i % 1000}
"""

        records.append((isbn, category, record))

    return records


async def main():
    """Main entry point for database building."""
    import argparse

    parser = argparse.ArgumentParser(description="Build test database from scraped KORMARC data")
    parser.add_argument(
        "--input", type=Path, default=Path("data/isbns"), help="Input directory with scraped data"
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/kormarc_5000.db"), help="Output database path"
    )
    parser.add_argument("--count", type=int, default=5000, help="Target number of records")
    parser.add_argument("--batch", type=int, default=500, help="Batch size for processing")

    args = parser.parse_args()

    # Build database
    stats = await build_database(args.input, args.output, args.count, args.batch)

    # Save statistics
    stats_file = args.output.parent / f"{args.output.stem}_stats.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(f"\nStatistics saved to: {stats_file}")


if __name__ == "__main__":
    asyncio.run(main())
