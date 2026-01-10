"""
Serialization tests for KORMARC records.

This module tests conversion between Record objects and various formats:
- JSON serialization and deserialization
- XML serialization
- Dictionary conversion
- Round-trip integrity
"""

import json

import pytest

from kormarc.models.fields import ControlField, DataField, Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record
from kormarc.parser.kormarc_parser import KORMARCParser
from tests.fixtures.kormarc_samples import (
    ROUNDTRIP_RECORD,
    VALID_BOOK_RECORD,
)


class TestJSONSerialization:
    """Test JSON serialization and deserialization."""

    def test_record_to_json_string(self) -> None:
        """Test converting record to JSON string."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        json_str = record.to_json()

        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_json_contains_all_fields(self) -> None:
        """Test that JSON contains all record fields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [ControlField(tag="001", data="12345")]
        subfields = [Subfield(code="a", data="Test Title")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)
        json_str = record.to_json()

        # Verify JSON contains expected keys
        data = json.loads(json_str)
        assert "leader" in data
        assert "control_fields" in data
        assert "data_fields" in data

        # Verify nested data
        assert data["leader"]["record_length"] == 714
        assert len(data["control_fields"]) == 1
        assert data["control_fields"][0]["tag"] == "001"
        assert len(data["data_fields"]) == 1
        assert data["data_fields"][0]["tag"] == "245"

    def test_json_preserves_unicode(self) -> None:
        """Test that JSON preserves Korean characters."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)
        json_str = record.to_json()

        # Verify Korean text is preserved
        assert "파이썬" in json_str
        assert "코딩" in json_str
        assert "클로드" in json_str

    def test_json_is_valid(self) -> None:
        """Test that generated JSON is valid and can be parsed."""
        parser = KORMARCParser()
        record = parser.parse(VALID_BOOK_RECORD)
        json_str = record.to_json()

        # Should not raise exception
        data = json.loads(json_str)
        assert isinstance(data, dict)

    def test_json_roundtrip(self) -> None:
        """Test round-trip: Record -> JSON -> Record."""
        parser = KORMARCParser()
        original_record = parser.parse(VALID_BOOK_RECORD)

        # Convert to JSON
        json_str = original_record.to_json()

        # Parse JSON back to dict
        data = json.loads(json_str)

        # Reconstruct record from dict
        reconstructed_record = Record.model_validate(data)

        # Verify leader is preserved
        assert reconstructed_record.leader.record_length == original_record.leader.record_length
        assert reconstructed_record.leader.record_status == original_record.leader.record_status

        # Verify control fields are preserved
        assert len(reconstructed_record.control_fields) == len(original_record.control_fields)
        for orig, recon in zip(original_record.control_fields, reconstructed_record.control_fields):
            assert recon.tag == orig.tag
            assert recon.data == orig.data

        # Verify data fields are preserved
        assert len(reconstructed_record.data_fields) == len(original_record.data_fields)
        for orig, recon in zip(original_record.data_fields, reconstructed_record.data_fields):
            assert recon.tag == orig.tag
            assert recon.indicator1 == orig.indicator1
            assert recon.indicator2 == orig.indicator2
            assert len(recon.subfields) == len(orig.subfields)


class TestDictConversion:
    """Test dictionary conversion."""

    def test_record_to_dict(self) -> None:
        """Test converting record to dictionary."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        data = record.to_dict()

        assert isinstance(data, dict)
        assert "leader" in data
        assert "control_fields" in data
        assert "data_fields" in data

    def test_dict_contains_complete_data(self) -> None:
        """Test that dictionary contains complete record data."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="008", data="200101s"),
        ]

        subfields = [
            Subfield(code="a", data="Title"),
            Subfield(code="b", data="Subtitle"),
        ]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)
        data = record.to_dict()

        # Verify structure
        assert data["leader"]["record_length"] == 714
        assert len(data["control_fields"]) == 2
        assert data["control_fields"][0]["tag"] == "001"
        assert data["control_fields"][0]["data"] == "12345"
        assert len(data["data_fields"]) == 1
        assert len(data["data_fields"][0]["subfields"]) == 2

    def test_dict_roundtrip(self) -> None:
        """Test round-trip: Record -> Dict -> Record."""
        parser = KORMARCParser()
        original_record = parser.parse(VALID_BOOK_RECORD)

        # Convert to dict
        data = original_record.to_dict()

        # Reconstruct record from dict
        reconstructed_record = Record.model_validate(data)

        # Verify all fields match
        assert reconstructed_record.leader == original_record.leader
        assert len(reconstructed_record.control_fields) == len(original_record.control_fields)
        assert len(reconstructed_record.data_fields) == len(original_record.data_fields)


class TestXMLSerialization:
    """Test XML serialization (MARCXML format)."""

    def test_xml_not_yet_implemented(self) -> None:
        """Test that XML conversion raises NotImplementedError."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)
        record = Record(leader=leader)

        with pytest.raises(NotImplementedError):
            record.to_xml()


class TestRoundTripIntegrity:
    """Test data integrity through round-trip conversions."""

    def test_complete_roundtrip_json(self) -> None:
        """Test complete round-trip through JSON preserves all data."""
        parser = KORMARCParser()
        original_record = parser.parse(ROUNDTRIP_RECORD)

        # Record -> JSON -> Dict -> Record
        json_str = original_record.to_json()
        intermediate_data = json.loads(json_str)
        final_record = Record.model_validate(intermediate_data)

        # Verify leader integrity
        assert final_record.leader == original_record.leader

        # Verify control fields integrity
        assert len(final_record.control_fields) == len(original_record.control_fields)
        for orig, final in zip(original_record.control_fields, final_record.control_fields):
            assert final.tag == orig.tag
            assert final.data == orig.data

        # Verify data fields integrity
        assert len(final_record.data_fields) == len(original_record.data_fields)
        for orig, final in zip(original_record.data_fields, final_record.data_fields):
            assert final.tag == orig.tag
            assert final.indicator1 == orig.indicator1
            assert final.indicator2 == orig.indicator2
            assert len(final.subfields) == len(orig.subfields)
            for orig_sub, final_sub in zip(orig.subfields, final.subfields):
                assert final_sub.code == orig_sub.code
                assert final_sub.data == orig_sub.data

    def test_complete_roundtrip_dict(self) -> None:
        """Test complete round-trip through dict preserves all data."""
        parser = KORMARCParser()
        original_record = parser.parse(ROUNDTRIP_RECORD)

        # Record -> Dict -> Record
        intermediate_dict = original_record.to_dict()
        final_record = Record.model_validate(intermediate_dict)

        # Verify complete data preservation
        assert final_record == original_record

    def test_korean_text_preservation(self) -> None:
        """Test that Korean text is preserved through round-trip."""
        parser = KORMARCParser()
        original_record = parser.parse(VALID_BOOK_RECORD)

        # Round-trip through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        final_record = Record.model_validate(data)

        # Find title field and verify Korean text
        title_field = next(f for f in final_record.data_fields if f.tag == "245")
        korean_found = any("파이썬" in sf.data for sf in title_field.subfields)
        assert korean_found, "Korean text should be preserved through round-trip"

    def test_special_characters_preservation(self) -> None:
        """Test that special characters are preserved through round-trip."""
        # Create record with special characters
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [Subfield(code="a", data="C++ & Java <Python>")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        original_record = Record(leader=leader, data_fields=data_fields)

        # Round-trip through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        final_record = Record.model_validate(data)

        # Verify special characters preserved
        assert "C++" in final_record.data_fields[0].subfields[0].data
        assert "&" in final_record.data_fields[0].subfields[0].data
        assert "<Python>" in final_record.data_fields[0].subfields[0].data


class TestSerializationEdgeCases:
    """Test serialization edge cases and error conditions."""

    def test_empty_record_serialization(self) -> None:
        """Test serializing a record with minimal data."""
        leader_str = "00314nam  2200121 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        json_str = record.to_json()

        # Should contain valid JSON
        data = json.loads(json_str)
        assert "leader" in data
        assert data["leader"]["record_length"] == 314

    def test_record_with_many_fields_serialization(self) -> None:
        """Test serializing a record with many fields."""
        parser = KORMARCParser()
        record = parser.parse(ROUNDTRIP_RECORD)

        json_str = record.to_json()

        # Verify all fields are present in JSON
        data = json.loads(json_str)
        assert len(data["control_fields"]) == len(record.control_fields)
        assert len(data["data_fields"]) == len(record.data_fields)

    def test_dict_immutability(self) -> None:
        """Test that modifying returned dict doesn't affect record."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        data = record.to_dict()

        # Modify dict
        data["leader"]["record_length"] = 999

        # Original record should be unchanged
        assert record.leader.record_length == 714
