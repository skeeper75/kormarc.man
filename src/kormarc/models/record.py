"""Record model for KORMARC records.

This module defines the main Record model that contains
a leader and a collection of fields.
"""

import xml.etree.ElementTree as ET

from pydantic import BaseModel, ConfigDict, Field

from kormarc.models.fields import ControlField, DataField
from kormarc.models.leader import Leader

# MARCXML namespace constant
MARCXML_NAMESPACE = "http://www.loc.gov/MARC21/slim"


class Record(BaseModel):
    """KORMARC Record model.

    A complete KORMARC record contains a leader and
    a collection of control fields and data fields.

    Attributes:
        leader: Leader (24-character fixed field)
        control_fields: List of control fields (tags 001-009)
        data_fields: List of data fields (tags 010-999)
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    leader: Leader
    control_fields: list[ControlField] = Field(default_factory=list)
    data_fields: list[DataField] = Field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert record to dictionary representation.

        Returns:
            Dictionary containing all record data
        """
        return self.model_dump()

    def to_json(self) -> str:
        """Convert record to JSON string.

        Returns:
            JSON string representation of the record
        """
        return self.model_dump_json()

    def to_xml(self) -> str:
        """Convert record to MARCXML format.

        Generates MARC21 XML compliant output following the standard schema:
        - Root element: <record xmlns="http://www.loc.gov/MARC21/slim">
        - Leader element: <leader> with 24-character leader string
        - Control fields: <controlfield tag="001"> for tags 001-009
        - Data fields: <datafield tag="245" ind1="1" ind2="0"> for tags 010-999
        - Subfields: <subfield code="a"> within data fields

        Special characters are automatically escaped by ElementTree.
        UTF-8 encoding is supported for Korean and international text.

        Returns:
            MARCXML string representation with XML declaration

        Examples:
            >>> leader = Leader.from_string("00714cam  2200205 a 4500")
            >>> record = Record(leader=leader)
            >>> xml = record.to_xml()
            >>> xml.startswith('<?xml version')
            True
        """
        # Create root record element with MARCXML namespace
        record_elem = ET.Element(f"{{{MARCXML_NAMESPACE}}}record")

        # Add leader element
        leader_elem = ET.SubElement(record_elem, f"{{{MARCXML_NAMESPACE}}}leader")
        leader_elem.text = str(self.leader)

        # Add control fields (tags 001-009)
        for control_field in self.control_fields:
            cf_elem = ET.SubElement(record_elem, f"{{{MARCXML_NAMESPACE}}}controlfield")
            cf_elem.set("tag", control_field.tag)
            cf_elem.text = control_field.data

        # Add data fields (tags 010-999) with subfields
        for data_field in self.data_fields:
            df_elem = ET.SubElement(record_elem, f"{{{MARCXML_NAMESPACE}}}datafield")
            df_elem.set("tag", data_field.tag)
            df_elem.set("ind1", data_field.indicator1)
            df_elem.set("ind2", data_field.indicator2)

            # Add subfields
            for subfield in data_field.subfields:
                sf_elem = ET.SubElement(df_elem, f"{{{MARCXML_NAMESPACE}}}subfield")
                sf_elem.set("code", subfield.code)
                sf_elem.text = subfield.data

        # Generate XML string with declaration
        return ET.tostring(record_elem, encoding="unicode", xml_declaration=True)

    def validate(self) -> bool:
        """Validate record structure and content.

        Returns:
            True if record is valid

        Raises:
            ValidationError: If record validation fails
        """
        # Pydantic validation is automatic
        return True
