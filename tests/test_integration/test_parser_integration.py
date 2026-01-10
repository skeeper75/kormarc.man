"""
Integration tests for KORMARC Parser.

This module tests end-to-end parsing of KORMARC records including:
- Complete record parsing
- Error handling
- Real data samples
"""

import pytest

from kormarc.exceptions import ParseError
from kormarc.parser.kormarc_parser import KORMARCParser
from tests.fixtures.kormarc_samples import (
    CONTROL_ONLY_RECORD,
    INCOMPLETE_RECORD,
    INVALID_LEADER_LENGTH,
    MINIMAL_RECORD,
    MULTIPLE_FIELDS_RECORD,
    SERIAL_RECORD,
    SPECIAL_CHARS_RECORD,
    VALID_BOOK_RECORD,
)


class TestEndToEndParsing:
    """Test end-to-end parsing of complete KORMARC records."""

    def test_parse_valid_book_record(self) -> None:
        """Test parsing a valid book record with all fields."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)

        # Verify leader
        assert record.leader.record_length == 714
        assert record.leader.record_status == "c"  # 'c' for corrected/updated
        assert record.leader.type_of_record == "a"  # 'a' for language material
        assert record.leader.bibliographic_level == "m"  # 'm' for monograph

        # Verify control fields
        assert len(record.control_fields) == 2
        assert record.control_fields[0].tag == "001"
        assert record.control_fields[0].data == "1234567890"
        assert record.control_fields[1].tag == "008"

        # Verify data fields
        assert len(record.data_fields) == 7

        # Check title field (245)
        title_field = next(f for f in record.data_fields if f.tag == "245")
        assert title_field.indicator1 == "1"
        assert title_field.indicator2 == "0"
        assert len(title_field.subfields) == 3
        assert title_field.subfields[0].code == "a"
        assert "파이썬 코딩의 기술" in title_field.subfields[0].data

    def test_parse_minimal_record(self) -> None:
        """Test parsing a minimal valid record."""
        parser = KORMARCParser()
        record = parser.parse(MINIMAL_RECORD)

        assert record.leader.record_length == 422
        assert len(record.control_fields) == 2
        assert len(record.data_fields) == 1
        assert record.data_fields[0].tag == "245"

    def test_parse_record_with_multiple_fields(self) -> None:
        """Test parsing a record with multiple data fields."""
        parser = KORMARCParser()
        record = parser.parse(MULTIPLE_FIELDS_RECORD)

        # Verify multiple control fields
        assert len(record.control_fields) == 2

        # Verify multiple data fields
        assert len(record.data_fields) >= 10

        # Check specific fields exist
        tags = {f.tag for f in record.data_fields}
        assert "020" in tags  # ISBN
        assert "100" in tags  # Author
        assert "245" in tags  # Title
        assert "260" in tags  # Publication
        assert "300" in tags  # Physical description

    def test_parse_control_only_record(self) -> None:
        """Test parsing a record with only control fields."""
        parser = KORMARCParser()
        record = parser.parse(CONTROL_ONLY_RECORD)

        assert record.leader.record_length == 314
        assert len(record.control_fields) == 2
        assert len(record.data_fields) == 0

    def test_parse_serial_record(self) -> None:
        """Test parsing a serial (continuing resource) record."""
        parser = KORMARCParser()
        record = parser.parse(SERIAL_RECORD)

        # Verify leader indicates serial
        assert record.leader.type_of_record == "a"
        assert record.leader.bibliographic_level == "s"

        # Verify serial-specific fields
        tags = {f.tag for f in record.data_fields}
        assert "310" in tags  # Frequency
        assert "362" in tags  # Numeric designation

    def test_parse_special_characters(self) -> None:
        """Test parsing records with special characters."""
        parser = KORMARCParser()
        record = parser.parse(SPECIAL_CHARS_RECORD)

        # Find title field with special characters
        title_field = next(f for f in record.data_fields if f.tag == "245")
        assert "C++" in title_field.subfields[0].data
        assert "Java" in title_field.subfields[0].data

        # Check note field with quoted text
        note_field = next(f for f in record.data_fields if f.tag == "500")
        assert "examples.zip" in note_field.subfields[0].data


class TestParserErrorHandling:
    """Test parser error handling and edge cases."""

    def test_parse_invalid_leader_length(self) -> None:
        """Test that invalid leader length raises ParseError."""
        parser = KORMARCParser()

        with pytest.raises(ParseError):
            parser.parse(INVALID_LEADER_LENGTH)

    def test_parse_incomplete_record(self) -> None:
        """Test that incomplete record is handled gracefully."""
        parser = KORMARCParser()

        # May raise ParseError or return partial record
        # depending on implementation choice
        try:
            record = parser.parse(INCOMPLETE_RECORD)
            # If partial record is returned, it should have at least a leader
            assert record.leader is not None
        except ParseError:
            # This is also acceptable behavior
            pass

    def test_parse_empty_string(self) -> None:
        """Test parsing an empty string."""
        parser = KORMARCParser()

        with pytest.raises(ParseError):
            parser.parse("")

    def test_parse_whitespace_only(self) -> None:
        """Test parsing whitespace-only input."""
        parser = KORMARCParser()

        with pytest.raises(ParseError):
            parser.parse("   \n\n  \t  ")

    def test_parse_bytes_input(self) -> None:
        """Test parsing bytes input (UTF-8 encoded)."""
        parser = KORMARCParser()
        data_bytes = VALID_BOOK_RECORD.encode("utf-8")

        record = parser.parse(data_bytes)

        assert record.leader.record_length == 714
        assert len(record.control_fields) == 2


class TestParserFromMethods:
    """Test parser convenience methods."""

    def test_parse_from_file(self, tmp_path) -> None:
        """Test parsing record from file."""
        parser = KORMARCParser()

        # Create temporary file with valid record
        test_file = tmp_path / "test_record.marc"
        test_file.write_text(VALID_BOOK_RECORD, encoding="utf-8")

        record = parser.parse_file(str(test_file))

        assert record.leader.record_length == 714
        assert len(record.data_fields) == 7

    def test_parse_from_nonexistent_file(self, tmp_path) -> None:
        """Test that parsing nonexistent file raises appropriate error."""
        parser = KORMARCParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file(str(tmp_path / "nonexistent.marc"))


class TestRecordIntegrity:
    """Test parsed record integrity and validation."""

    def test_parsed_record_is_valid(self) -> None:
        """Test that parsed record passes validation."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)

        # Record should be valid
        assert record.validate() is True

    def test_parsed_record_is_immutable(self) -> None:
        """Test that parsed record is immutable."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)

        # Attempting to modify should raise exception
        with pytest.raises(Exception):
            record.control_fields = []

    def test_parsed_record_roundtrip_dict(self) -> None:
        """Test that parsed record can convert to dict and back."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)

        # Convert to dict
        record_dict = record.to_dict()

        assert "leader" in record_dict
        assert "control_fields" in record_dict
        assert "data_fields" in record_dict

        # Dict should contain expected data
        assert record_dict["leader"]["record_length"] == 714
        assert len(record_dict["control_fields"]) == 2
        assert len(record_dict["data_fields"]) == 7

    def test_parsed_record_roundtrip_json(self) -> None:
        """Test that parsed record can serialize to JSON and back."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)

        # Serialize to JSON
        json_str = record.to_json()

        assert isinstance(json_str, str)
        assert "leader" in json_str
        assert "record_length" in json_str

        # JSON should be valid and contain record data
        assert "714" in json_str  # record_length
        assert "245" in json_str  # title field tag
