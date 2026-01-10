"""
KORMARC Parser implementation.

This module provides the main parser for KORMARC records.

KORMARC format structure:
- Leader: 24-byte fixed-length field at the beginning
- Directory: Variable-length list of field entries (tag + length + position)
- Variable Fields: Control fields (001-009) and Data fields (010-999)

Directory entry format (12 bytes per entry):
- Tag: 3 characters
- Length: 4 characters (field data length)
- Position: 5 characters (starting position from base address)
"""

from kormarc.exceptions import ParseError
from kormarc.models.fields import ControlField, DataField, Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record


class KORMARCParser:
    """Parser for KORMARC format records."""

    def parse(self, data: str | bytes) -> Record:
        """Parse KORMARC record from string or bytes.

        Args:
            data: KORMARC record data in simplified text format
                  (one field per line: "TAG indicators|subfield_code data")

        Returns:
            Parsed Record object

        Raises:
            ParseError: If parsing fails
        """
        # Convert bytes to string if needed
        if isinstance(data, bytes):
            try:
                data = data.decode("utf-8")
            except UnicodeDecodeError as e:
                raise ParseError(f"Failed to decode data as UTF-8: {e}") from e

        # Strip leading/trailing whitespace and split into lines
        lines = [line.strip() for line in data.strip().splitlines() if line.strip()]

        if not lines:
            raise ParseError("Empty record: no data to parse")

        # First line is the leader
        leader_line = lines[0]
        try:
            leader = Leader.from_string(leader_line)
        except Exception as e:
            raise ParseError(f"Failed to parse leader: {e}") from e

        control_fields = []
        data_fields = []

        # Parse remaining lines as fields
        for line in lines[1:]:
            if not line:
                continue

            try:
                # Split line into tag and content
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    continue  # Skip malformed lines

                tag = parts[0]
                content = parts[1] if len(parts) > 1 else ""

                # Check if it's a control field (001-009) or data field (010+)
                if tag.isdigit() and int(tag) <= 9:
                    # Control field (001-009)
                    control_field = ControlField(tag=tag.zfill(3), data=content)
                    control_fields.append(control_field)
                else:
                    # Data field (010+) with subfields
                    indicators, subfields_data = self._parse_data_field_content(content)
                    data_field = DataField(
                        tag=tag.zfill(3),
                        indicator1=indicators[0] if len(indicators) > 0 else " ",
                        indicator2=indicators[1] if len(indicators) > 1 else " ",
                        subfields=subfields_data,
                    )
                    data_fields.append(data_field)

            except Exception as e:
                # Continue parsing other fields even if one fails
                raise ParseError(f"Failed to parse field {tag}: {e}") from e

        return Record(leader=leader, control_fields=control_fields, data_fields=data_fields)

    def _parse_data_field_content(self, content: str) -> tuple[list[str], list[Subfield]]:
        """Parse data field content into indicators and subfields.

        Args:
            content: Field content (e.g., "10  |aTitle|bSubtitle")

        Returns:
            Tuple of (indicators list, subfields list)
        """
        # Split indicators from content
        # Format: "10  |aTitle|bSubtitle" or "  |aTitle"
        indicators = []
        subfields = []

        # Find the delimiter (usually "|")
        if "|" in content:
            delimiter_pos = content.index("|")
            indicator_part = content[:delimiter_pos]
            subfield_part = content[delimiter_pos:]

            # Parse indicators
            for char in indicator_part:
                if char in "0123456789 ":
                    indicators.append(char)
                else:
                    break

            # Ensure we have exactly 2 indicators
            while len(indicators) < 2:
                indicators.append(" ")

            # Parse subfields
            # Split by '|' and process each subfield
            subfield_parts = subfield_part.split("|")
            for part in subfield_parts:
                part = part.strip()
                if len(part) >= 1:
                    code = part[0]
                    data = part[1:] if len(part) > 1 else ""
                    if code:  # Only add if code is not empty
                        subfields.append(Subfield(code=code, data=data))
        else:
            # No delimiter, treat entire content as data with default subfield 'a'
            indicators = [" ", " "]
            if content.strip():
                subfields.append(Subfield(code="a", data=content.strip()))

        return indicators[:2], subfields

    def parse_file(self, path: str) -> Record:
        """Parse KORMARC record from file.

        Args:
            path: Path to KORMARC file

        Returns:
            Parsed Record object

        Raises:
            ParseError: If parsing fails
            FileNotFoundError: If file does not exist
        """
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            return self.parse(content)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"KORMARC file not found: {path}") from e
        except Exception as e:
            raise ParseError(f"Failed to parse file {path}: {e}") from e
