"""KORMARC Builder Debug Test"""

import sys

sys.path.insert(0, "src")

from kormarc.kormarc_builder import BookInfo, KORMARCBuilder, KORMARCRecord

# Test 1: DataField creation
print("=== Test 1: DataField Creation ===")
record = KORMARCRecord()
field = record.add_data("040", " ", " ")
print(f"Type: {type(field)}")
print(f"Field: {field}")
print(f"Has add_subfield: {hasattr(field, 'add_subfield')}")

if field:
    field.add_subfield("a", "NLK")
    print(f"After add_subfield: {field.format()}")

# Test 2: Full build
print("\n=== Test 2: Full Build ===")
builder = KORMARCBuilder()
book_info = BookInfo(
    isbn="9791162233149",
    title="Python 프로그래밍 정복",
    author="박응용",
    publisher="한빛미디어",
    pub_year="2025",
    pages=880,
    kdc="005",
    category="book",
)

record = builder.build(book_info)
print("KORMARC Record:")
print(record.format())
