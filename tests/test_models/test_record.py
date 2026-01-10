"""
Test cases for Record model

This module tests the main Record data model for KORMARC records.
"""

import pytest

from kormarc.models.fields import ControlField, DataField, Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record


class TestRecordCreation:
    """Test Record model creation and initialization."""

    def test_create_record_with_leader_only(self) -> None:
        """Test creating a record with only a leader."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)

        assert record.leader == leader
        assert record.control_fields == []
        assert record.data_fields == []

    def test_create_record_with_control_fields(self) -> None:
        """Test creating a record with control fields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="008", data="200101s"),
        ]

        record = Record(leader=leader, control_fields=control_fields)

        assert len(record.control_fields) == 2
        assert record.control_fields[0].tag == "001"
        assert record.control_fields[1].tag == "008"

    def test_create_record_with_data_fields(self) -> None:
        """Test creating a record with data fields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [Subfield(code="a", data="Test Title")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, data_fields=data_fields)

        assert len(record.data_fields) == 1
        assert record.data_fields[0].tag == "245"

    def test_create_complete_record(self) -> None:
        """Test creating a complete record with all components."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [ControlField(tag="001", data="12345")]

        subfields = [Subfield(code="a", data="Test Title")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

        assert record.leader.record_length == 714
        assert len(record.control_fields) == 1
        assert len(record.data_fields) == 1


class TestRecordMethods:
    """Test Record model methods."""

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

    def test_record_to_json(self) -> None:
        """Test converting record to JSON string."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        json_str = record.to_json()

        assert isinstance(json_str, str)
        assert "leader" in json_str
        assert "record_length" in json_str

    def test_record_validate(self) -> None:
        """Test record validation method."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)
        assert record.validate() is True


class TestRecordImmutability:
    """Test Record model immutability."""

    def test_record_is_immutable(self) -> None:
        """Test that record is immutable."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)

        with pytest.raises(Exception):  # FrozenInstanceError
            record.control_fields = []

    def test_record_lists_are_immutable(self) -> None:
        """Test that record field lists cannot be reassigned."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        record = Record(leader=leader)

        with pytest.raises(Exception):  # FrozenInstanceError
            record.data_fields = [DataField(tag="245", indicator1=" ", indicator2=" ")]
