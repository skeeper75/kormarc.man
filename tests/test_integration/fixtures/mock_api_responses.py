"""
Mock API Responses for Integration Tests

국립중앙도서관 API 응답 샘플 데이터 및 헬퍼 함수
"""

# Sample ISBN for testing
SAMPLE_ISBN = "9788960777330"

# Sample MARCXML response from National Library API
SAMPLE_MARCXML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/">
    <srw:numberOfRecords>1</srw:numberOfRecords>
    <srw:records>
        <srw:record>
            <srw:recordSchema>kormarc</srw:recordSchema>
            <srw:recordData>
                <marc:record xmlns:marc="http://www.loc.gov/MARC21/slim">
                    <marc:leader>00000nam a2200000 c 4500</marc:leader>
                    <marc:controlfield tag="001">CNL000012345</marc:controlfield>
                    <marc:controlfield tag="003">KORCNL</marc:controlfield>
                    <marc:controlfield tag="005">20250110120000.0</marc:controlfield>
                    <marc:controlfield tag="008">250110s2025    ulk           000 0 kor</marc:controlfield>
                    <marc:datafield tag="020" ind1=" " ind2=" ">
                        <marc:subfield code="a">9788960777330</marc:subfield>
                        <marc:subfield code="c">₩38000</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="040" ind1=" " ind2=" ">
                        <marc:subfield code="a">211009</marc:subfield>
                        <marc:subfield code="c">211009</marc:subfield>
                        <marc:subfield code="d">211009</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="082" ind1="0" ind2="4">
                        <marc:subfield code="a">005.133</marc:subfield>
                        <marc:subfield code="2">23</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="100" ind1="1" ind2=" ">
                        <marc:subfield code="a">박응용</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="245" ind1="1" ind2="0">
                        <marc:subfield code="a">파이썬 프로그래밍</marc:subfield>
                        <marc:subfield code="b">기초부터 실전까지</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="260" ind1=" " ind2=" ">
                        <marc:subfield code="a">서울</marc:subfield>
                        <marc:subfield code="b">한빛미디어</marc:subfield>
                        <marc:subfield code="c">2025</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="300" ind1=" " ind2=" ">
                        <marc:subfield code="a">500 p.</marc:subfield>
                        <marc:subfield code="c">26 cm</marc:subfield>
                    </marc:datafield>
                </marc:record>
            </srw:recordData>
        </srw:record>
    </srw:records>
</srw:searchRetrieveResponse>
"""

# Sample empty MARCXML response
SAMPLE_EMPTY_MARCXML_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/">
    <srw:numberOfRecords>0</srw:numberOfRecords>
    <srw:records/>
</srw:searchRetrieveResponse>
"""

# Sample KORMARC data (parsed)
SAMPLE_KORMARC_DATA = {
    "leader": "00000nam a2200000 c 4500",
    "control_fields": {
        "001": "CNL000012345",
        "003": "KORCNL",
        "005": "20250110120000.0",
        "008": "250110s2025    ulk           000 0 kor",
    },
    "data_fields": {
        "020": {
            "ind1": " ",
            "ind2": " ",
            "subfields": {
                "a": "9788960777330",
                "c": "₩38000",
            },
        },
        "040": {
            "ind1": " ",
            "ind2": " ",
            "subfields": {
                "a": "211009",
                "c": "211009",
                "d": "211009",
            },
        },
        "082": {
            "ind1": "0",
            "ind2": "4",
            "subfields": {
                "a": "005.133",
                "2": "23",
            },
        },
        "100": {
            "ind1": "1",
            "ind2": " ",
            "subfields": {
                "a": "박응용",
            },
        },
        "245": {
            "ind1": "1",
            "ind2": "0",
            "subfields": {
                "a": "파이썬 프로그래밍",
                "b": "기초부터 실전까지",
            },
        },
        "260": {
            "ind1": " ",
            "ind2": " ",
            "subfields": {
                "a": "서울",
                "b": "한빛미디어",
                "c": "2025",
            },
        },
        "300": {
            "ind1": " ",
            "ind2": " ",
            "subfields": {
                "a": "500 p.",
                "c": "26 cm",
            },
        },
    },
    "isbn": "9788960777330",
    "title": "파이썬 프로그래밍",
    "author": "박응용",
    "publisher": "한빛미디어",
    "pub_year": "2025",
    "pages": 500,
    "kdc": "005.133",
}


def create_mock_marcxml(isbn: str = SAMPLE_ISBN, title: str = "테스트 도서") -> str:
    """
    Mock MARCXML 응답 생성

    Args:
        isbn: ISBN
        title: 제목

    Returns:
        MARCXML 응답 문자열
    """
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/">
    <srw:numberOfRecords>1</srw:numberOfRecords>
    <srw:records>
        <srw:record>
            <srw:recordSchema>kormarc</srw:recordSchema>
            <srw:recordData>
                <marc:record xmlns:marc="http://www.loc.gov/MARC21/slim">
                    <marc:leader>00000nam a2200000 c 4500</marc:leader>
                    <marc:controlfield tag="001">TEST001</marc:controlfield>
                    <marc:controlfield tag="003">KORCNL</marc:controlfield>
                    <marc:controlfield tag="005">20250110120000.0</marc:controlfield>
                    <marc:controlfield tag="008">250110s2025    ulk           000 0 kor</marc:controlfield>
                    <marc:datafield tag="020" ind1=" " ind2=" ">
                        <marc:subfield code="a">{isbn}</marc:subfield>
                    </marc:datafield>
                    <marc:datafield tag="245" ind1="1" ind2="0">
                        <marc:subfield code="a">{title}</marc:subfield>
                    </marc:datafield>
                </marc:record>
            </srw:recordData>
        </srw:record>
    </srw:records>
</srw:searchRetrieveResponse>
"""


def create_mock_api_error_response() -> str:
    """
    Mock API 오류 응답 생성

    Returns:
        에러 응답 XML 문자열
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/">
    <srw:diagnostics>
        <diag:diagnostic xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/">
            <diag:uri>info:srw/diagnostic/1/4</diag:uri>
            <diag:details>Unsupported operation</diag:details>
            <diag:message>Unsupported operation</diag:message>
        </diag:diagnostic>
    </srw:diagnostics>
</srw:searchRetrieveResponse>
"""


# Sample scraper data (웹 스크래핑 결과)
SAMPLE_SCRAPER_DATA = {
    "title": "파이썬 프로그래밍",
    "author": "박응용",
    "publisher": "한빛미디어",
    "pub_year": "2025",
    "pages": 500,
    "isbn": SAMPLE_ISBN,
    "kdc": "005",
    "detail_url": "https://www.nl.go.kr/nis/detailView.do?isbn=9788960777330",
    "detail_id": "9788960777330",
}


def create_mock_scraper_data(isbn: str = SAMPLE_ISBN, **kwargs) -> dict:
    """
    Mock 스크래퍼 데이터 생성

    Args:
        isbn: ISBN
        **kwargs: 추가 필드 (title, author, publisher 등)

    Returns:
        스크래퍼 결과 딕셔너리
    """
    default_data = {
        "title": "테스트 도서",
        "author": "테스트 저자",
        "publisher": "테스트 출판사",
        "pub_year": "2025",
        "pages": 300,
        "isbn": isbn,
        "kdc": "000",
        "detail_url": f"https://www.nl.go.kr/nis/detailView.do?isbn={isbn}",
        "detail_id": isbn,
    }
    default_data.update(kwargs)
    return default_data
