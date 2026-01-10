"""
KORMARC Parser Constants

This module defines constants used throughout the KORMARC parser.
"""

# Leader constants
LEADER_LENGTH = 24
RECORD_STATUS_VALUES = ["a", "c", "d", "n", "p"]
TYPE_OF_RECORD_VALUES = [
    "a", "c", "d", "e", "f", "g", "i", "j", "k", "m", "o", "p", "r", "t",
]
BIBLIOGRAPHIC_LEVEL_VALUES = ["a", "b", "c", "d", "i", "m", "s"]

# Field tag ranges
CONTROL_FIELD_START = "001"
CONTROL_FIELD_END = "009"
DATA_FIELD_START = "010"

# Indicator constants
INDICATOR_LENGTH = 1
INDICATOR_FILL_CHAR = " "

# Subfield constants
SUBFIELD_CODE_LENGTH = 1
SUBFIELD_DELIMITER = "\u001F"  # ASCII Unit Separator
FIELD_DELIMITER = "\u001E"  # ASCII Record Separator
