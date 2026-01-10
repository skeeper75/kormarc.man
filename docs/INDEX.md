# KORMARC Parser Documentation

Complete documentation for KORMARC Parser library version 0.1.0.

## Documentation Contents

### Getting Started
- [README.md](../README.md) - Project overview, installation, and quick start guide
- [CHANGELOG.md](../CHANGELOG.md) - Version history and release notes

### API Reference
- [API.md](API.md) - Complete API documentation for all modules, classes, and methods

### Usage Examples
- [EXAMPLES.md](EXAMPLES.md) - Practical examples and usage patterns

## Quick Links

### Core Concepts
- [KORMARC Format](../README.md#데이터-형식) - Understanding the data structure
- [Data Models](API.md#module-kormarcmodels) - Leader, ControlField, DataField, Subfield, Record
- [Parser](API.md#module-kormarcparser) - KORMARCParser class

### Common Tasks
- [Basic Parsing](EXAMPLES.md#parsing-records) - Parse records from string or file
- [Data Access](EXAMPLES.md#data-access) - Access leader, fields, and subfields
- [Format Conversion](EXAMPLES.md#format-conversion) - Convert to JSON, XML, or dict
- [Error Handling](EXAMPLES.md#error-handling) - Handle parsing and validation errors

### Advanced Topics
- [Batch Processing](EXAMPLES.md#batch-processing-records) - Process multiple records
- [Filtering Records](EXAMPLES.md#filtering-records-by-criteria) - Filter by language, year, etc.
- [Building a Catalog](EXAMPLES.md#building-a-simple-catalog) - Create catalog entries
- [Exporting to CSV](EXAMPLES.md#exporting-to-csv) - Export records to CSV format

## Library Overview

KORMARC Parser is a Python library for parsing and converting Korean Library Automation Data Format (KORMARC) records. It provides:

- Type-safe data models using Pydantic
- LINE-based parsing for simple text format
- MARC21 standard compliant XML output
- JSON serialization support
- Comprehensive error handling
- 90%+ test coverage

## Installation

```bash
pip install kormarc-parser
```

With development dependencies:

```bash
pip install kormarc-parser[dev]
```

## Quick Example

```python
from kormarc import KORMARCParser

parser = KORMARCParser()
record = parser.parse("""
00714cam  2200205 a 4500
001 12345
245 10|aPython Programming|bA Guide
260   |aSeoul|bPublisher|c2026
""")

# Convert formats
json_data = record.to_json()
xml_data = record.to_xml()

# Access data
print(record.leader.record_length)
for field in record.data_fields:
    print(f"{field.tag}: {[sf.data for sf in field.subfields]}")
```

## Project Links

- Repository: GitHub
- Issues: GitHub Issues
- License: MIT
- Python: 3.12+
- PyPI: kormarc-parser

## External References

- [MARC21 Bibliographic Format](https://www.loc.gov/marc/bibliographic/)
- [MARC21 XML Schema](http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd)
- [KORMARC Standard](https://www.kslib.or.kr/)

---

For detailed documentation, see the specific documentation files listed above.
