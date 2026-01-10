"""
TOON 생성기 구현

Timestamp-Ordered Object Notation (TOON) 생성기
TypeID/ULID 표준 기반의 KORMARC 레코드 식별자 생성

명세: docs/TOON_SPEC.md
표준:
- ULID: https://github.com/ulid/spec
- TypeID: UUIDv7 with prefix
- Crockford's Base32
"""

import os
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime


class TOONValidationError(Exception):
    """TOON 검증 실패 예외"""

    pass


# Crockford's Base32 알파벳
BASE32_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
BASE32_DECODE_MAP = {
    **{c: i for i, c in enumerate(BASE32_ALPHABET)},
    **{c.lower(): i for i, c in enumerate(BASE32_ALPHABET)},
    # 대체 문자 매핑
    "i": 1,
    "l": 1,
    "o": 0,
}


def encode_base32(data: bytes) -> str:
    """
    Crockford's Base32로 인코딩

    Args:
        data: 인코딩할 바이트 데이터

    Returns:
        Base32로 인코딩된 문자열

    Example:
        >>> encode_base32(b'\\x01\\x23\\x45\\x67\\x89\\xAB')
        '01HZR9SYXR'
    """
    result = []
    buffer = 0
    bits_left = 0

    for byte in data:
        buffer = (buffer << 8) | byte
        bits_left += 8

        while bits_left >= 5:
            bits_left -= 5
            index = (buffer >> bits_left) & 0x1F
            result.append(BASE32_ALPHABET[index])

    if bits_left > 0:
        index = (buffer << (5 - bits_left)) & 0x1F
        result.append(BASE32_ALPHABET[index])

    return "".join(result)


def decode_base32(encoded: str) -> bytes:
    """
    Crockford's Base32 디코딩

    Args:
        encoded: Base32로 인코딩된 문자열

    Returns:
        디코딩된 바이트 데이터

    Raises:
        ValueError: 잘못된 Base32 문자열

    Example:
        >>> decode_base32("01HZR9SYXR")
        b'\\x01\\x23\\x45\\x67\\x89\\xAB'
    """
    encoded = encoded.upper().replace("-", "").replace(" ", "")

    # 버퍼와 비트 카운터 초기화
    buffer = 0
    bits_left = 0
    result = []

    for char in encoded:
        if char not in BASE32_DECODE_MAP:
            raise ValueError(f"Invalid Base32 character: {char}")

        # 현재 문자를 버퍼에 추가
        buffer = (buffer << 5) | BASE32_DECODE_MAP[char]
        bits_left += 5

        # 8비트(1바이트)가 모이면 결과에 추가
        while bits_left >= 8:
            bits_left -= 8
            result.append((buffer >> bits_left) & 0xFF)

    return bytes(result)


@dataclass
class TOONInfo:
    """TOON 식별자 정보"""

    type: str
    """전체 타입 (예: kormarc_book)"""

    subtype: str
    """서브타입 (예: book)"""

    ulid: str
    """ULID 부분 (26자)"""

    timestamp_ms: int
    """타임스탬프 (밀리초)"""

    created_at: datetime
    """생성 시간"""

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "type": self.type,
            "subtype": self.subtype,
            "ulid": self.ulid,
            "timestamp_ms": self.timestamp_ms,
            "created_at": self.created_at.isoformat(),
        }


class TOONGenerator:
    """
    TOON 식별자 생성기

    Example:
        >>> generator = TOONGenerator()
        >>> toon_id = generator.generate("kormarc_book")
        >>> print(toon_id)
        'kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y'
    """

    # ULID 패턴: 26자 Base32
    ULID_PATTERN = re.compile(r"^[0-9A-HJ-KM-NP-TV-Z]{26}$", re.IGNORECASE)

    # TOON 패턴: prefix_26자리ULID
    # kormarc_book, kormarc_serial 등의 형식 지원
    TOON_PATTERN = re.compile(r"^([a-z]+(?:_[a-z]+)*)_([0-9A-HJ-KM-NP-TV-Z]{26})$", re.IGNORECASE)

    def __init__(self):
        """TOON 생성기 초기화"""
        self._validate_alphabet()

    def _validate_alphabet(self):
        """Base32 알파벳 검증"""
        assert len(BASE32_ALPHABET) == 32
        assert "I" not in BASE32_ALPHABET
        assert "L" not in BASE32_ALPHABET
        assert "O" not in BASE32_ALPHABET
        assert "U" not in BASE32_ALPHABET

    def generate(
        self, record_type: str, timestamp_ms: int | None = None, random_bytes: bytes | None = None
    ) -> str:
        """
        TOON 식별자 생성

        Args:
            record_type: 레코드 타입 (예: kormarc_book)
            timestamp_ms: 커스텀 타임스탬프 (밀리초, 테스트용)
            random_bytes: 커스텀 난수 (테스트용)

        Returns:
            TOON 식별자

        Example:
            >>> generator = TOONGenerator()
            >>> toon_id = generator.generate("kormarc_book")
            >>> assert toon_id.startswith("kormarc_book_")
        """
        # 1. 타임스탬프 생성 (48-bit)
        if timestamp_ms is None:
            timestamp_ms = int(time.time() * 1000)
        timestamp_ms = timestamp_ms & 0xFFFFFFFFFFFF

        # 2. 난수 생성 (80-bit)
        if random_bytes is None:
            random_bytes = os.urandom(10)
        assert len(random_bytes) == 10, "Random bytes must be 10 bytes"

        # 3. 결합
        data = timestamp_ms.to_bytes(6, byteorder="big") + random_bytes

        # 4. Base32 인코딩
        ulid = encode_base32(data).upper()

        # 5. 패딩 제거 (26자리)
        ulid = ulid[:26]

        # 6. 접두사 추가
        return f"{record_type}_{ulid}"

    def parse(self, toon_id: str) -> dict:
        """
        TOON 식별자 파싱

        Args:
            toon_id: TOON 식별자

        Returns:
            파싱된 정보 딕셔너리

        Raises:
            TOONValidationError: 잘못된 TOON 형식

        Example:
            >>> generator = TOONGenerator()
            >>> info = generator.parse("kormarc_book_01HZR9SYXR9VQJXJ9X8Y8Y8Y8Y")
            >>> assert info["type"] == "kormarc_book"
        """
        toon_id = toon_id.strip()

        # 소문자로 정규화
        match = self.TOON_PATTERN.match(toon_id.lower())
        if not match:
            raise TOONValidationError(f"Invalid TOON format: {toon_id}")

        type_prefix, ulid = match.groups()

        # ULID 디코딩
        decoded = decode_base32(ulid)

        # 타임스탬프 추출 (처음 6바이트)
        timestamp_ms = int.from_bytes(decoded[:6], byteorder="big")

        # 생성 시간 변환
        created_at = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)

        # 타입 접두서와 서브타입 분리
        type_parts = type_prefix.split("_")
        if len(type_parts) >= 2:
            subtype = "_".join(type_parts[1:])
        else:
            subtype = ""

        return {
            "type": type_prefix.lower(),
            "subtype": subtype.lower(),
            "ulid": ulid.upper(),
            "timestamp_ms": timestamp_ms,
            "created_at": created_at,
        }

    def validate(self, toon_id: str) -> bool:
        """
        TOON 식별자 검증

        Args:
            toon_id: 검증할 TOON 식별자

        Returns:
            유효성 여부

        Example:
            >>> generator = TOONGenerator()
            >>> toon_id = generator.generate("kormarc_book")
            >>> assert generator.validate(toon_id) is True
        """
        try:
            self.parse(toon_id)
            return True
        except (TOONValidationError, ValueError):
            return False

    def extract_timestamp(self, toon_id: str) -> datetime:
        """
        TOON에서 타임스탬프 추출

        Args:
            toon_id: TOON 식별자

        Returns:
            생성 시간

        Example:
            >>> generator = TOONGenerator()
            >>> toon_id = generator.generate("kormarc_book")
            >>> ts = generator.extract_timestamp(toon_id)
            >>> assert isinstance(ts, datetime)
        """
        parsed = self.parse(toon_id)
        return parsed["created_at"]


def determine_record_type(record) -> str:
    """
    KORMARC 레코드에서 TOON 타입 결정

    Args:
        record: KORMARC 레코드 객체

    Returns:
        TOON 타입 문자열

    Example:
        >>> record_type = determine_record_type(kormarc_record)
        >>> assert record_type in ["kormarc_book", "kormarc_serial", ...]
    """
    # 리더에서 bibliographic level 확인
    bib_level = getattr(record.leader, "bibliographic_level", None)

    # 제어 필드 008 확인
    field_008 = None
    if hasattr(record, "get_control_field"):
        field_008 = record.get_control_field("008")
    elif hasattr(record, "control_fields"):
        field_008 = next((f for f in record.control_fields if f.tag == "008"), None)

    if not field_008:
        return "kormarc_unknown"

    # 레코드 타입 결정
    if bib_level == "m":
        return "kormarc_book"
    elif bib_level == "s":
        return "kormarc_serial"
    elif bib_level == "a":
        # MONOGRAPHIC COMPONENT PART (학술지 등)
        return "kormarc_academic"
    elif bib_level in ("c", "d"):
        # COLLECTION / DIVISION (만화 등)
        return "kormarc_comic"
    else:
        return "kormarc_unknown"


def toon_to_json(record, toon_id: str) -> dict:
    """
    TOON과 KORMARC 레코드를 JSON으로 변환

    Args:
        record: KORMARC 레코드 객체
        toon_id: TOON 식별자

    Returns:
        JSON 직렬화 가능한 딕셔너리

    Example:
        >>> json_data = toon_to_json(record, toon_id)
        >>> assert "toon_id" in json_data
        >>> assert "type" in json_data
    """
    generator = TOONGenerator()
    parsed = generator.parse(toon_id)

    # 원본 KORMARC 데이터
    raw_kormarc = str(record)

    # 파싱된 데이터
    parsed_data = {
        "leader": {
            "record_length": record.leader.record_length,
            "record_status": record.leader.record_status,
            "type_of_record": record.leader.type_of_record,
            "bibliographic_level": record.leader.bibliographic_level,
        },
        "control_fields": [
            {"tag": f.tag, "data": f.data} for f in getattr(record, "control_fields", [])
        ],
        "data_fields": [
            {
                "tag": f.tag,
                "indicators": f.indicator1 + f.indicator2,
                "subfields": [{"code": s.code, "data": s.data} for s in f.subfields],
            }
            for f in getattr(record, "data_fields", [])
        ],
    }

    return {
        "toon_id": toon_id,
        "timestamp": parsed["created_at"].isoformat(),
        "type": parsed["type"],
        "isbn": extract_isbn(record),
        "raw_kormarc": raw_kormarc,
        "parsed": parsed_data,
    }


def extract_isbn(record) -> str:
    """
    KORMARC 레코드에서 ISBN 추출

    Args:
        record: KORMARC 레코드 객체

    Returns:
        ISBN 문자열 (없으면 빈 문자열)
    """
    # 필드 020 또는 024에서 ISBN 찾기
    if hasattr(record, "data_fields"):
        for field in record.data_fields:
            if field.tag in ("020", "024"):
                for subfield in field.subfields:
                    if subfield.code == "a":
                        # ISBN 정제 (하이픈, 공백 제거)
                        isbn = subfield.data.replace("-", "").replace(" ", "")
                        if isbn.isdigit():
                            return isbn
    return ""


# 모듈 레벨 테스트
if __name__ == "__main__":
    # 간단한 테스트
    generator = TOONGenerator()

    # TOON 생성
    toon_id = generator.generate("kormarc_book")
    print(f"Generated TOON: {toon_id}")

    # TOON 파싱
    parsed = generator.parse(toon_id)
    print(f"Parsed TOON: {parsed}")

    # TOON 검증
    is_valid = generator.validate(toon_id)
    print(f"Valid: {is_valid}")

    # 타임스탬프 추출
    timestamp = generator.extract_timestamp(toon_id)
    print(f"Timestamp: {timestamp}")
