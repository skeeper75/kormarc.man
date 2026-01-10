"""
Leader model for KORMARC records.

The leader is a 24-character fixed-length field that contains
critical information about the record's structure and processing.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from kormarc.constants import (
    BIBLIOGRAPHIC_LEVEL_VALUES,
    LEADER_LENGTH,
    RECORD_STATUS_VALUES,
    TYPE_OF_RECORD_VALUES,
)
from kormarc.exceptions import LeaderValidationError


class Leader(BaseModel):
    """KORMARC Leader model.

    The leader contains 24 positions that define parameters for
    processing the record.

    Attributes:
        record_length: Length of the entire record (positions 00-04)
        record_status: Status of the record (position 05)
        type_of_record: Type of record (position 06)
        bibliographic_level: Bibliographic level (position 07)
        control_type: Type of control (position 08)
        character_encoding: Character encoding scheme (position 09)
        indicator_count: Number of indicator positions (position 10)
        subfield_code_count: Number of subfield code positions (position 11)
        base_address: Starting character position of the data portion (positions 12-16)
        encoding_level: Encoding level (position 17)
        descriptive_cataloging: Descriptive cataloging form (position 18)
        multipart_level: Multipart resource record level (position 19)
        entry_map: Entry map (positions 20-23)
    """

    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra="forbid",
        str_strip_whitespace=False,  # Disabled to preserve meaningful spaces
    )

    record_length: int = Field(..., ge=0, description="Length of the entire record")
    record_status: Literal["a", "c", "d", "n", "p"] = Field(..., description="Record status")
    type_of_record: Literal[
        "a", "c", "d", "e", "f", "g", "i", "j", "k", "m", "o", "p", "r", "t"
    ] = Field(..., description="Type of record")
    bibliographic_level: Literal["a", "b", "c", "d", "i", "m", "s"] = Field(
        ..., description="Bibliographic level"
    )
    control_type: str = Field(default=" ", description="Type of control")
    character_encoding: str = Field(..., description="Character encoding scheme")
    indicator_count: int = Field(default=2, ge=0, description="Number of indicators")
    subfield_code_count: int = Field(default=2, ge=0, description="Number of subfield codes")
    base_address: int = Field(..., ge=0, description="Base address of data")
    encoding_level: str = Field(default=" ", description="Encoding level")
    descriptive_cataloging: str = Field(default=" ", description="Descriptive cataloging")
    multipart_level: str = Field(default=" ", description="Multipart resource level")
    entry_map: str = Field(default="4500", description="Entry map")

    @field_validator("record_status", mode="before")
    @classmethod
    def validate_record_status(cls, v: str) -> str:
        """Validate record status value."""
        if v not in RECORD_STATUS_VALUES:
            raise LeaderValidationError(
                f"Invalid record_status '{v}'. Must be one of {RECORD_STATUS_VALUES}"
            )
        return v

    @field_validator("type_of_record", mode="before")
    @classmethod
    def validate_type_of_record(cls, v: str) -> str:
        """Validate type of record value."""
        if v not in TYPE_OF_RECORD_VALUES:
            raise LeaderValidationError(
                f"Invalid type_of_record '{v}'. Must be one of {TYPE_OF_RECORD_VALUES}"
            )
        return v

    @field_validator("bibliographic_level", mode="before")
    @classmethod
    def validate_bibliographic_level(cls, v: str) -> str:
        """Validate bibliographic level value."""
        if v not in BIBLIOGRAPHIC_LEVEL_VALUES:
            raise LeaderValidationError(
                f"Invalid bibliographic_level '{v}'. Must be one of {BIBLIOGRAPHIC_LEVEL_VALUES}"
            )
        return v

    @classmethod
    def from_string(cls, leader_str: str) -> "Leader":
        """Parse leader from 24-character string.

        Args:
            leader_str: 24-character leader string

        Returns:
            Leader model instance

        Raises:
            LeaderValidationError: If leader is not exactly 24 characters
        """
        if len(leader_str) != LEADER_LENGTH:
            raise LeaderValidationError(
                f"Leader must be exactly {LEADER_LENGTH} characters, "
                f"got {len(leader_str)} characters"
            )

        return cls(
            record_length=int(leader_str[0:5]),
            record_status=leader_str[5],
            type_of_record=leader_str[6],
            bibliographic_level=leader_str[7],
            control_type=leader_str[8],
            character_encoding=leader_str[9],
            indicator_count=int(leader_str[10]),
            subfield_code_count=int(leader_str[11]),
            base_address=int(leader_str[12:17]),
            encoding_level=leader_str[17],
            descriptive_cataloging=leader_str[18],
            multipart_level=leader_str[19],
            entry_map=leader_str[20:24],
        )

    def to_dict(self) -> dict:
        """Convert leader to dictionary representation.

        Returns:
            Dictionary containing all leader fields
        """
        return self.model_dump()

    def __str__(self) -> str:
        """Convert leader to 24-character string representation.

        Returns:
            24-character leader string
        """
        return (
            f"{self.record_length:05d}"
            f"{self.record_status}"
            f"{self.type_of_record}"
            f"{self.bibliographic_level}"
            f"{self.control_type}"
            f"{self.character_encoding}"
            f"{self.indicator_count}"
            f"{self.subfield_code_count}"
            f"{self.base_address:05d}"
            f"{self.encoding_level}"
            f"{self.descriptive_cataloging}"
            f"{self.multipart_level}"
            f"{self.entry_map}"
        )
