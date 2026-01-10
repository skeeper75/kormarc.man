"""
KORMARC test fixtures and sample data.

This module provides real-world KORMARC record samples for testing.
"""

# Valid KORMARC book record
VALID_BOOK_RECORD = """
00714cam  2200205 a 4500
001 1234567890
008 200101s2020    ko a     000 0 kor d
245 10  |a파이썬 코딩의 기술 /|d클로드 지음 ;|e홍길동 옮김
100 1   |a클로드,|e지음
260    |a서울 :|b출판사,|c2020
300    |a xviii, 456 p. :|b삽화 ;|c24 cm
500    |aIncludes index
650  0 |a컴퓨터 프로그래밍
700 1   |a홍길동,|e역
""".strip()

# Minimal valid record
MINIMAL_RECORD = """
00422nam  2200145 a 4500
001 0000000001
008 200101s2020    ko a
245 00 |aTest Title
""".strip()

# Record with multiple data fields
MULTIPLE_FIELDS_RECORD = """
00850cam  2200277 a 4500
001 9876543210
008 201501s2015    ko a     001 0 kor d
020    |a9788966260005
040    |a211060
041 0  |akor
082 04 |a005.13
100 1   |a저자,|e저
245 13 |a파이썬 완벽 가이드 /|c저자 지음
250    |a초판
260    |a서울 :|b한빛미디어,|c2015
300    |a xx, 695 p. ;|c24 cm +|eCD-ROM 1매
490 1  |aIT EXPERT
500    |a색인수록
650  0 |aPython (컴퓨터 프로그래밍 언어)
650  0 |a프로그래밍 언어
700 1  |a공저자,|e저
""".strip()

# Record with only control fields
CONTROL_ONLY_RECORD = """
00314nam  2200121 a 4500
001 1111111111
008 202001s2020    ko a
""".strip()

# Invalid record - wrong leader length
INVALID_LEADER_LENGTH = """
00am  2200205 a 4500
001 12345
""".strip()

# Invalid record - missing required fields
INCOMPLETE_RECORD = """
00714cam  2200205 a 4500
001 12345
""".strip()

# Real KORMARC serial record sample
SERIAL_RECORD = """
00787cas  2200289 a 4500
001 12345678
008 199001m19909999kr ar p       0   a0kor d
245 00 |a한국 잡지
260    |a서울 :|b출판사
310    |a월간
362 0  |aNo. 1 (1990. 1)-
550    |a한국학 관련 기사 수록
650  0 |a잡지
710 2  |a한국학술지
""".strip()

# Record with special characters in subfields
SPECIAL_CHARS_RECORD = """
00645nam  2200217 a 4500
001 5555555555
008 201001s2010    ko a     000 0 kor d
245 14 |aC++ & Java 완벽 비교 /|d"개발자" 지음
100 1   |aSmith, John,|e저
260    |a서울 :|bTech Books,|c2010
300    |a 500 p. ;|c23 cm
500    |aIncludes CD-ROM: "examples.zip"
650  0 |aC++ (프로그래밍 언어)
650  0 |aJava (프로그래밍 언어)
""".strip()

# Record for round-trip testing (serialization/deserialization)
ROUNDTRIP_RECORD = """
00782nam  2200253 a 4500
001 9999999999
008 202301s2023    ko a     000 0 kor d
020    |a9791162243630
040    |a211060
041 0  |akoreng
082 04 |a005.133
100 1   |a김개발,|e저
245 13 |a테스트 주도 개발 :|bTDD 실천 가이드 /|d김개발 지음
246 30 |aTDD 실천 가이드
250    |a3판
260    |a판교 :|b한빛미디어,|c2023
300    |a xv, 358 p. :|b삽화 ;|c24 cm
490 1  |aACORN+ 실전 개발 시리즈
500    |a부록: 테스트 코드 예제
650  0 |a소프트웨어 공학
650  0 |a테스트 주도 개발
700 1   |a이협력,|e저
""".strip()

# Directory entry format for variable-length fields
# Format: tag + length + starting_position
DIRECTORY_ENTRY = {"tag": "245", "length": "0025", "position": "00125"}

# Sample directory entries
SAMPLE_DIRECTORY = [
    "0010006000000",
    "0080041000006",
    "0200018000047",
    "0400006000065",
    "0410004000071",
    "0820007000075",
    "1000012000082",
    "2450025000094",
    "2500003000119",
    "2600030000122",
    "3000022000152",
    "4900018000174",
    "5000020000192",
    "6500014000212",
    "6500014000226",
    "7000012000240",
]


def get_expected_record_data():
    """Get expected Record data for VALID_BOOK_RECORD.

    Returns:
        Dictionary containing expected parsed Record field values
    """
    return {
        "leader": {
            "record_length": 714,
            "record_status": "a",
            "type_of_record": "c",
            "bibliographic_level": "a",
            "control_type": "m",
            "character_encoding": "a",
            "indicator_count": 2,
            "subfield_code_count": 2,
            "base_address": 205,
            "encoding_level": " ",
            "descriptive_cataloging": "a",
            "multipart_level": " ",
            "entry_map": "4500",
        },
        "control_fields": [
            {"tag": "001", "data": "1234567890"},
            {"tag": "008", "data": "200101s2020    ko a     000 0 kor d"},
        ],
        "data_fields": [
            {
                "tag": "245",
                "indicator1": "1",
                "indicator2": "0",
                "subfields": [
                    {"code": "a", "data": "파이썬 코딩의 기술 /"},
                    {"code": "d", "data": "클로드 지음 ;"},
                    {"code": "e", "data": "홍길동 옮김"},
                ],
            },
            {
                "tag": "100",
                "indicator1": "1",
                "indicator2": " ",
                "subfields": [
                    {"code": "a", "data": "클로드,"},
                    {"code": "e", "data": "지음"},
                ],
            },
            {
                "tag": "260",
                "indicator1": " ",
                "indicator2": " ",
                "subfields": [
                    {"code": "a", "data": "서울 :"},
                    {"code": "b", "data": "출판사,"},
                    {"code": "c", "data": "2020"},
                ],
            },
            {
                "tag": "300",
                "indicator1": " ",
                "indicator2": " ",
                "subfields": [
                    {"code": "a", "data": " xviii, 456 p. :"},
                    {"code": "b", "data": "삽화 ;"},
                    {"code": "c", "data": "24 cm"},
                ],
            },
            {
                "tag": "500",
                "indicator1": " ",
                "indicator2": " ",
                "subfields": [
                    {"code": "a", "data": "Includes index"},
                ],
            },
            {
                "tag": "650",
                "indicator1": " ",
                "indicator2": "0",
                "subfields": [
                    {"code": "a", "data": "컴퓨터 프로그래밍"},
                ],
            },
            {
                "tag": "700",
                "indicator1": "1",
                "indicator2": " ",
                "subfields": [
                    {"code": "a", "data": "홍길동,"},
                    {"code": "e", "data": "역"},
                ],
            },
        ],
    }
