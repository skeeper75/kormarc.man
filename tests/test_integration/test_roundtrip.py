"""
Round-trip integrity tests for KORMARC records.

This module tests that records maintain data integrity through:
- Parse -> Serialize -> Parse cycle
- Multiple format conversions
- Data preservation across transformations
"""

import json

import pytest

from kormarc.models.record import Record
from kormarc.parser.kormarc_parser import KORMARCParser
from tests.fixtures.kormarc_samples import (
    CONTROL_ONLY_RECORD,
    MINIMAL_RECORD,
    MULTIPLE_FIELDS_RECORD,
    ROUNDTRIP_RECORD,
    SERIAL_RECORD,
    SPECIAL_CHARS_RECORD,
    VALID_BOOK_RECORD,
)


class TestParseSerializeParse:
    """Test parse -> serialize -> parse cycle."""

    def test_parse_json_parse_cycle(self) -> None:
        """Test parse -> JSON -> parse cycle preserves data."""
        parser = KORMARCParser()

        # Original parse
        original_record = parser.parse(VALID_BOOK_RECORD)

        # Serialize to JSON
        json_str = original_record.to_json()

        # Parse JSON back to Record
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify data preservation
        assert reconstructed_record.leader == original_record.leader

        # Compare control fields
        assert len(reconstructed_record.control_fields) == len(original_record.control_fields)
        for orig, recon in zip(original_record.control_fields, reconstructed_record.control_fields):
            assert recon.tag == orig.tag, f"Control field tag mismatch: {recon.tag} != {orig.tag}"
            assert recon.data == orig.data, f"Control field data mismatch for tag {orig.tag}"

        # Compare data fields
        assert len(reconstructed_record.data_fields) == len(original_record.data_fields)
        for orig, recon in zip(original_record.data_fields, reconstructed_record.data_fields):
            assert recon.tag == orig.tag, "Data field tag mismatch"
            assert recon.indicator1 == orig.indicator1, f"Indicator1 mismatch for field {orig.tag}"
            assert recon.indicator2 == orig.indicator2, f"Indicator2 mismatch for field {orig.tag}"

            # Compare subfields
            assert len(recon.subfields) == len(orig.subfields), (
                f"Subfield count mismatch for field {orig.tag}"
            )
            for orig_sub, recon_sub in zip(orig.subfields, recon.subfields):
                assert recon_sub.code == orig_sub.code, "Subfield code mismatch"
                assert recon_sub.data == orig_sub.data, (
                    f"Subfield data mismatch for code {orig_sub.code}"
                )

    def test_parse_dict_parse_cycle(self) -> None:
        """Test parse -> dict -> parse cycle preserves data."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)

        # Convert to dict and back
        record_dict = original_record.to_dict()
        reconstructed_record = Record.model_validate(record_dict)

        # Verify complete equality
        assert reconstructed_record == original_record

    def test_multiple_cycles(self) -> None:
        """Test multiple parse-serialize cycles."""
        parser = KORMARCParser()

        # First cycle
        record1 = parser.parse(VALID_BOOK_RECORD)
        json1 = record1.to_json()

        # Second cycle
        data = json.loads(json1)
        record2 = Record.model_validate(data)
        json2 = record2.to_json()

        # Third cycle
        data2 = json.loads(json2)
        record3 = Record.model_validate(data2)

        # All records should be equivalent
        assert record2.leader == record1.leader
        assert record3.leader == record2.leader
        assert len(record3.data_fields) == len(record1.data_fields)


class TestDataIntegrity:
    """Test data integrity across transformations."""

    def test_korean_text_integrity(self) -> None:
        """Test that Korean text is preserved through transformations."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)

        # Extract original Korean text from title field
        title_field = next(f for f in original_record.data_fields if f.tag == "245")
        original_korean = [
            sf.data for sf in title_field.subfields if any(c in sf.data for c in "가나다라마바사")
        ]

        # Transform through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify Korean text preserved
        title_field_recon = next(f for f in reconstructed_record.data_fields if f.tag == "245")
        reconstructed_korean = [
            sf.data
            for sf in title_field_recon.subfields
            if any(c in sf.data for c in "가나다라마바사")
        ]

        assert len(original_korean) == len(reconstructed_korean)
        for orig, recon in zip(original_korean, reconstructed_korean):
            assert orig == recon

    def test_special_characters_integrity(self) -> None:
        """Test that special characters are preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(SPECIAL_CHARS_RECORD)

        # Find fields with special characters
        special_char_fields = []
        for field in original_record.data_fields:
            for subfield in field.subfields:
                if any(c in subfield.data for c in ["&", "<", ">", '"', "'"]):
                    special_char_fields.append((field.tag, subfield.code, subfield.data))

        # Transform through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify special characters preserved
        for tag, code, data in special_char_fields:
            field = next(f for f in reconstructed_record.data_fields if f.tag == tag)
            subfield = next(sf for sf in field.subfields if sf.code == code)
            assert data in subfield.data, f"Special character data not preserved for {tag}${code}"

    def test_numeric_data_integrity(self) -> None:
        """Test that numeric data is preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)

        # Extract numeric values from leader
        original_length = original_record.leader.record_length
        original_base_address = original_record.leader.base_address

        # Transform through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify numeric data preserved
        assert reconstructed_record.leader.record_length == original_length
        assert reconstructed_record.leader.base_address == original_base_address

    def test_indicator_integrity(self) -> None:
        """Test that indicator values (including spaces) are preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(MULTIPLE_FIELDS_RECORD)

        # Collect all indicators
        original_indicators = [
            (f.tag, f.indicator1, f.indicator2) for f in original_record.data_fields
        ]

        # Transform through JSON
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify indicators preserved
        for tag, ind1, ind2 in original_indicators:
            field = next(f for f in reconstructed_record.data_fields if f.tag == tag)
            assert field.indicator1 == ind1, f"Indicator1 not preserved for field {tag}"
            assert field.indicator2 == ind2, f"Indicator2 not preserved for field {tag}"


class TestFieldOrderIntegrity:
    """Test that field order is preserved through transformations."""

    def test_control_field_order_preserved(self) -> None:
        """Test that control field order is preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(MULTIPLE_FIELDS_RECORD)
        original_order = [f.tag for f in original_record.control_fields]

        # Transform
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        reconstructed_order = [f.tag for f in reconstructed_record.control_fields]

        assert original_order == reconstructed_order

    def test_data_field_order_preserved(self) -> None:
        """Test that data field order is preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)
        original_order = [f.tag for f in original_record.data_fields]

        # Transform
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        reconstructed_order = [f.tag for f in reconstructed_record.data_fields]

        assert original_order == reconstructed_order

    def test_subfield_order_preserved(self) -> None:
        """Test that subfield order within fields is preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)

        # Transform
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Check subfield order for each field
        for orig_field, recon_field in zip(
            original_record.data_fields, reconstructed_record.data_fields
        ):
            orig_order = [sf.code for sf in orig_field.subfields]
            recon_order = [sf.code for sf in recon_field.subfields]
            assert orig_order == recon_order, f"Subfield order mismatch for field {orig_field.tag}"


class TestMultipleRecordTypes:
    """Test round-trip for various record types."""

    @pytest.mark.parametrize(
        "record_data",
        [
            VALID_BOOK_RECORD,
            MINIMAL_RECORD,
            MULTIPLE_FIELDS_RECORD,
            SERIAL_RECORD,
            CONTROL_ONLY_RECORD,
            SPECIAL_CHARS_RECORD,
            ROUNDTRIP_RECORD,
        ],
    )
    def test_roundtrip_for_various_records(self, record_data: str) -> None:
        """Test round-trip preservation for various record types."""
        parser = KORMARCParser()

        # Parse original
        original_record = parser.parse(record_data)

        # Transform to JSON and back
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Verify leader preserved
        assert reconstructed_record.leader == original_record.leader

        # Verify control fields count preserved
        assert len(reconstructed_record.control_fields) == len(original_record.control_fields)

        # Verify data fields count preserved
        assert len(reconstructed_record.data_fields) == len(original_record.data_fields)


class TestWhitespaceHandling:
    """Test whitespace handling through transformations."""

    def test_trailing_whitespace_preserved(self) -> None:
        """Test that trailing whitespace in fields is preserved."""
        leader_str = "00714cam  2200205 a 4500"
        from kormarc.models.fields import DataField, Subfield
        from kormarc.models.leader import Leader

        leader = Leader.from_string(leader_str)

        # Create field with intentional trailing whitespace
        subfields = [Subfield(code="a", data="Title   "), Subfield(code="b", data="Subtitle ")]
        data_fields = [DataField(tag="245", indicator1=" ", indicator2=" ", subfields=subfields)]

        original_record = Record(leader=leader, data_fields=data_fields)

        # Transform
        json_str = original_record.to_json()
        data = json.loads(json_str)
        from kormarc.models.record import Record as RecordModel

        reconstructed_record = RecordModel.model_validate(data)

        # Verify whitespace preserved
        assert reconstructed_record.data_fields[0].subfields[0].data == "Title   "
        assert reconstructed_record.data_fields[0].subfields[1].data == "Subtitle "

    def test_internal_spaces_preserved(self) -> None:
        """Test that internal spaces are preserved."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)

        # Find field with internal spaces (e.g., 245 $a "파이썬 코딩의 기술 /")
        title_field = next(f for f in original_record.data_fields if f.tag == "245")
        original_with_spaces = [
            sf.data for sf in title_field.subfields if "  " in sf.data or " " in sf.data
        ]

        # Transform
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        title_field_recon = next(f for f in reconstructed_record.data_fields if f.tag == "245")
        reconstructed_with_spaces = [
            sf.data for sf in title_field_recon.subfields if "  " in sf.data or " " in sf.data
        ]

        assert len(original_with_spaces) == len(reconstructed_with_spaces)


class TestImmutabilityAfterRoundTrip:
    """Test that reconstructed records maintain immutability."""

    def test_reconstructed_record_is_immutable(self) -> None:
        """Test that records reconstructed after round-trip are immutable."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Attempting to modify should raise exception
        with pytest.raises(Exception):
            reconstructed_record.control_fields = []

    def test_reconstructed_fields_are_immutable(self) -> None:
        """Test that fields in reconstructed records are immutable."""
        parser = KORMARCParser()

        original_record = parser.parse(VALID_BOOK_RECORD)
        json_str = original_record.to_json()
        data = json.loads(json_str)
        reconstructed_record = Record.model_validate(data)

        # Attempting to modify field lists should raise exception
        with pytest.raises(Exception):
            reconstructed_record.data_fields = []
