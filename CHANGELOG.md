# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-10

### Added

#### Core Features
- KORMARC record parser with LINE-based parsing format
- Leader model with 24-character fixed field validation
- ControlField model for tags 001-009
- DataField model for tags 010-999 with indicators and subfields
- Subfield model for field subdivision
- Record model containing leader, control fields, and data fields

#### Conversion Features
- JSON serialization via `Record.to_json()` method
- MARC21 XML conversion via `Record.to_xml()` method
- Dictionary export via `Record.to_dict()` method
- Standard MARCXML schema compliance (http://www.loc.gov/MARC21/slim)

#### Parser Implementation
- `KORMARCParser.parse()` for string/bytes input
- `KORMARCParser.parse_file()` for file-based parsing
- UTF-8 encoding support for Korean and international text
- Automatic indicator and subfield parsing

#### Exception Hierarchy
- `KORMARCError` base exception class
- `ParseError` for parsing failures
- `LeaderParseError` for leader-specific errors
- `FieldParseError` for field parsing errors
- `SubfieldParseError` for subfield parsing errors
- `ValidationError` for data validation failures
- `LeaderValidationError` for leader validation errors
- `FieldValidationError` for field validation errors
- `ConversionError` for format conversion failures
- `JSONConversionError` for JSON conversion errors
- `XMLConversionError` for XML conversion errors
- `EncodingError` for encoding-related errors

#### Data Models
- Pydantic-based type-safe models
- Immutable record structure with frozen=True
- Automatic data validation
- Strict mode enforcement

#### Testing
- 89 passing tests with 90.98% coverage
- Unit tests for all models (Leader, Fields, Record)
- Integration tests for parser functionality
- Serialization tests (JSON, XML)
- Roundtrip conversion tests
- Edge case and error handling tests

#### Developer Experience
- Type hints throughout codebase
- mypy compatibility
- ruff linting and formatting
- pytest for testing with coverage reporting
- pyproject.toml for modern Python packaging

### Specification Implementation
- Implemented SPEC-KORMARC-PARSER-001 requirements
- KORMARC format parsing (LINE-based format)
- Record to JSON conversion
- Record to MARCXML conversion (MARC21 standard)
- Data models with validation

### Dependencies
- Python 3.12+ support
- pydantic >= 2.9.0 for data validation

### Development Dependencies
- pytest >= 8.0.0 for testing
- pytest-cov >= 4.0.0 for coverage reporting
- ruff >= 0.8.0 for linting and formatting
- mypy >= 1.0.0 for type checking

---

## [Unreleased]

### Planned Features
- Batch file parsing
- MARCXML to Record parsing
- Field validation rules
- Additional MARC field support
- Performance optimizations
- CLI tool for record conversion
