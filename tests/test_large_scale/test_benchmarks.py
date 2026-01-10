"""Benchmark test suite for large-scale KORMARC processing.

This module tests performance characteristics of parsing, storage,
and query operations with large datasets.
"""

import time
from pathlib import Path

import pytest

from kormarc.models import Record
from kormarc.parser import KORMARCParser


@pytest.fixture
def sample_kormarc_records() -> list[str]:
    """Generate sample KORMARC records for benchmarking."""

    def generate_record(index: int, category: str = "general") -> str:
        """Generate a single KORMARC record."""
        return f"""00714cam  2200205 a 4500
001 {index:010d}
020  |a{8956789010 + (index % 1000):010d}
245 10|a벤치마크 테스트 도서 {index}|b대규모 데이터 처리 테스트
260  |a서울|b테스트 출판사|c2025
300  |a{300 + index % 100} p.|b삽화|c{24 + index % 5} cm
650  0|aKORMARC|x카탈로깡|x벤치마킹
700  1 |a저자{index % 10}
"""

    records = []
    for i in range(10000):
        categories = ["general", "academic", "serial", "comic"]
        category = categories[i % len(categories)]
        records.append(generate_record(i, category))

    return records


class TestParsingPerformance:
    """Test KORMARC parsing performance."""

    def test_single_record_parsing_performance(self, benchmark, sample_kormarc_records):
        """Benchmark parsing a single KORMARC record."""
        parser = KORMARCParser()
        # sample_kormarc_records is already a generator, next() gets first value
        record_data = sample_kormarc_records

        result = benchmark(parser.parse, record_data)

        assert isinstance(result, Record)
        assert len(result.control_fields) > 0

    def test_batch_parsing_performance(self, sample_kormarc_records):
        """Benchmark parsing 1000 records sequentially."""
        parser = KORMARCParser()

        records = []
        start_time = time.time()

        for i, record_data in enumerate(sample_kormarc_records):
            if i >= 1000:
                break
            record = parser.parse(record_data)
            records.append(record)

        duration = time.time() - start_time

        assert len(records) == 1000
        assert duration < 10.0, f"1000 records should parse in < 10s (took {duration:.2f}s)"

        # Calculate records per second
        rps = 1000 / duration
        print(f"\nParsing speed: {rps:.2f} records/second")

    @pytest.mark.parametrize("record_count", [100, 500, 1000, 5000])
    def test_parsing_scalability(self, sample_kormarc_records, record_count: int):
        """Test parsing performance scales linearly with record count."""
        parser = KORMARCParser()

        records = []
        start_time = time.time()

        for i, record_data in enumerate(sample_kormarc_records):
            if i >= record_count:
                break
            record = parser.parse(record_data)
            records.append(record)

        duration = time.time() - start_time
        rps = record_count / duration

        print(f"\n{record_count} records: {duration:.2f}s ({rps:.2f} records/sec)")

        # Assert reasonable performance: at least 100 records/sec
        assert rps >= 100, f"Parsing too slow: {rps:.2f} records/sec"


class TestSerializationPerformance:
    """Test record serialization performance."""

    def test_json_serialization_performance(self, benchmark, sample_kormarc_records):
        """Benchmark JSON serialization."""
        parser = KORMARCParser()
        record = parser.parse(next(sample_kormarc_records))

        result = benchmark(record.to_json)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_xml_serialization_performance(self, benchmark, sample_kormarc_records):
        """Benchmark XML serialization."""
        parser = KORMARCParser()
        record = parser.parse(next(sample_kormarc_records))

        result = benchmark(record.to_xml)

        assert isinstance(result, str)
        assert result.startswith("<?xml")

    def test_dict_conversion_performance(self, benchmark, sample_kormarc_records):
        """Benchmark dictionary conversion."""
        parser = KORMARCParser()
        record = parser.parse(next(sample_kormarc_records))

        result = benchmark(record.to_dict)

        assert isinstance(result, dict)
        assert "leader" in result


class TestMemoryPerformance:
    """Test memory usage during large-scale processing."""

    def test_memory_leak_detection(self, sample_kormarc_records):
        """Test for memory leaks when parsing many records."""
        import gc
        import tracemalloc

        parser = KORMARCParser()

        # Force garbage collection before measuring
        gc.collect()

        # Start memory tracking
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        # Parse 1000 records
        records = []
        for i, record_data in enumerate(sample_kormarc_records):
            if i >= 1000:
                break
            record = parser.parse(record_data)
            records.append(record)

        # Take another snapshot
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        # Calculate memory usage
        top_stats = snapshot2.compare_to(snapshot1, "lineno")
        total_memory = sum(stat.size_diff for stat in top_stats) / 1024 / 1024  # MB

        print(f"\nMemory usage for 1000 records: {total_memory:.2f} MB")

        # Assert reasonable memory usage: less than 100MB for 1000 records
        assert total_memory < 100, f"Memory usage too high: {total_memory:.2f} MB"

    def test_record_size_distribution(self, sample_kormarc_records):
        """Analyze size distribution of parsed records."""
        parser = KORMARCParser()

        sizes = []
        for i, record_data in enumerate(sample_kormarc_records):
            if i >= 1000:
                break
            record = parser.parse(record_data)
            size = len(record.to_json().encode("utf-8"))
            sizes.append(size)

        avg_size = sum(sizes) / len(sizes)
        min_size = min(sizes)
        max_size = max(sizes)

        print("\nRecord size distribution (bytes):")
        print(f"  Average: {avg_size:.2f}")
        print(f"  Min: {min_size}")
        print(f"  Max: {max_size}")

        # Assert reasonable size: average < 10KB per record
        assert avg_size < 10240, f"Average record size too large: {avg_size:.2f} bytes"


class TestDatabasePerformance:
    """Test database operations performance."""

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self, sample_kormarc_records):
        """Benchmark bulk insert operations."""
        import tempfile

        from kormarc.parser import KORMARCParser
        from scripts.db_schema import bulk_insert_records, create_schema, get_connection

        parser = KORMARCParser()

        # Create test database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)

        try:
            await create_schema(db_path)
            conn = await get_connection(db_path)

            # Prepare records for bulk insert
            records = []
            for i, record_data in enumerate(sample_kormarc_records):
                if i >= 1000:
                    break
                record = parser.parse(record_data)
                isbn = f"123456789{i % 10}"
                category = ["general", "academic", "serial", "comic"][i % 4]
                records.append((isbn, category, record_data))

            # Benchmark bulk insert
            start_time = time.time()
            inserted_count = await bulk_insert_records(conn, records)
            duration = time.time() - start_time

            await conn.close()

            assert inserted_count == 1000
            print(f"\nBulk insert: {inserted_count} records in {duration:.2f}s")
            print(f"Insert speed: {inserted_count / duration:.2f} records/sec")

            # Assert reasonable performance: at least 100 records/sec
            rps = inserted_count / duration
            assert rps >= 100, f"Bulk insert too slow: {rps:.2f} records/sec"

        finally:
            db_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_query_performance_with_index(self, sample_kormarc_records):
        """Benchmark query performance with indexes."""
        import tempfile

        from kormarc.parser import KORMARCParser
        from scripts.db_schema import (
            bulk_insert_records,
            create_schema,
            get_connection,
            get_record_by_isbn,
        )

        parser = KORMARCParser()

        # Create test database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)

        try:
            await create_schema(db_path)
            conn = await get_connection(db_path)

            # Insert 1000 records
            records = []
            for i, record_data in enumerate(sample_kormarc_records):
                if i >= 1000:
                    break
                isbn = f"123456789{i % 10}"
                category = ["general", "academic", "serial", "comic"][i % 4]
                records.append((isbn, category, record_data))

            await bulk_insert_records(conn, records)

            # Benchmark queries
            query_times = []
            for i in range(100):
                isbn = f"123456789{i % 10}"
                start = time.time()
                record = await get_record_by_isbn(conn, isbn)
                duration = time.time() - start
                query_times.append(duration)
                assert record is not None

            await conn.close()

            avg_query_time = sum(query_times) / len(query_times)
            max_query_time = max(query_times)

            print("\nQuery performance (100 queries):")
            print(f"  Average: {avg_query_time * 1000:.2f}ms")
            print(f"  Max: {max_query_time * 1000:.2f}ms")

            # Assert reasonable performance: average query < 10ms
            assert avg_query_time < 0.01, f"Query too slow: {avg_query_time * 1000:.2f}ms"

        finally:
            db_path.unlink(missing_ok=True)


class TestConcurrentProcessing:
    """Test concurrent processing performance."""

    @pytest.mark.asyncio
    async def test_concurrent_parsing(self):
        """Test concurrent parsing with asyncio."""
        import asyncio

        from kormarc.parser import KORMARCParser

        async def parse_record(record_data: str) -> Record:
            parser = KORMARCParser()
            return parser.parse(record_data)

        # Create 100 sample records
        records_data = []
        for i in range(100):
            record_data = f"""00714cam  2200205 a 4500
001 {i:010d}
245 10|aConcurrent Test {i}
"""
            records_data.append(record_data)

        # Parse concurrently
        start_time = time.time()
        tasks = [parse_record(data) for data in records_data]
        records = await asyncio.gather(*tasks)
        duration = time.time() - start_time

        assert len(records) == 100
        print(f"\nConcurrent parsing: {len(records)} records in {duration:.2f}s")
        print(f"Speed: {len(records) / duration:.2f} records/sec")


class TestDataIntegrityPerformance:
    """Test data integrity validation performance."""

    def test_validation_performance(self, benchmark, sample_kormarc_records):
        """Benchmark record validation."""
        parser = KORMARCParser()
        record = parser.parse(next(sample_kormarc_records))

        result = benchmark(record.validate)

        assert result is True

    def test_roundtrip_performance(self, benchmark, sample_kormarc_records):
        """Benchmark parse -> serialize -> parse roundtrip."""
        parser = KORMARCParser()

        def roundtrip(record_data: str) -> Record:
            record1 = parser.parse(record_data)
            json_data = record1.to_json()
            record2 = parser.model_validate_json(json_data)
            return record2

        record_data = next(sample_kormarc_records)
        result = benchmark(roundtrip, record_data)

        assert isinstance(result, Record)


class TestTOONConversionPerformance:
    """Test TOON format conversion performance."""

    def test_toon_conversion_speed(self, benchmark, sample_kormarc_records):
        """Benchmark TOON conversion."""
        from scripts.db_schema import convert_to_toon

        parser = KORMARCParser()
        record = parser.parse(next(sample_kormarc_records))

        result = benchmark(convert_to_toon, record)

        assert isinstance(result, dict)
        assert "title" in result


@pytest.mark.benchmark(group="large_scale")
@pytest.mark.asyncio
class TestLargeScaleBenchmarks:
    """Comprehensive benchmarks for large-scale operations."""

    async def test_full_pipeline_benchmark(self, sample_kormarc_records):
        """Benchmark full pipeline: parse -> convert -> insert -> query."""
        import tempfile

        from kormarc.parser import KORMARCParser
        from scripts.db_schema import (
            bulk_insert_records,
            create_schema,
            get_connection,
            get_record_by_isbn,
        )

        parser = KORMARCParser()

        # Create test database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)

        try:
            # Phase 1: Schema creation
            schema_start = time.time()
            await create_schema(db_path)
            schema_duration = time.time() - schema_start

            conn = await get_connection(db_path)

            # Phase 2: Parse and prepare records
            parse_start = time.time()
            records = []
            for i, record_data in enumerate(sample_kormarc_records):
                if i >= 5000:
                    break
                record = parser.parse(record_data)
                isbn = f"978{8956789012 + i:010d}"
                category = ["general", "academic", "serial", "comic"][i % 4]
                records.append((isbn, category, record_data))
            parse_duration = time.time() - parse_start

            # Phase 3: Bulk insert
            insert_start = time.time()
            await bulk_insert_records(conn, records)
            insert_duration = time.time() - insert_start

            # Phase 4: Query performance
            query_start = time.time()
            for i in range(0, 1000, 100):
                isbn = f"978{8956789012 + i:010d}"
                record = await get_record_by_isbn(conn, isbn)
                assert record is not None
            query_duration = time.time() - query_start

            await conn.close()

            # Report results
            total_records = len(records)
            print(f"\n{'=' * 60}")
            print(f"Full Pipeline Benchmark ({total_records} records)")
            print(f"{'=' * 60}")
            print(f"Schema creation: {schema_duration:.3f}s")
            print(
                f"Parsing:         {parse_duration:.3f}s ({total_records / parse_duration:.2f} records/sec)"
            )
            print(
                f"Bulk insert:     {insert_duration:.3f}s ({total_records / insert_duration:.2f} records/sec)"
            )
            print(f"Queries (10):    {query_duration:.3f}s")
            print(f"{'=' * 60}")
            print(f"Total time:      {schema_duration + parse_duration + insert_duration:.3f}s")
            print(f"{'=' * 60}")

            # Performance assertions
            assert parse_duration < 30.0, "Parsing too slow"
            assert insert_duration < 60.0, "Insert too slow"

        finally:
            db_path.unlink(missing_ok=True)
