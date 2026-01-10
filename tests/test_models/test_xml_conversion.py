"""
Test cases for Record.to_xml() MARCXML conversion.

This module tests MARCXML generation following the MARC21 XML standard.
"""

from xml.etree import ElementTree as ET

from kormarc.models.fields import ControlField, DataField, Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record


class TestXMLConversionBasic:
    """Test basic XML conversion functionality."""

    def test_to_xml_with_leader_only(self) -> None:
        """Test XML conversion with only leader."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)
        record = Record(leader=leader)

        xml_str = record.to_xml()

        # Verify XML is well-formed
        root = ET.fromstring(xml_str)

        # Check namespace
        assert root.tag == "{http://www.loc.gov/MARC21/slim}record"

        # Check leader element
        leader_elem = root.find("{http://www.loc.gov/MARC21/slim}leader")
        assert leader_elem is not None
        assert leader_elem.text == leader_str

    def test_to_xml_with_control_fields(self) -> None:
        """Test XML conversion with control fields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="008", data="200101s"),
        ]

        record = Record(leader=leader, control_fields=control_fields)
        xml_str = record.to_xml()

        root = ET.fromstring(xml_str)

        # Check controlfield elements
        controlfields = root.findall("{http://www.loc.gov/MARC21/slim}controlfield")
        assert len(controlfields) == 2

        # Check tag attributes
        tags = [cf.get("tag") for cf in controlfields]
        assert "001" in tags
        assert "008" in tags

        # Check data content
        assert controlfields[0].text == "12345"
        assert controlfields[1].text == "200101s"

    def test_to_xml_with_data_fields(self) -> None:
        """Test XML conversion with data fields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [Subfield(code="a", data="Test Title")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, data_fields=data_fields)
        xml_str = record.to_xml()

        root = ET.fromstring(xml_str)

        # Check datafield element
        datafields = root.findall("{http://www.loc.gov/MARC21/slim}datafield")
        assert len(datafields) == 1

        df = datafields[0]
        assert df.get("tag") == "245"
        assert df.get("ind1") == "1"
        assert df.get("ind2") == "0"

        # Check subfield elements
        subfields = df.findall("{http://www.loc.gov/MARC21/slim}subfield")
        assert len(subfields) == 1
        assert subfields[0].get("code") == "a"
        assert subfields[0].text == "Test Title"


class TestXMLConversionSpecialCharacters:
    """Test XML conversion with special characters."""

    def test_xml_escaping_special_chars(self) -> None:
        """Test proper XML escaping of special characters."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        # Data with special XML characters
        control_fields = [ControlField(tag="001", data="<>&\"'")]
        subfields = [Subfield(code="a", data="Title: A & B <C>")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, control_fields=control_fields, data_fields=data_fields)
        xml_str = record.to_xml()

        # Verify XML is well-formed (parsing will fail if not properly escaped)
        root = ET.fromstring(xml_str)

        # Check that special characters are properly escaped
        controlfield = root.find("{http://www.loc.gov/MARC21/slim}controlfield")
        assert controlfield.text == "<>&\"'"

        subfield = root.find(".//{http://www.loc.gov/MARC21/slim}subfield")
        assert subfield.text == "Title: A & B <C>"

    def test_xml_korean_characters(self) -> None:
        """Test XML conversion with Korean characters (UTF-8)."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [Subfield(code="a", data="한국어 도서 제목")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, data_fields=data_fields)
        xml_str = record.to_xml()

        # Verify XML is well-formed with Korean text
        root = ET.fromstring(xml_str)

        subfield = root.find(".//{http://www.loc.gov/MARC21/slim}subfield")
        assert subfield.text == "한국어 도서 제목"


class TestXMLConversionCompleteRecord:
    """Test XML conversion with complete records."""

    def test_complete_record_xml_structure(self) -> None:
        """Test XML structure of a complete record."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [
            ControlField(tag="001", data="12345"),
            ControlField(tag="008", data="200101s2001    enk a    000 0 eng d"),
        ]

        subfields_title = [
            Subfield(code="a", data="Test title"),
            Subfield(code="b", data="Subtitle"),
        ]
        subfields_author = [Subfield(code="a", data="Author, Name")]

        data_fields = [
            DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields_title),
            DataField(tag="100", indicator1="1", indicator2=" ", subfields=subfields_author),
        ]

        record = Record(
            leader=leader,
            control_fields=control_fields,
            data_fields=data_fields,
        )

        xml_str = record.to_xml()
        root = ET.fromstring(xml_str)

        # Verify structure
        assert root.tag == "{http://www.loc.gov/MARC21/slim}record"

        # Check leader
        leader_elem = root.find("{http://www.loc.gov/MARC21/slim}leader")
        assert leader_elem is not None

        # Check control fields
        controlfields = root.findall("{http://www.loc.gov/MARC21/slim}controlfield")
        assert len(controlfields) == 2

        # Check data fields
        datafields = root.findall("{http://www.loc.gov/MARC21/slim}datafield")
        assert len(datafields) == 2

        # Verify first datafield (245)
        df_245 = datafields[0]
        assert df_245.get("tag") == "245"
        assert df_245.get("ind1") == "1"
        assert df_245.get("ind2") == "0"

        subfields_245 = df_245.findall("{http://www.loc.gov/MARC21/slim}subfield")
        assert len(subfields_245) == 2
        assert subfields_245[0].get("code") == "a"
        assert subfields_245[1].get("code") == "b"

    def test_xml_output_formatting(self) -> None:
        """Test XML output has proper formatting."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        control_fields = [ControlField(tag="001", data="12345")]
        subfields = [Subfield(code="a", data="Test")]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(
            leader=leader,
            control_fields=control_fields,
            data_fields=data_fields,
        )

        xml_str = record.to_xml()

        # Check for XML declaration
        assert xml_str.startswith("<?xml version")

        # Check for proper namespace
        assert "http://www.loc.gov/MARC21/slim" in xml_str

        # Verify it's valid XML
        ET.fromstring(xml_str)


class TestXMLConversionEdgeCases:
    """Test XML conversion edge cases."""

    def test_empty_data_fields(self) -> None:
        """Test XML conversion with data fields that have no subfields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        data_fields = [DataField(tag="245", indicator1=" ", indicator2=" ")]
        record = Record(leader=leader, data_fields=data_fields)

        xml_str = record.to_xml()
        root = ET.fromstring(xml_str)

        datafields = root.findall("{http://www.loc.gov/MARC21/slim}datafield")
        assert len(datafields) == 1

        subfields = datafields[0].findall("{http://www.loc.gov/MARC21/slim}subfield")
        assert len(subfields) == 0

    def test_space_indicators(self) -> None:
        """Test XML conversion with space indicators."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [Subfield(code="a", data="Test")]
        data_fields = [DataField(tag="245", indicator1=" ", indicator2=" ", subfields=subfields)]

        record = Record(leader=leader, data_fields=data_fields)
        xml_str = record.to_xml()

        root = ET.fromstring(xml_str)
        df = root.find("{http://www.loc.gov/MARC21/slim}datafield")

        # Check that space indicators are preserved
        assert df.get("ind1") == " "
        assert df.get("ind2") == " "

    def test_multiple_subfields(self) -> None:
        """Test XML conversion with multiple subfields."""
        leader_str = "00714cam  2200205 a 4500"
        leader = Leader.from_string(leader_str)

        subfields = [
            Subfield(code="a", data="First"),
            Subfield(code="b", data="Second"),
            Subfield(code="c", data="Third"),
        ]
        data_fields = [DataField(tag="245", indicator1="1", indicator2="0", subfields=subfields)]

        record = Record(leader=leader, data_fields=data_fields)
        xml_str = record.to_xml()

        root = ET.fromstring(xml_str)
        subfield_elems = root.findall(".//{http://www.loc.gov/MARC21/slim}subfield")

        assert len(subfield_elems) == 3
        assert subfield_elems[0].get("code") == "a"
        assert subfield_elems[1].get("code") == "b"
        assert subfield_elems[2].get("code") == "c"
