"""
Test cases for Field models (ControlField, DataField, Subfield)

This module tests the field data models for KORMARC records.
"""

import pytest
from pydantic import ValidationError as PydanticValidationError

from kormarc.models.fields import ControlField, DataField, Subfield


class TestSubfield:
    """Test Subfield model."""

    def test_create_subfield(self) -> None:
        """Test creating a subfield with code and data."""
        subfield = Subfield(code="a", data="Title data")

        assert subfield.code == "a"
        assert subfield.data == "Title data"

    def test_subfield_code_must_be_single_char(self) -> None:
        """Test that subfield code must be exactly one character."""
        with pytest.raises(PydanticValidationError):
            Subfield(code="ab", data="data")

    def test_subfield_is_immutable(self) -> None:
        """Test that subfield is immutable."""
        subfield = Subfield(code="a", data="data")

        with pytest.raises(Exception):  # FrozenInstanceError
            subfield.code = "b"

    def test_subfield_to_dict(self) -> None:
        """Test converting subfield to dictionary."""
        subfield = Subfield(code="a", data="Test data")

        data = subfield.model_dump()

        assert data["code"] == "a"
        assert data["data"] == "Test data"


class TestControlField:
    """Test ControlField model."""

    def test_create_control_field(self) -> None:
        """Test creating a control field."""
        field = ControlField(tag="001", data="12345")

        assert field.tag == "001"
        assert field.data == "12345"

    def test_control_field_tag_must_be_001_009(self) -> None:
        """Test that control field tags must be in 001-009 range."""
        # Valid tags
        for tag in ["001", "002", "003", "008", "009"]:
            field = ControlField(tag=tag, data="test")
            assert field.tag == tag

        # Invalid tags
        with pytest.raises(PydanticValidationError):
            ControlField(tag="010", data="test")

        with pytest.raises(PydanticValidationError):
            ControlField(tag="000", data="test")

    def test_control_field_is_immutable(self) -> None:
        """Test that control field is immutable."""
        field = ControlField(tag="001", data="12345")

        with pytest.raises(Exception):  # FrozenInstanceError
            field.data = "67890"


class TestDataField:
    """Test DataField model."""

    def test_create_data_field(self) -> None:
        """Test creating a data field with indicators and subfields."""
        subfields = [
            Subfield(code="a", data="Title"),
            Subfield(code="b", data="Subtitle"),
        ]

        field = DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)

        assert field.tag == "245"
        assert field.indicator1 == "1"
        assert field.indicator2 == "0"
        assert len(field.subfields) == 2
        assert field.subfields[0].code == "a"

    def test_data_field_tag_must_be_010_plus(self) -> None:
        """Test that data field tags must be >= 010."""
        # Valid tags
        for tag in ["010", "100", "245", "650", "999"]:
            field = DataField(tag=tag, indicator1=" ", indicator2=" ")
            assert field.tag == tag

        # Invalid tags
        with pytest.raises(PydanticValidationError):
            DataField(tag="009", indicator1=" ", indicator2=" ")

        with pytest.raises(PydanticValidationError):
            DataField(tag="001", indicator1=" ", indicator2=" ")

    def test_data_field_indicators_must_be_single_char(self) -> None:
        """Test that indicators must be exactly one character."""
        with pytest.raises(PydanticValidationError):
            DataField(tag="245", indicator1="", indicator2=" ")

        with pytest.raises(PydanticValidationError):
            DataField(tag="245", indicator1="ab", indicator2=" ")

    def test_data_field_default_empty_subfields(self) -> None:
        """Test that data field can be created without subfields."""
        field = DataField(tag="245", indicator1=" ", indicator2=" ")

        assert field.subfields == []

    def test_data_field_with_space_indicators(self) -> None:
        """Test that indicators can be spaces."""
        field = DataField(tag="245", indicator1=" ", indicator2=" ")

        assert field.indicator1 == " "
        assert field.indicator2 == " "

    def test_data_field_is_immutable(self) -> None:
        """Test that data field is immutable."""
        field = DataField(tag="245", indicator1="1", indicator2="0")

        with pytest.raises(Exception):  # FrozenInstanceError
            field.indicator1 = "2"

    def test_data_field_to_dict(self) -> None:
        """Test converting data field to dictionary."""
        subfields = [Subfield(code="a", data="Title")]
        field = DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)

        data = field.model_dump()

        assert data["tag"] == "245"
        assert data["indicator1"] == "1"
        assert data["indicator2"] == "0"
        assert len(data["subfields"]) == 1
