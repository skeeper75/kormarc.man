# KORMARC Parser Usage Examples

This document provides practical examples for using the KORMARC Parser library.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Parsing Records](#parsing-records)
- [Data Access](#data-access)
- [Format Conversion](#format-conversion)
- [Error Handling](#error-handling)
- [Advanced Examples](#advanced-examples)

---

## Basic Usage

### Importing the Library

```python
# Import all main components
from kormarc import (
    KORMARCParser,
    Record,
    Leader,
    ControlField,
    DataField,
    Subfield,
)

# Import exceptions for error handling
from kormarc.exceptions import (
    ParseError,
    ValidationError,
    ConversionError,
)
```

### Quick Start Example

```python
from kormarc import KORMARCParser

# Create parser instance
parser = KORMARCParser()

# Parse a simple record
record_data = """00714cam  2200205 a 4500
001 12345
245 10|aPython Programming|bA Complete Guide
260   |aSeoul|bTech Publisher|c2026"""

record = parser.parse(record_data)

# Convert to different formats
json_output = record.to_json()
xml_output = record.to_xml()
dict_output = record.to_dict()

print(f"Record Length: {record.leader.record_length}")
print(f"Title: {record.data_fields[0].subfields[0].data}")
```

---

## Parsing Records

### Parsing from String

```python
from kormarc import KORMARCParser

parser = KORMARCParser()

# Multi-line string with record data
record_data = """
00714cam  2200205 a 4500
001 12345678
008 210101s2026    ko |a|
020   |a9788999999991
040   |aKER|bkor|cKER
041 0 |akor
082 04|a005.13|22
245 00|aPython programming|bbeginner's guide
250   |aFirst edition
260   |aSeoul|bCoding Publishers|c2026
300   |axxiv, 450 pages|billustrations|c24 cm
500   |aIncludes index
650  0|aPython (Computer program language)|vTextbooks
700 1 |aSmith, John.|eauthor
"""

record = parser.parse(record_data)
```

### Parsing from File

```python
from kormarc import KORMARCParser

parser = KORMARCParser()

# Parse from file
record = parser.parse_file("data/bibliographic_record.kormarc")

# Process the record
print(f"Parsed record: {record.leader.record_length} bytes")
```

### Creating Records Programmatically

```python
from kormarc import Leader, Record, ControlField, DataField, Subfield

# Create leader
leader = Leader.from_string("00714cam  2200205 a 4500")

# Create control fields
control_fields = [
    ControlField(tag="001", data="12345"),
    ControlField(tag="008", data="210101s2026    ko |a|"),
]

# Create data fields
data_fields = [
    DataField(
        tag="245",
        indicator1="1",
        indicator2="0",
        subfields=[
            Subfield(code="a", data="Python Programming"),
            Subfield(code="b", data="A Complete Guide"),
        ]
    ),
    DataField(
        tag="260",
        indicator1=" ",
        indicator2=" ",
        subfields=[
            Subfield(code="a", data="Seoul"),
            Subfield(code="b", data="Tech Publisher"),
            Subfield(code="c", data="2026"),
        ]
    ),
]

# Create record
record = Record(
    leader=leader,
    control_fields=control_fields,
    data_fields=data_fields,
)
```

---

## Data Access

### Accessing Leader Information

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Access leader properties
leader = record.leader

print(f"Record Length: {leader.record_length}")
print(f"Record Status: {leader.record_status}")
print(f"Type of Record: {leader.type_of_record}")
print(f"Bibliographic Level: {leader.bibliographic_level}")
print(f"Encoding Level: {leader.encoding_level}")
print(f"Base Address: {leader.base_address}")
```

### Accessing Control Fields

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Iterate all control fields
for cf in record.control_fields:
    print(f"Tag {cf.tag}: {cf.data}")

# Find specific control field
isbn_field = next((cf for cf in record.control_fields if cf.tag == "020"), None)
if isbn_field:
    print(f"ISBN: {isbn_field.data}")
```

### Accessing Data Fields

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Iterate all data fields
for df in record.data_fields:
    print(f"Tag {df.tag}: Indicators [{df.indicator1}][{df.indicator2}]")
    for sf in df.subfields:
        print(f"  ${sf.code} {sf.data}")

# Find specific data field (245 - Title)
title_field = next((df for df in record.data_fields if df.tag == "245"), None)
if title_field:
    title = next((sf.data for sf in title_field.subfields if sf.code == "a"), "")
    subtitle = next((sf.data for sf in title_field.subfields if sf.code == "b"), "")
    print(f"Title: {title}")
    print(f"Subtitle: {subtitle}")
```

### Extracting Specific Information

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

def get_subfield_value(field, code):
    """Get first subfield value with given code."""
    for sf in field.subfields:
        if sf.code == code:
            return sf.data
    return None

def get_field_by_tag(record, tag):
    """Get first field with given tag."""
    return next((df for df in record.data_fields if df.tag == tag), None)

# Extract title
title_field = get_field_by_tag(record, "245")
if title_field:
    title = get_subfield_value(title_field, "a")
    print(f"Title: {title}")

# Extract publication information
pub_field = get_field_by_tag(record, "260")
if pub_field:
    place = get_subfield_value(pub_field, "a")
    publisher = get_subfield_value(pub_field, "b")
    year = get_subfield_value(pub_field, "c")
    print(f"Published: {place}: {publisher}, {year}")

# Extract subjects
subjects = [df for df in record.data_fields if df.tag.startswith("6")]
for subject in subjects:
    value = get_subfield_value(subject, "a")
    if value:
        print(f"Subject: {value}")
```

---

## Format Conversion

### Converting to JSON

```python
from kormarc import KORMARCParser
import json

parser = KORMARCParser()
record = parser.parse(record_data)

# Get JSON string
json_string = record.to_json()

# Pretty print
json_data = json.loads(json_string)
print(json.dumps(json_data, indent=2, ensure_ascii=False))

# Save to file
with open("output/record.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(json_data, indent=2, ensure_ascii=False))
```

### Converting to MARCXML

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Get XML string
xml_string = record.to_xml()

# Print or save
print(xml_string)

with open("output/record.xml", "w", encoding="utf-8") as f:
    f.write(xml_string)
```

Expected XML output:

```xml
<?xml version='1.0' encoding='utf-8'?>
<record xmlns="http://www.loc.gov/MARC21/slim">
  <leader>00714cam  2200205 a 4500</leader>
  <controlfield tag="001">12345</controlfield>
  <controlfield tag="008">210101s2026    ko |a|</controlfield>
  <datafield tag="245" ind1="1" ind2="0">
    <subfield code="a">Python Programming</subfield>
    <subfield code="b">A Complete Guide</subfield>
  </datafield>
  <datafield tag="260" ind1=" " ind2=" ">
    <subfield code="a">Seoul</subfield>
    <subfield code="b">Tech Publisher</subfield>
    <subfield code="c">2026</subfield>
  </datafield>
</record>
```

### Converting to Dictionary

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse(record_data)

# Get dictionary representation
data_dict = record.to_dict()

# Access nested data
record_length = data_dict['leader']['record_length']
control_fields = data_dict['control_fields']

# Modify (creates new dict since models are frozen)
modified_dict = data_dict.copy()
modified_dict['leader']['record_length'] = 1000
```

---

## Error Handling

### Parsing Errors

```python
from kormarc import KORMARCParser
from kormarc.exceptions import ParseError

parser = KORMARCParser()

# Handle parsing errors
try:
    record = parser.parse(invalid_data)
except ParseError as e:
    print(f"Parsing failed: {e.message}")
    if e.context:
        for key, value in e.context.items():
            print(f"  {key}: {value}")
```

### Validation Errors

```python
from kormarc import KORMARCParser
from kormarc.exceptions import ValidationError

parser = KORMARCParser()

try:
    record = parser.parse(data)
    # Validate record
    record.validate()
except ValidationError as e:
    print(f"Validation failed: {e.message}")
```

### Conversion Errors

```python
from kormarc import KORMARCParser
from kormarc.exceptions import JSONConversionError, XMLConversionError

parser = KORMARCParser()
record = parser.parse(data)

try:
    json_data = record.to_json()
except JSONConversionError as e:
    print(f"JSON conversion failed: {e}")

try:
    xml_data = record.to_xml()
except XMLConversionError as e:
    print(f"XML conversion failed: {e}")
```

---

## Advanced Examples

### Batch Processing Records

```python
from kormarc import KORMARCParser

def process_batch(file_path: str):
    """Process multiple records from a file."""
    parser = KORMARCParser()

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by double newline (assuming records separated by blank lines)
    record_strings = content.strip().split('\n\n')

    records = []
    errors = []

    for i, record_str in enumerate(record_strings, 1):
        try:
            record = parser.parse(record_str)
            records.append(record)
            print(f"Processed record {i}")
        except Exception as e:
            errors.append((i, str(e)))
            print(f"Error in record {i}: {e}")

    return records, errors

# Usage
records, errors = process_batch("data/batch_records.kormarc")
print(f"Successfully processed: {len(records)} records")
print(f"Errors: {len(errors)}")
```

### Filtering Records by Criteria

```python
from kormarc import KORMARCParser

def filter_by_language(records, language_code):
    """Filter records by language (008 field)."""
    filtered = []
    for record in records:
        for cf in record.control_fields:
            if cf.tag == "008" and len(cf.data) >= 35:
                if cf.data[35:38] == language_code:
                    filtered.append(record)
                    break
    return filtered

def filter_by_year(records, year):
    """Filter records by publication year."""
    filtered = []
    for record in records:
        for df in record.data_fields:
            if df.tag == "260":
                for sf in df.subfields:
                    if sf.code == "c" and str(year) in sf.data:
                        filtered.append(record)
                        break
    return filtered

# Usage
parser = KORMARCParser()
records = [parser.parse(record_data) for record_data in record_list]

korean_records = filter_by_language(records, "kor")
year_2026_records = filter_by_year(records, 2026)
```

### Building a Simple Catalog

```python
from kormarc import KORMARCParser
from dataclasses import dataclass
from typing import Optional

@dataclass
class CatalogEntry:
    """Simple catalog entry."""
    title: str
    subtitle: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    year: Optional[str]
    isbn: Optional[str]
    subjects: list[str]

def extract_catalog_entry(record) -> CatalogEntry:
    """Extract catalog information from KORMARC record."""
    def get_subfield(field, code):
        if not field:
            return None
        for sf in field.subfields:
            if sf.code == code:
                return sf.data
        return None

    def get_field(tag):
        return next((df for df in record.data_fields if df.tag == tag), None)

    def get_control(tag):
        return next((cf for cf in record.control_fields if cf.tag == tag), None)

    # Title information (245)
    title_field = get_field("245")
    title = get_subfield(title_field, "a") or ""
    subtitle = get_subfield(title_field, "b")

    # Author (100 or 700)
    author_field = get_field("100") or get_field("700")
    author = get_subfield(author_field, "a")

    # Publication (260)
    pub_field = get_field("260")
    publisher = get_subfield(pub_field, "b")
    year = get_subfield(pub_field, "c")

    # ISBN (020)
    isbn_field = get_control("020")
    isbn = isbn_field.data if isbn_field else None

    # Subjects (6xx)
    subjects = []
    for df in record.data_fields:
        if df.tag.startswith("6"):
            subject = get_subfield(df, "a")
            if subject:
                subjects.append(subject)

    return CatalogEntry(
        title=title,
        subtitle=subtitle,
        author=author,
        publisher=publisher,
        year=year,
        isbn=isbn,
        subjects=subjects,
    )

# Usage
parser = KORMARCParser()
record = parser.parse(record_data)
entry = extract_catalog_entry(record)

print(f"Title: {entry.title}")
if entry.subtitle:
    print(f"Subtitle: {entry.subtitle}")
if entry.author:
    print(f"Author: {entry.author}")
print(f"Subjects: {', '.join(entry.subjects)}")
```

### Exporting to CSV

```python
import csv
from kormarc import KORMARCParser

def export_to_csv(records, output_path):
    """Export KORMARC records to CSV format."""
    parser = KORMARCParser()

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow([
            'Title',
            'Author',
            'Publisher',
            'Year',
            'ISBN',
            'Subjects'
        ])

        # Write records
        for record in records:
            # Extract data (simplified)
            title = ""
            author = ""
            publisher = ""
            year = ""
            isbn = ""
            subjects = []

            for df in record.data_fields:
                if df.tag == "245":
                    for sf in df.subfields:
                        if sf.code == "a":
                            title = sf.data
                elif df.tag in ["100", "700"]:
                    for sf in df.subfields:
                        if sf.code == "a":
                            author = sf.data
                elif df.tag == "260":
                    for sf in df.subfields:
                        if sf.code == "b":
                            publisher = sf.data
                        elif sf.code == "c":
                            year = sf.data.replace('c', '').strip()
                elif df.tag.startswith("6"):
                    for sf in df.subfields:
                        if sf.code == "a":
                            subjects.append(sf.data)

            for cf in record.control_fields:
                if cf.tag == "020":
                    isbn = cf.data

            writer.writerow([
                title,
                author,
                publisher,
                year,
                isbn,
                '; '.join(subjects)
            ])

# Usage
records = [parser.parse(data) for data in record_list]
export_to_csv(records, "output/catalog.csv")
```

---

## Tips and Best Practices

1. **Always handle exceptions**: KORMARC parsing can fail due to malformed input
2. **Validate after parsing**: Use `record.validate()` to ensure data integrity
3. **Use type hints**: The library provides full type hints for better IDE support
4. **Cache parsed records**: Record models are frozen/immutable, safe to cache
5. **Check for None**: When finding specific fields, always check if field exists
6. **UTF-8 encoding**: Always use UTF-8 when reading/writing files with Korean text
7. **Batch processing**: Process records in batches for better performance

---

## Further Reading

- [API Documentation](API.md)
- [MARC21 Format](https://www.loc.gov/marc/bibliographic/)
- [KORMARC Standard](https://www.kslib.or.kr/)
