"""
KORMARC 빌더 모듈

도서 정보(BookInfo)를 KORMARC 레코드로 변환하는 빌더 클래스.

명세:
- docs/NOWON_KORMARC_RULES.md (노원구 KORMARC 규칙)
- docs/TOON_SPEC.md (TOON 식별자 명세)

통합:
- models/record.py의 Pydantic Record 사용
- toon_generator.py의 TOON 생성과 연동
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from kormarc.models.fields import ControlField as PydanticControlField
from kormarc.models.fields import DataField as PydanticDataField
from kormarc.models.fields import Subfield
from kormarc.models.leader import Leader
from kormarc.models.record import Record
from kormarc.toon_generator import TOONGenerator


@dataclass
class BookInfo:
    """도서 정보 데이터 클래스"""

    isbn: str
    """ISBN (13자리, 하이픈 제거)"""

    title: str
    """도서 제목"""

    author: str | None = None
    """저자명"""

    publisher: str | None = None
    """발행처"""

    pub_year: str | None = None
    """발행년 (YYYY 또는 YYYYMM)"""

    pages: int | None = None
    """페이지수"""

    kdc: str | None = None
    """KDC (한국십진분류표) 분류기호"""

    category: str = "book"
    """도서 유형 (book, serial, academic, comic)"""

    price: int | None = None
    """가격 (원)"""

    description: str | None = None
    """내용 요약"""

    def to_dict(self) -> dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "pub_year": self.pub_year,
            "pages": self.pages,
            "kdc": self.kdc,
            "category": self.category,
            "price": self.price,
            "description": self.description,
        }


class KORMARCBuilder:
    """
    KORMARC 빌더

    BookInfo를 KORMARC 레코드로 변환하고 TOON 식별자를 생성합니다.

    Example:
        >>> builder = KORMARCBuilder()
        >>> book_info = BookInfo(
        ...     isbn="9791162233149",
        ...     title="Python 프로그래밍",
        ...     author="박응용",
        ...     publisher="한빛미디어",
        ...     pub_year="2025",
        ...     pages=500
        ... )
        >>> record, toon_id = builder.build_with_toon(book_info)
        >>> print(record.to_xml())
    """

    # 제어번호 생성기 (시뮬레이션)
    _control_number = 100000

    def __init__(self, toon_generator: TOONGenerator | None = None):
        """
        빌더 초기화

        Args:
            toon_generator: TOON 생성기 (없으면 자동 생성)
        """
        self.toon_generator = toon_generator or TOONGenerator()

    def _generate_control_number(self) -> str:
        """제어번호 생성 (001 필드)"""
        control_num = KORMARCBuilder._control_number
        KORMARCBuilder._control_number += 1
        return f"{control_num:012d}"

    def _generate_leader(self, book_info: BookInfo) -> Leader:
        """리더 생성"""
        # bibliographic_level 결정
        bib_level_map = {
            "book": "m",
            "serial": "s",
            "academic": "a",
            "comic": "c",
        }
        bib_level = bib_level_map.get(book_info.category, "m")

        # Leader 생성 (단행본 기본)
        return Leader(
            record_length=714,  # 계산된 길이 (시뮬레이션)
            record_status="a",  # 증가하는 완전 레코드
            type_of_record="a",  # 언어 자료
            bibliographic_level=bib_level,
            control_type="m",
            character_encoding="a",  # UTF-8
            indicator_count=2,
            subfield_code_count=2,
            base_address=205,
            encoding_level=" ",
            descriptive_cataloging=" ",
            multipart_level=" ",
            entry_map="4500",
        )

    def _build_control_fields(self, book_info: BookInfo) -> list[PydanticControlField]:
        """제어 필드 생성"""
        today = datetime.now()
        date_str = today.strftime("%y%m%d")

        # 언어 코드
        language = "kor"

        # 형태 코드 결정
        type_code_map = {"book": "a", "serial": "s", "academic": "a", "comic": "a"}
        type_code = type_code_map.get(book_info.category, "a")

        # 008 필드 데이터 (40문자 고정길이)
        field_008_data = f"{date_str}s2025    {language:3s}  {type_code}"
        # 패딩으로 40자리 맞춤
        field_008_data = field_008_data.ljust(40, " ")

        return [
            PydanticControlField(tag="001", data=self._generate_control_number()),
            PydanticControlField(tag="003", data="NLK"),
            PydanticControlField(tag="005", data=today.strftime("%Y%m%d%H%M%S.0")),
            PydanticControlField(tag="008", data=field_008_data),
        ]

    def _build_data_fields(self, book_info: BookInfo) -> list[PydanticDataField]:
        """데이터 필드 생성"""
        data_fields = []

        # 040: 목록작성기관
        data_fields.append(
            PydanticDataField(
                tag="040",
                indicator1=" ",
                indicator2=" ",
                subfields=[
                    Subfield(code="a", data="NLK"),
                    Subfield(code="b", data="kor"),
                    Subfield(code="c", data="(NLK)"),
                    Subfield(code="d", data="NLK"),
                    Subfield(code="e", data="KORMARC2014"),
                ],
            )
        )

        # 020: ISBN
        data_fields.append(
            PydanticDataField(
                tag="020",
                indicator1=" ",
                indicator2=" ",
                subfields=[Subfield(code="a", data=book_info.isbn)],
            )
        )

        # 100: 주요 저자
        if book_info.author:
            data_fields.append(
                PydanticDataField(
                    tag="100",
                    indicator1="1",
                    indicator2=" ",
                    subfields=[Subfield(code="a", data=book_info.author)],
                )
            )

        # 245: 표제
        data_fields.append(
            PydanticDataField(
                tag="245",
                indicator1="0",
                indicator2=" ",
                subfields=[Subfield(code="a", data=book_info.title)],
            )
        )

        # 260: 발행사항
        subfields_260 = []
        if book_info.publisher:
            subfields_260.append(Subfield(code="b", data=book_info.publisher))
        if book_info.pub_year:
            subfields_260.append(Subfield(code="c", data=f"c{book_info.pub_year}"))

        if subfields_260:
            data_fields.append(
                PydanticDataField(
                    tag="260",
                    indicator1=" ",
                    indicator2=" ",
                    subfields=subfields_260,
                )
            )

        # 300: 형태사항
        if book_info.pages:
            data_fields.append(
                PydanticDataField(
                    tag="300",
                    indicator1=" ",
                    indicator2=" ",
                    subfields=[Subfield(code="a", data=f"{book_info.pages}p")],
                )
            )

        # 082: DDC (KDC 사용)
        if book_info.kdc:
            data_fields.append(
                PydanticDataField(
                    tag="082",
                    indicator1="0",
                    indicator2="4",
                    subfields=[Subfield(code="a", data=book_info.kdc)],
                )
            )

        # 650: 주제명
        if book_info.kdc and book_info.kdc[0] in "0123456789":
            kdc_topics = {
                "0": "총류",
                "1": "철학",
                "2": "종교",
                "3": "사회과학",
                "4": "자연과학",
                "5": "기술과학",
                "6": "예술",
                "7": "언어",
                "8": "문학",
                "9": "역사",
            }
            topic = kdc_topics.get(book_info.kdc[0])
            if topic:
                data_fields.append(
                    PydanticDataField(
                        tag="650",
                        indicator1=" ",
                        indicator2="8",
                        subfields=[Subfield(code="a", data=topic)],
                    )
                )

        return data_fields

    def build(self, book_info: BookInfo) -> Record:
        """
        BookInfo를 KORMARC 레코드로 변환

        Args:
            book_info: 도서 정보

        Returns:
            Pydantic Record 객체

        Example:
            >>> builder = KORMARCBuilder()
            >>> book_info = BookInfo(
            ...     isbn="9791162233149",
            ...     title="Python 프로그래밍"
            ... )
            >>> record = builder.build(book_info)
        """
        leader = self._generate_leader(book_info)
        control_fields = self._build_control_fields(book_info)
        data_fields = self._build_data_fields(book_info)

        return Record(
            leader=leader,
            control_fields=control_fields,
            data_fields=data_fields,
        )

    def build_with_toon(self, book_info: BookInfo) -> tuple[Record, str]:
        """
        BookInfo를 KORMARC 레코드로 변환하고 TOON 식별자 생성

        Args:
            book_info: 도서 정보

        Returns:
            (Record, TOON 식별자) 튜플

        Example:
            >>> builder = KORMARCBuilder()
            >>> book_info = BookInfo(isbn="9791162233149", title="Python")
            >>> record, toon_id = builder.build_with_toon(book_info)
            >>> assert toon_id.startswith("kormarc_")
        """
        # Record 생성
        record = self.build(book_info)

        # TOON 타입 결정
        record_type_map = {
            "book": "kormarc_book",
            "serial": "kormarc_serial",
            "academic": "kormarc_academic",
            "comic": "kormarc_comic",
        }
        record_type = record_type_map.get(book_info.category, "kormarc_book")

        # TOON 생성
        toon_id = self.toon_generator.generate(record_type)

        return record, toon_id

    def build_toon_dict(self, book_info: BookInfo) -> dict[str, Any]:
        """
        BookInfo를 TOON JSON 딕셔너리로 변환

        Args:
            book_info: 도서 정보

        Returns:
            TOON JSON 형식 딕셔너리
        """
        record, toon_id = self.build_with_toon(book_info)

        # TOON 파싱
        parsed_toon = self.toon_generator.parse(toon_id)

        # ISBN 추출
        isbn = book_info.isbn.replace("-", "").replace(" ", "")

        return {
            "toon_id": toon_id,
            "timestamp": parsed_toon["created_at"].isoformat(),
            "type": parsed_toon["type"],
            "isbn": isbn,
            "raw_kormarc": record.to_xml(),
            "parsed": {
                "leader": record.leader.to_dict(),
                "control_fields": [{"tag": f.tag, "data": f.data} for f in record.control_fields],
                "data_fields": [
                    {
                        "tag": f.tag,
                        "indicators": f.indicator1 + f.indicator2,
                        "subfields": [{"code": s.code, "data": s.data} for s in f.subfields],
                    }
                    for f in record.data_fields
                ],
            },
        }


# 모듈 레벨 테스트
if __name__ == "__main__":
    builder = KORMARCBuilder()

    # 샘플 도서 정보
    book_info = BookInfo(
        isbn="9791162233149",
        title="Python 프로그래밍 정복",
        author="박응용",
        publisher="한빛미디어",
        pub_year="2025",
        pages=880,
        kdc="005",
        category="book",
        price=38000,
    )

    # Record + TOON 생성
    record, toon_id = builder.build_with_toon(book_info)

    print("=== TOON ID ===")
    print(toon_id)

    print("\n=== KORMARC XML ===")
    print(record.to_xml())

    print("\n=== TOON JSON ===")
    import json

    toon_dict = builder.build_toon_dict(book_info)
    print(json.dumps(toon_dict, indent=2, ensure_ascii=False))
