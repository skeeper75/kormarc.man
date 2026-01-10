"""
국립중앙도서관 Open API 클라이언트

SRU (Search/Retrieve via URL) 인터페이스를 사용하여
도서 정보를 검색하고 KORMARC 레코드를 수집합니다.

참고:
- 국립중앙도서관: https://www.nl.go.kr/
- Open API: https://www.nl.go.kr/nl/search/openApi/search.do
"""

import asyncio
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import quote

import httpx


class NationalLibraryClient:
    """
    국립중앙도서관 Open API 클라이언트

    SRU 인터페이스를 통해 도서 정보를 검색합니다.

    Example:
        >>> client = NationalLibraryClient()
        >>> results = await client.search_by_keyword("파이썬", max_records=10)
        >>> for record in results:
        ...     print(record['title'])
    """

    # SRU 엔드포인트 (국립중앙도서관)
    SRU_ENDPOINT = "https://www.nl.go.kr/NL/search/openApi/srhOpenApi.do"

    # 검색 파라미터
    DEFAULT_OPERATION = "searchRetrieve"
    DEFAULT_VERSION = "1.2"
    DEFAULT_RECORD_SCHEMA = "kormarc"  # KORMARC 형식

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
        delay: float = 0.5,
    ):
        """
        API 클라이언트 초기화

        Args:
            api_key: API 인증키 (없으면 공개 API 사용)
            timeout: 요청 타임아웃 (초)
            delay: 요청 간 지연 시간 (초, API 제한 준수)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.delay = delay
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager 진입"""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager 퇴출"""
        if self._client:
            await self._client.aclose()

    async def _request(
        self,
        params: dict[str, Any],
    ) -> str:
        """
        API 요청 전송

        Args:
            params: 요청 파라미터

        Returns:
            XML 응답 문자열
        """
        if self._client is None:
            raise RuntimeError("Client not initialized. Use async context manager.")

        # 기본 파라미터
        request_params = {
            "operation": self.DEFAULT_OPERATION,
            "version": self.DEFAULT_VERSION,
            "recordSchema": self.DEFAULT_RECORD_SCHEMA,
        }

        # API 키 (있으면)
        if self.api_key:
            request_params["apiKey"] = self.api_key

        # 사용자 파라미터 병합
        request_params.update(params)

        # 요청 전송
        response = await self._client.get(self.SRU_ENDPOINT, params=request_params)
        response.raise_for_status()

        # API 속도 제한 준수
        await asyncio.sleep(self.delay)

        return response.text

    async def search_by_keyword(
        self,
        keyword: str,
        max_records: int = 100,
        start_record: int = 1,
    ) -> list[dict[str, Any]]:
        """
        키워드로 도서 검색

        Args:
            keyword: 검색어
            max_records: 최대 결과 개수
            start_record: 시작 레코드 번호

        Returns:
            검색 결과 리스트
        """
        # CQL (Contextual Query Language) 쿼리
        # 키워드 검색: 모든 필드에서 검색
        cql_query = f"{quote(keyword)}"

        params = {
            "query": cql_query,
            "maximumRecords": max_records,
            "startRecord": start_record,
        }

        xml_response = await self._request(params)

        # XML 파싱
        return self._parse_sru_response(xml_response)

    async def search_by_isbn(
        self,
        isbn: str,
    ) -> dict[str, Any] | None:
        """
        ISBN으로 도서 검색

        Args:
            isbn: ISBN (10 또는 13자리)

        Returns:
            도서 정보 또는 None
        """
        # ISBN 검색 CQL
        # ISBN 필드: 020$a
        cql_query = f"020.a={quote(isbn)}"

        params = {
            "query": cql_query,
            "maximumRecords": 1,
            "startRecord": 1,
        }

        xml_response = await self._request(params)
        results = self._parse_sru_response(xml_response)

        return results[0] if results else None

    async def search_by_title(
        self,
        title: str,
        max_records: int = 100,
        start_record: int = 1,
    ) -> list[dict[str, Any]]:
        """
        제목으로 도서 검색

        Args:
            title: 제목 (일부 일치 가능)
            max_records: 최대 결과 개수
            start_record: 시작 레코드 번호

        Returns:
            검색 결과 리스트
        """
        # 제목 검색: 245$a 필드
        cql_query = f"245.a={quote(title)}"

        params = {
            "query": cql_query,
            "maximumRecords": max_records,
            "startRecord": start_record,
        }

        xml_response = await self._request(params)
        return self._parse_sru_response(xml_response)

    async def search_by_author(
        self,
        author: str,
        max_records: int = 100,
        start_record: int = 1,
    ) -> list[dict[str, Any]]:
        """
        저자명으로 도서 검색

        Args:
            author: 저자명
            max_records: 최대 결과 개수
            start_record: 시작 레코드 번호

        Returns:
            검색 결과 리스트
        """
        # 저자 검색: 100$a 필드
        cql_query = f"100.a={quote(author)}"

        params = {
            "query": cql_query,
            "maximumRecords": max_records,
            "startRecord": start_record,
        }

        xml_response = await self._request(params)
        return self._parse_sru_response(xml_response)

    async def search_by_kdc(
        self,
        kdc: str,
        max_records: int = 100,
        start_record: int = 1,
    ) -> list[dict[str, Any]]:
        """
        KDC 분류로 도서 검색

        Args:
            kdc: KDC 분류코드 (예: 005, 813)
            max_records: 최대 결과 개수
            start_record: 시작 레코드 번호

        Returns:
            검색 결과 리스트
        """
        # KDC 검색: 082$a 또는 650$a
        cql_query = f"082.a={quote(kdc)}"

        params = {
            "query": cql_query,
            "maximumRecords": max_records,
            "startRecord": start_record,
        }

        xml_response = await self._request(params)
        return self._parse_sru_response(xml_response)

    def _parse_sru_response(self, xml_response: str) -> list[dict[str, Any]]:
        """
        SRU XML 응답 파싱

        Args:
            xml_response: SRU XML 응답

        Returns:
            파싱된 레코드 리스트
        """
        import xml.etree.ElementTree as ET

        # XML 파싱
        root = ET.fromstring(xml_response)

        # 네임스페이스
        ns = {
            "srw": "http://www.loc.gov/zing/srw/",
            "marc": "http://www.loc.gov/MARC21/slim",
        }

        records = []

        # 레코드 추출
        for marc_record in root.findall(".//marc:record", ns):
            record_data = self._parse_marc_record(marc_record, ns)
            if record_data:
                records.append(record_data)

        return records

    def _parse_marc_record(
        self, marc_record: ET.Element, ns: dict[str, str]
    ) -> dict[str, Any] | None:
        """
        MARC 레코드 파싱

        Args:
            marc_record: MARC record XML 요소
            ns: 네임스페이스

        Returns:
            파싱된 레코드 데이터
        """
        # 리더
        leader_elem = marc_record.find("marc:leader", ns)
        leader = leader_elem.text if leader_elem is not None else ""

        # 제어 필드
        control_fields = {}
        for controlfield in marc_record.findall("marc:controlfield", ns):
            tag = controlfield.get("tag")
            if tag:
                control_fields[tag] = controlfield.text or ""

        # 데이터 필드
        data_fields = {}
        for datafield in marc_record.findall("marc:datafield", ns):
            tag = datafield.get("tag")
            if tag:
                subfields = {}
                for subfield in datafield.findall("marc:subfield", ns):
                    code = subfield.get("code")
                    if code:
                        subfields[code] = subfield.text or ""
                data_fields[tag] = {
                    "ind1": datafield.get("ind1", ""),
                    "ind2": datafield.get("ind2", ""),
                    "subfields": subfields,
                }

        # 주요 정보 추출
        isbn = self._extract_isbn(data_fields)
        title = self._extract_title(data_fields)
        author = self._extract_author(data_fields)
        publisher = self._extract_publisher(data_fields)
        pub_year = self._extract_pub_year(data_fields)
        pages = self._extract_pages(data_fields)
        kdc = self._extract_kdc(data_fields)

        return {
            "leader": leader,
            "control_fields": control_fields,
            "data_fields": data_fields,
            # 추출된 주요 정보
            "isbn": isbn,
            "title": title,
            "author": author,
            "publisher": publisher,
            "pub_year": pub_year,
            "pages": pages,
            "kdc": kdc,
        }

    def _extract_isbn(self, data_fields: dict) -> str:
        """ISBN 추출 (020 필드)"""
        if "020" in data_fields:
            subfields = data_fields["020"]["subfields"]
            return subfields.get("a", "")
        return ""

    def _extract_title(self, data_fields: dict) -> str:
        """제목 추출 (245 필드)"""
        if "245" in data_fields:
            subfields = data_fields["245"]["subfields"]
            return subfields.get("a", "")
        return ""

    def _extract_author(self, data_fields: dict) -> str:
        """저자 추출 (100 필드)"""
        if "100" in data_fields:
            subfields = data_fields["100"]["subfields"]
            return subfields.get("a", "")
        return ""

    def _extract_publisher(self, data_fields: dict) -> str:
        """출판사 추출 (260 필드)"""
        if "260" in data_fields:
            subfields = data_fields["260"]["subfields"]
            return subfields.get("b", "")
        return ""

    def _extract_pub_year(self, data_fields: dict) -> str:
        """발행년 추출 (260 필드)"""
        if "260" in data_fields:
            subfields = data_fields["260"]["subfields"]
            year = subfields.get("c", "")
            # 'c2025' 형식에서 숫자만 추출
            return "".join(filter(str.isdigit, year))
        return ""

    def _extract_pages(self, data_fields: dict) -> int | None:
        """페이지수 추출 (300 필드)"""
        if "300" in data_fields:
            subfields = data_fields["300"]["subfields"]
            pages = subfields.get("a", "")
            # '880p' 형식에서 숫자만 추출
            page_str = "".join(filter(str.isdigit, pages))
            return int(page_str) if page_str else None
        return None

    def _extract_kdc(self, data_fields: dict) -> str:
        """KDC 추출 (082 필드)"""
        if "082" in data_fields:
            subfields = data_fields["082"]["subfields"]
            return subfields.get("a", "")
        return ""


class BookCollector:
    """
    대규모 도서 수집기

    국립도서관 API를 통해 카테고리별 도서를 수집합니다.

    Example:
        >>> collector = BookCollector()
        >>> await collector.initialize()
        >>> records = await collector.collect_by_kdc("005", max_records=100)
        >>> await collector.save_to_database("kormarc.db")
    """

    def __init__(
        self,
        api_key: str | None = None,
        delay: float = 1.0,
    ):
        """
        수집기 초기화

        Args:
            api_key: API 인증키
            delay: 요청 간 지연 시간 (초)
        """
        self.api_key = api_key
        self.delay = delay
        self.client: NationalLibraryClient | None = None
        self.collected_records: list[dict[str, Any]] = []

    async def initialize(self) -> None:
        """수집기 초기화"""
        self.client = NationalLibraryClient(
            api_key=self.api_key,
            delay=self.delay,
        )
        await self.client.__aenter__()

    async def close(self) -> None:
        """수집기 종료"""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def collect_by_keyword(
        self,
        keyword: str,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """
        키워드로 도서 수집

        Args:
            keyword: 검색어
            max_records: 최대 수집 개수

        Returns:
            수집된 레코드 리스트
        """
        if self.client is None:
            raise RuntimeError("Collector not initialized")

        records = []
        batch_size = 100  # SRU 기본 최대값

        for start in range(1, max_records + 1, batch_size):
            current_max = min(batch_size, max_records - len(records))

            results = await self.client.search_by_keyword(
                keyword=keyword,
                max_records=current_max,
                start_record=start,
            )

            if not results:
                break

            records.extend(results)
            self.collected_records.extend(results)

            print(f"수집 진행: {len(records)}/{max_records} 건")

            if len(results) < current_max:
                # 더 이상 결과 없음
                break

        return records

    async def collect_by_kdc(
        self,
        kdc: str,
        max_records: int = 100,
    ) -> list[dict[str, Any]]:
        """
        KDC 분류로 도서 수집

        Args:
            kdc: KDC 분류코드
            max_records: 최대 수집 개수

        Returns:
            수집된 레코드 리스트
        """
        if self.client is None:
            raise RuntimeError("Collector not initialized")

        records = []
        batch_size = 100

        for start in range(1, max_records + 1, batch_size):
            current_max = min(batch_size, max_records - len(records))

            results = await self.client.search_by_kdc(
                kdc=kdc,
                max_records=current_max,
                start_record=start,
            )

            if not results:
                break

            records.extend(results)
            self.collected_records.extend(results)

            print(f"[KDC {kdc}] 수집 진행: {len(records)}/{max_records} 건")

            if len(results) < current_max:
                break

        return records

    async def collect_by_category(
        self,
        category: str,
        max_records_per_kdc: int = 50,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        카테고리별 도서 수집

        Args:
            category: 카테고리 (book, serial, academic, comic)
            max_records_per_kdc: 각 KDC당 최대 수집 개수

        Returns:
            KDC별 수집된 레코드 딕셔너리
        """
        # 카테고리별 KDC 범위
        category_kdc_ranges = {
            "book": ["000", "100", "200", "300", "400", "500", "600", "700", "800", "900"],
            "serial": ["050", "150", "250", "350", "450", "550", "650", "750", "850", "950"],
            "academic": ["000", "100", "200", "300", "400", "500", "600", "700", "800", "900"],
            "comic": ["800"],  # 문학 > 만화
        }

        kdc_codes = category_kdc_ranges.get(category, [])

        results = {}

        for kdc_prefix in kdc_codes:
            # 세부 KDC 코드 생성 (예: 000 -> 000~009)
            for i in range(10):
                kdc = f"{kdc_prefix[:-1]}{i}" if len(kdc_prefix) == 3 else kdc_prefix

                records = await self.collect_by_kdc(
                    kdc=kdc,
                    max_records=max_records_per_kdc // 10,
                )

                if records:
                    results[kdc] = records

        return results

    async def save_to_database(
        self,
        db_path: str = "kormarc.db",
        data_source: str = "national_library_api",
    ) -> int:
        """
        수집된 레코드를 데이터베이스에 저장

        Args:
            db_path: 데이터베이스 파일 경로
            data_source: 데이터 소스标识

        Returns:
            저장된 레코드 수
        """
        from kormarc.db import KORMARCDatabase
        from kormarc.kormarc_builder import BookInfo, KORMARCBuilder

        if not self.collected_records:
            print("저장할 레코드가 없습니다.")
            return 0

        db = KORMARCDatabase(db_path)
        await db.initialize()

        builder = KORMARCBuilder()
        saved_count = 0

        for api_record in self.collected_records:
            try:
                # API 레코드를 BookInfo로 변환
                book = BookInfo(
                    isbn=api_record["isbn"] or f"unknown_{saved_count}",
                    title=api_record["title"] or "제목 없음",
                    author=api_record.get("author"),
                    publisher=api_record.get("publisher"),
                    pub_year=api_record.get("pub_year"),
                    pages=api_record.get("pages"),
                    kdc=api_record.get("kdc"),
                    category="book",  # 기본값
                )

                # TOON JSON 생성
                toon_dict = builder.build_toon_dict(book)

                # 데이터베이스 저장
                await db.save_record(
                    toon_id=toon_dict["toon_id"],
                    record_data=toon_dict,
                    scraped_at=data_source,
                    data_source=data_source,
                )

                saved_count += 1

                if saved_count % 100 == 0:
                    print(f"저장 진행: {saved_count}/{len(self.collected_records)} 건")

            except Exception as e:
                print(f"저장 실패: {api_record.get('isbn', 'unknown')} - {e}")
                continue

        await db.close()

        print(f"총 {saved_count}건 저장 완료")
        return saved_count


# 모듈 레벨 테스트
if __name__ == "__main__":
    import asyncio

    async def test_api_client():
        """API 클라이언트 테스트"""
        async with NationalLibraryClient() as client:
            # ISBN 검색 테스트
            result = await client.search_by_isbn("9788960777330")

            if result:
                print(f"제목: {result.get('title')}")
                print(f"저자: {result.get('author')}")
                print(f"KDC: {result.get('kdc')}")
            else:
                print("검색 결과 없음")

    # asyncio.run(test_api_client())
    print("API 클라이언트 테스트 (실제 API 호출 필요시 주석 해제)")
