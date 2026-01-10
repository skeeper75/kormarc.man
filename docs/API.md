# KORMARC Parser API Documentation

Version 0.1.0

Complete API reference for KORMARC Parser library.

## Table of Contents

- [Module: kormarc](#module-kormarc)
- [Module: kormarc.exceptions](#module-kormarcexceptions)
- [Module: kormarc.models](#module-kormarcmodels)
- [Module: kormarc.parser](#module-kormarcparser)

---

## Module: kormarc

Main module providing all public exports.

### Exports

```python
from kormarc import (
    # Models
    Leader,
    ControlField,
    DataField,
    Subfield,
    Record,

    # Parser
    KORMARCParser,

    # Exceptions
    KORMARCError,
    ParseError,
    LeaderParseError,
    FieldParseError,
    SubfieldParseError,
    ValidationError,
    LeaderValidationError,
    FieldValidationError,
    ConversionError,
    JSONConversionError,
    XMLConversionError,
    EncodingError,
)
```

---

## Module: kormarc.exceptions

Exception hierarchy for KORMARC parsing errors.

### KORMARCError

**Base exception** for all KORMARC-related errors.

#### Attributes

- `message: str` - Error message
- `context: dict` - Additional context information

#### Example

```python
from kormarc.exceptions import KORMARCError

try:
    # parsing code
except KORMARCError as e:
    print(f"Error: {e.message}")
    print(f"Context: {e.context}")
```

### ParseError

Raised when parsing fails due to malformed input.

**Inherits:** `KORMARCError`

### LeaderParseError

Raised when leader parsing fails.

**Inherits:** `ParseError`

### FieldParseError

Raised when field parsing fails.

**Inherits:** `ParseError`

### SubfieldParseError

Raised when subfield parsing fails.

**Inherits:** `ParseError`

### ValidationError

Raised when data validation fails.

**Inherits:** `KORMARCError`

### LeaderValidationError

Raised when leader validation fails.

**Inherits:** `ValidationError`

### FieldValidationError

Raised when field validation fails.

**Inherits:** `ValidationError`

### ConversionError

Raised when format conversion fails.

**Inherits:** `KORMARCError`

### JSONConversionError

Raised when JSON conversion fails.

**Inherits:** `ConversionError`

### XMLConversionError

Raised when XML conversion fails.

**Inherits:** `ConversionError`

### EncodingError

Raised when encoding issues occur.

**Inherits:** `KORMARCError`

---

## Module: kormarc.models

Data models for KORMARC records.

### Leader

**Bases:** `pydantic.BaseModel`

Leader field (24-character fixed field) for KORMARC records.

#### Class Methods

##### `from_string(data: str) -> Leader`

Create Leader from 24-character string.

**Parameters:**
- `data` (str): 24-character leader string

**Returns:**
- `Leader`: Leader instance

**Raises:**
- `LeaderParseError`: If string format is invalid

**Example:**
```python
from kormarc.models import Leader

leader = Leader.from_string("00714cam  2200205 a 4500")
print(leader.record_length)  # 714
print(leader.record_status)  # 'c'
```

#### Attributes

| Attribute | Type | Description | Position |
|-----------|------|-------------|----------|
| `record_length` | int | Total record length | 0-4 |
| `record_status` | str | Record status code | 5 |
| `type_of_record` | str | Type of record | 6 |
| `bibliographic_level` | str | Bibliographic level | 7 |
| `type_of_control` | str | Type of control | 8 |
| `character_coding_scheme` | str | Character coding scheme | 9 |
| `indicator_count` | int | Number of character positions in indicators | 10 |
| `subfield_code_count` | int | Number of character positions in subfield code | 11 |
| `base_address` | int | Base address of data | 12-16 |
| `encoding_level` | str | Encoding level | 17 |
| `descriptive_cataloging_form` | str | Descriptive cataloging form | 18 |
| `multipart_resource_record_level` | str | Multipart resource record level | 19 |
| `length_of_length_of_field` | int | Length of length-of-field portion | 20 |
| `starting_character_position` | int | Starting character position | 21 |
| `length_of_implementation` | int | Length of implementation-defined portion | 22 |

---

### ControlField

**Bases:** `pydantic.BaseModel`

Control field for tags 001-009.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tag` | str | Field tag (001-009), zero-padded to 3 chars |
| `data` | str | Field data content |

#### Example

```python
from kormarc.models import ControlField

# Create control field
cf = ControlField(tag="001", data="12345")
print(cf.tag)  # '001'
print(cf.data)  # '12345'
```

---

### DataField

**Bases:** `pydantic.BaseModel`

Data field for tags 010-999 with indicators and subfields.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `tag` | str | Field tag (010-999), zero-padded to 3 chars |
| `indicator1` | str | First indicator (blank or digit) |
| `indicator2` | str | Second indicator (blank or digit) |
| `subfields` | list[Subfield] | List of subfields |

#### Example

```python
from kormarc.models import DataField, Subfield

# Create data field
df = DataField(
    tag="245",
    indicator1="1",
    indicator2="0",
    subfields=[
        Subfield(code="a", data="Python Programming"),
        Subfield(code="b", data="A Beginner's Guide")
    ]
)
```

---

### Subfield

**Bases:** `pydantic.BaseModel`

Subfield within a data field.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `code` | str | Subfield code (a-z, 0-9) |
| `data` | str | Subfield data content |

#### Example

```python
from kormarc.models import Subfield

sf = Subfield(code="a", data="Title text")
print(sf.code)  # 'a'
print(sf.data)  # 'Title text'
```

---

### Record

**Bases:** `pydantic.BaseModel`

Complete KORMARC record containing leader, control fields, and data fields.

#### Constructor

```python
Record(
    leader: Leader,
    control_fields: list[ControlField] = [],
    data_fields: list[DataField] = []
)
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `leader` | Leader | Leader field (24-character fixed) |
| `control_fields` | list[ControlField] | List of control fields (001-009) |
| `data_fields` | list[DataField] | List of data fields (010-999) |

#### Methods

##### `to_dict() -> dict`

Convert record to dictionary representation.

**Returns:**
- `dict`: Dictionary containing all record data

**Example:**
```python
data_dict = record.to_dict()
print(data_dict['leader']['record_length'])
```

##### `to_json() -> str`

Convert record to JSON string.

**Returns:**
- `str`: JSON string representation

**Example:**
```python
json_str = record.to_json()
print(json_str)  # {"leader": {...}, "control_fields": [...], ...}
```

##### `to_xml() -> str`

Convert record to MARCXML format following MARC21 standard schema.

**Returns:**
- `str`: MARCXML string with XML declaration

**Example:**
```python
xml_str = record.to_xml()
print(xml_str)
# <?xml version='1.0' encoding='utf-8'?>
# <record xmlns="http://www.loc.gov/MARC21/slim">
#   <leader>00714cam  2200205 a 4500</leader>
#   ...
# </record>
```

##### `validate() -> bool`

Validate record structure and content.

**Returns:**
- `bool`: True if valid

**Raises:**
- `ValidationError`: If validation fails

**Example:**
```python
is_valid = record.validate()
```

---

## Module: kormarc.parser

KORMARC record parser.

### KORMARCParser

Parser for KORMARC format records.

#### Methods

##### `parse(data: str | bytes) -> Record`

Parse KORMARC record from string or bytes.

**Parameters:**
- `data` (str | bytes): KORMARC record data in simplified text format (one field per line: "TAG indicators|subfield_code data")

**Returns:**
- `Record`: Parsed Record object

**Raises:**
- `ParseError`: If parsing fails

**Example:**
```python
from kormarc.parser import KORMARCParser

parser = KORMARCParser()
record = parser.parse("""
00714cam  2200205 a 4500
001 12345
245 10|aPython Programming|bA Guide
260   |aSeoul|bPublisher|c2026
""")
```

**Input Format:**
- First line: 24-character leader string
- Subsequent lines: "TAG content"
- Control fields (001-009): "TAG data"
- Data fields (010+): "TAG indicators|subfield_code data"

##### `parse_file(path: str) -> Record`

Parse KORMARC record from file.

**Parameters:**
- `path` (str): Path to KORMARC file

**Returns:**
- `Record`: Parsed Record object

**Raises:**
- `ParseError`: If parsing fails
- `FileNotFoundError`: If file does not exist

**Example:**
```python
from kormarc.parser import KORMARCParser

parser = KORMARCParser()
record = parser.parse_file("data.kormarc")
```

#### Private Methods

##### `_parse_data_field_content(content: str) -> tuple[list[str], list[Subfield]]`

Parse data field content into indicators and subfields.

**Parameters:**
- `content` (str): Field content (e.g., "10  |aTitle|bSubtitle")

**Returns:**
- `tuple[list[str], list[Subfield]]`: Tuple of (indicators list, subfields list)

---

## Usage Examples

### Basic Parsing

```python
from kormarc import KORMARCParser

parser = KORMARCParser()

# Parse from string
record = parser.parse("""
00714cam  2200205 a 4500
001 12345
245 10|aPython Programming|bBeginner's Guide
260   |aSeoul|bTech Publisher|c2026
""")

# Access data
print(record.leader.record_length)  # 714
print(record.leader.record_status)  # 'c'

# Iterate control fields
for cf in record.control_fields:
    print(f"{cf.tag}: {cf.data}")

# Iterate data fields
for df in record.data_fields:
    print(f"{df.tag}: {df.indicator1}{df.indicator2}")
    for sf in df.subfields:
        print(f"  ${sf.code} {sf.data}")
```

### Conversion

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Convert to JSON
json_data = record.to_json()
with open("record.json", "w") as f:
    f.write(json_data)

# Convert to MARCXML
xml_data = record.to_xml()
with open("record.xml", "w") as f:
    f.write(xml_data)

# Convert to dict
dict_data = record.to_dict()
import json
print(json.dumps(dict_data, indent=2))
```

### Error Handling

```python
from kormarc import KORMARCParser
from kormarc.exceptions import ParseError, ValidationError

parser = KORMARCParser()

try:
    record = parser.parse(invalid_data)
except ParseError as e:
    print(f"Parsing failed: {e.message}")
    if e.context:
        print(f"Additional context: {e.context}")

try:
    record = parser.parse(data)
    record.validate()
except ValidationError as e:
    print(f"Validation failed: {e.message}")
```

### Working with Specific Fields

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Find title field (245)
title_field = next((df for df in record.data_fields if df.tag == "245"), None)
if title_field:
    title = next((sf.data for sf in title_field.subfields if sf.code == "a"), "")
    print(f"Title: {title}")

# Get all subject fields (6xx)
subjects = [df for df in record.data_fields if df.tag.startswith("6")]
for subject in subjects:
    for sf in subject.subfields:
        if sf.code == "a":
            print(f"Subject: {sf.data}")
```

---

## Type Hints

All models and methods use Python type hints for full IDE support:

```python
from kormarc import KORMARCParser, Record
from kormarc.models import Leader, ControlField, DataField

parser: KORMARCParser = KORMARCParser()
record: Record = parser.parse(data)
leader: Leader = record.leader
control_fields: list[ControlField] = record.control_fields
data_fields: list[DataField] = record.data_fields
```

---

## Constants

### MARCXML Namespace

```python
from kormarc.models.record import MARCXML_NAMESPACE

MARCXML_NAMESPACE = "http://www.loc.gov/MARC21/slim"
```

---

## Performance Notes

- Parser uses Pydantic for validation with minimal overhead
- Record models are immutable (frozen=True) for thread safety
- JSON serialization uses Pydantic's optimized JSON encoder
- XML generation uses Python's built-in xml.etree.ElementTree

---

## Validation Rules

### Leader Validation
- Must be exactly 24 characters
- Record status must be valid character (a, c, d, n, p)
- Type of record must be valid character
- Numeric fields must parse as integers

### Field Validation
- Control field tags must be 001-009
- Data field tags must be 010-999
- Subfield codes must be a-z or 0-9
- Indicators must be blank or digit

---

## MARC21 References

This implementation follows:
- [MARC21 Format for Bibliographic Data](https://www.loc.gov/marc/bibliographic/)
- [MARC21 XML Schema](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd)
- [KORMARC Standard](https://www.kslib.or.kr/)
