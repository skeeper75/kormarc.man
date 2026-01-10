"""
Field models for KORMARC records.

This module defines ControlField, DataField, and Subfield models.
"""

from pydantic import BaseModel, ConfigDict, Field


class Subfield(BaseModel):
    """KORMARC Subfield model.

    A subfield contains a single piece of data within a data field.
    Each subfield has a code (single character) and data.

    Attributes:
        code: Subfield code (single character, e.g., 'a', 'b', 'c')
        data: Subfield data content
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,  # Preserve meaningful spaces
    )

    code: str = Field(..., min_length=1, max_length=1, description="Subfield code")
    data: str = Field(..., description="Subfield data")


class ControlField(BaseModel):
    """KORMARC Control Field model.

    Control fields (tags 001-009) contain data that is coded
    and not broken down into subfields.

    Attributes:
        tag: 3-character field tag (001-009)
        data: Field data content
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,  # Preserve meaningful spaces
    )

    tag: str = Field(..., pattern=r"^00[1-9]$", description="Field tag")
    data: str = Field(..., description="Control field data")


class DataField(BaseModel):
    """KORMARC Data Field model.

    Data fields (tags 010-999) contain data organized into
    subfields with two indicators.

    Attributes:
        tag: 3-character field tag (010-999)
        indicator1: First indicator (1 character or space)
        indicator2: Second indicator (1 character or space)
        subfields: List of subfields in this data field
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,  # Preserve meaningful spaces
    )

    tag: str = Field(..., pattern=r"^(0[1-9][0-9]|[1-9][0-9]{2})$", description="Field tag")
    indicator1: str = Field(..., min_length=1, max_length=1, description="First indicator")
    indicator2: str = Field(..., min_length=1, max_length=1, description="Second indicator")
    subfields: list[Subfield] = Field(default_factory=list, description="List of subfields")
