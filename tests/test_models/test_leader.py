"""
Test cases for Leader model

This module tests the Leader data model for KORMARC records.
"""

import pytest

from kormarc.exceptions import LeaderValidationError
from kormarc.models.leader import Leader


class TestLeaderParsing:
    """Test leader parsing from raw string."""

    def test_parse_complete_leader(self) -> None:
        """Test parsing a complete 24-character leader string."""
        # Example leader from KORMARC standard
        # Positions: 0-4:length, 5:status, 6:type, 7:level, 8:control, 9:encoding
        #            10:indicators, 11:subfields, 12-16:base_addr, 17:enc_level
        #            18:descrip, 19:multipart, 20-23:entry_map
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        assert leader.record_length == 714
        assert leader.record_status == "c"
        assert leader.type_of_record == "a"
        assert leader.bibliographic_level == "m"
        assert leader.control_type == " "
        assert leader.character_encoding == " "  # Position 9 is space
        assert leader.indicator_count == 2
        assert leader.subfield_code_count == 2
        assert leader.base_address == 205
        assert leader.encoding_level == " "
        assert leader.descriptive_cataloging == "a"
        assert leader.multipart_level == " "
        assert leader.entry_map == "4500"

    def test_leader_to_dict(self) -> None:
        """Test converting leader to dictionary representation."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        data = leader.to_dict()

        assert isinstance(data, dict)
        assert data["record_length"] == 714
        assert data["record_status"] == "c"
        assert data["type_of_record"] == "a"
        assert data["base_address"] == 205

    def test_leader_to_json(self) -> None:
        """Test converting leader to JSON string."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        json_str = leader.model_dump_json()

        assert isinstance(json_str, str)
        assert "record_length" in json_str
        assert "714" in json_str

    def test_create_leader_with_pydantic(self) -> None:
        """Test creating leader using Pydantic validation."""
        data = {
            "record_length": 714,
            "record_status": "c",
            "type_of_record": "a",
            "bibliographic_level": "m",
            "control_type": " ",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
        }

        leader = Leader(**data)
        assert leader.record_length == 714
        assert leader.record_status == "c"


class TestLeaderValidation:
    """Test leader validation rules."""

    def test_leader_must_be_24_characters(self) -> None:
        """Test that leader must be exactly 24 characters."""
        with pytest.raises(LeaderValidationError) as exc_info:
            Leader.from_string("short")

        assert "24 characters" in str(exc_info.value).lower()

    def test_leader_must_be_24_characters_long(self) -> None:
        """Test that leader longer than 24 characters raises error."""
        with pytest.raises(LeaderValidationError) as exc_info:
            Leader.from_string("00714cam  2200205 a 4500extra")

        assert "24 characters" in str(exc_info.value).lower()

    def test_invalid_record_status(self) -> None:
        """Test that invalid record status raises validation error."""
        leader_data = {
            "record_length": 714,
            "record_status": "z",  # Invalid status
            "type_of_record": "a",
            "bibliographic_level": "m",
            "control_type": " ",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
        }

        with pytest.raises(LeaderValidationError):
            Leader(**leader_data)

    def test_invalid_type_of_record(self) -> None:
        """Test that invalid type of record raises validation error."""
        leader_data = {
            "record_length": 714,
            "record_status": "c",
            "type_of_record": "z",  # Invalid type
            "bibliographic_level": "m",
            "control_type": " ",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
        }

        with pytest.raises(LeaderValidationError):
            Leader(**leader_data)

    def test_invalid_bibliographic_level(self) -> None:
        """Test that invalid bibliographic level raises validation error."""
        leader_data = {
            "record_length": 714,
            "record_status": "c",
            "type_of_record": "a",
            "bibliographic_level": "z",  # Invalid level
            "control_type": " ",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
        }

        with pytest.raises(LeaderValidationError):
            Leader(**leader_data)

    def test_extra_fields_forbidden(self) -> None:
        """Test that extra fields raise validation error."""
        from pydantic import ValidationError as PydanticValidationError

        leader_data = {
            "record_length": 714,
            "record_status": "c",
            "type_of_record": "a",
            "bibliographic_level": "m",
            "control_type": " ",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
            "unexpected_field": "should_fail",  # Extra field
        }

        with pytest.raises(PydanticValidationError):
            Leader(**leader_data)


class TestLeaderProperties:
    """Test leader computed properties and methods."""

    def test_leader_is_immutable(self) -> None:
        """Test that leader is immutable (frozen)."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        with pytest.raises(Exception):  # FrozenInstanceError
            leader.record_length = 999

    def test_leader_model_dump(self) -> None:
        """Test Pydantic model_dump method."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        dumped = leader.model_dump()

        assert dumped["record_length"] == 714
        assert dumped["base_address"] == 205
        assert len(dumped) == 13  # All 13 fields
