# 국립중앙도서관 스크래퍼 업데이트 요약

## 업데이트 개요

실제 국립중앙도서관 서지정보유통지원시스템(https://www.nl.go.kr/seoji/)의 웹사이트 구조를 분석하고, 스크래퍼를 실제 작동하도록 업데이트했습니다.

**업데이트 날짜**: 2026-01-10
**대상 파일**: `src/kormarc/scraper.py`

---

## 주요 변경 사항

### 1. URL 및 엔드포인트 업데이트

#### Before (잘못된 URL)
```python
BASE_URL = "https://www.nl.go.kr"
SEARCH_URL = f"{BASE_URL}/nis/searchView.do?menuKey=ni"
DETAIL_URL = f"{BASE_URL}/nis/detailView.do?menuKey=ni"
```

#### After (실제 URL)
```python
BASE_URL = "https://www.nl.go.kr/seoji"
SEARCH_URL = f"{BASE_URL}/contents/S80100000000.do"  # 통합검색 페이지
DETAIL_URL = f"{BASE_URL}/contents/S80101000000.do"  # 상세정보 페이지
```

**변경 이유**: 국립중앙도서관의 서지정보 시스템은 `/seoji/` 하위에 있으며, `/nis/` 경로는 존재하지 않음.

---

### 2. 검색 방식 변경

#### Before (직접 URL 접근)
```python
search_url = f"{self.SEARCH_URL}&keyword={quote(keyword)}"
await self._page.goto(search_url)
```

#### After (검색 폼 사용)
```python
# 메인 페이지 접속
await self._page.goto(self.BASE_URL)

# 검색 폼에서 검색어 입력
search_input = await self._page.query_selector('input[name="schStr"]')
await search_input.fill(keyword)

# Enter 키로 검색 실행
await search_input.press("Enter")
```

**변경 이유**:
- URL 파라미터로 직접 접근 시 JavaScript 리다이렉트로 인해 페이지가 로드되지 않음
- 검색 폼을 통한 자연스러운 검색이 필요

---

### 3. 브라우저 자동화 감지 회피

#### 추가된 설정
```python
# 브라우저 옵션
args=[
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
]

# Context 생성
context = await self._browser.new_context(
    user_agent="Mozilla/5.0 ...",
    viewport={"width": 1920, "height": 1080},
    locale="ko-KR",
)

# JavaScript로 webdriver 속성 제거
await self._page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
""")
```

**변경 이유**: 웹사이트가 Playwright 자동화를 감지하여 차단할 수 있음.

---

### 4. 검색 결과 선택자 업데이트

#### Before (가정된 선택자)
```python
result_items = await self._page.query_selector_all(
    ".searchResult_list li, .bookList li, .resultItem"
)
title_elem = await item.query_selector("a.title, .title a, h3 a")
```

#### After (실제 HTML 구조 기반)
```python
# 검색 결과 컨테이너
result_container = await self._page.query_selector(
    "#resultList_div, .resultList, #content_body"
)

# 각 결과 항목
result_items = await self._page.query_selector_all(".resultData")

# 제목 링크
title_elem = await item.query_selector(".tit a")
```

**실제 HTML 구조**:
```html
<div id="resultList_div" class="resultList">
    <div class="resultData">
        <div class="tit">
            <a href="#link" onclick="fn_goView('9791127047788','230336289,')">
                [종이책] 1. 파이썬 프로그래밍 심화3
            </a>
        </div>
        <ul class="dot-list">
            <li>저자 : ㈜크레버스</li>
            <li>발행처: (주식회사)크레버스</li>
            <li>ISBN: 979-11-270-4778-8 (63000)</li>
        </ul>
    </div>
</div>
```

---

### 5. 메타데이터 추출 로직 개선

#### 새로운 추출 방식

```python
# onclick 속성에서 ISBN과 제어번호 추출
onclick_value = await title_elem.get_attribute("onclick")
# 예: fn_goView('9791127047788','230336289,')
onclick_match = re.search(r"fn_goView\('([^']+)','([^']+)'", onclick_value)
if onclick_match:
    isbn = onclick_match.group(1)
    control_number = onclick_match.group(2).replace(",", "").strip()

# dot-list에서 메타데이터 추출
dot_list = await item.query_selector(".dot-list")
list_items = await dot_list.query_selector_all("li")
for li in list_items:
    li_text = await li.inner_text()
    if "저자" in li_text:
        author = li_text.replace("저자", "").replace(":", "").strip()
    elif "발행처" in li_text:
        publisher = li_text.replace("발행처", "").replace(":", "").strip()
    elif "ISBN" in li_text:
        isbn_full = li_text.replace("ISBN", "").replace(":", "").strip()
```

**개선 사항**:
- `onclick` 속성에서 ISBN과 제어번호를 직접 추출 (더 정확함)
- `.dot-list` 구조에서 체계적으로 메타데이터 파싱
- 정규표현식으로 발행년도 추출

---

### 6. 에러 처리 강화

#### 추가된 에러 처리
```python
# 검색 입력란 확인
search_input = await self._page.query_selector('input[name="schStr"]')
if not search_input:
    print("검색 입력란을 찾을 수 없습니다.")
    return results

# 검색 결과 컨테이너 확인
if not result_container:
    print("검색 결과 컨테이너를 찾을 수 없습니다.")
    await self._page.screenshot(path="debug_search_page.png")
    return records

# 예외 처리 및 traceback
except Exception as e:
    print(f"검색 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()
```

**개선 사항**:
- 각 단계에서 요소 존재 여부 확인
- 디버깅을 위한 스크린샷 자동 저장
- 상세한 에러 메시지 및 traceback 출력

---

## 테스트 결과

### 테스트 환경
- **브라우저**: Chromium (Playwright)
- **검색어**: "파이썬"
- **페이지 수**: 1
- **최대 레코드**: 5

### 성공 결과
```
검색 결과: 5건

[1] [종이책] 1. 파이썬 프로그래밍 심화3
    저자: ㈜크레버스
    출판사: (주식회사)크레버스
    발행년: 2026
    ISBN: 9791127047788
    제어번호: 230336289

[2] [종이책] 2. 파이썬 프로그래밍 심화1
    저자: ㈜크레버스
    출판사: (주식회사)크레버스
    발행년: 2026
    ISBN: 9791127047764
    제어번호: 230336291

... (생략)

✅ 검색 성공!
```

---

## 추가 개선 사항

### 1. 텍스트 기반 메타데이터 추출 함수

새로운 헬퍼 함수 `_extract_metadata_from_text()` 추가:
- 정규표현식으로 저자, 발행처, 발행년, ISBN, 제어번호 추출
- DOM 선택자가 실패할 경우 대체 방법으로 사용

### 2. 전체 텍스트 파싱 대체 방법

`_parse_text_results()` 함수 추가:
- 선택자로 결과를 찾지 못할 경우 전체 텍스트에서 파싱
- 휴리스틱 방식으로 레코드 구분

### 3. 페이징 버튼 선택자 개선

다양한 페이징 버튼 패턴 지원:
```python
next_selectors = [
    'a:has-text("다음")',
    'a:has-text(">")',
    'a.paging-next',
    '.nextPage',
    '.pageBtn.next',
    'a[title="다음"]',
]
```

---

## 알려진 제약사항

### 1. 상세 페이지 접근 제한
- 현재 검색 결과의 `href`가 `#link`로 되어 있어 직접 접근 불가
- `onclick` 이벤트로 상세 페이지 이동 필요
- ISBN 검색(`search_by_isbn`)은 추가 구현 필요

### 2. 동적 콘텐츠 로딩
- JavaScript 렌더링으로 인해 5초 대기 시간 필요
- `wait_until="networkidle"` 대신 `domcontentloaded` 사용

### 3. 세션 관리
- 메인 페이지 접속 후 검색해야 세션 확립
- 직접 URL 접근은 작동하지 않음

---

## 사용 예제

### 기본 사용법
```python
from kormarc.scraper import NationalLibraryScraper

async with NationalLibraryScraper(headless=True) as scraper:
    results = await scraper.search_by_keyword("파이썬", max_pages=1, max_records=10)

    for record in results:
        print(f"제목: {record['title']}")
        print(f"저자: {record['author']}")
        print(f"ISBN: {record['isbn']}")
```

### 디버깅 모드
```python
# 브라우저 표시 + 느린 동작
async with NationalLibraryScraper(headless=False, slow_mo=500) as scraper:
    results = await scraper.search_by_keyword("Python")
```

---

## 파일 구조

### 수정된 파일
- `src/kormarc/scraper.py` - 주요 스크래퍼 로직

### 테스트 파일
- `test_scraper_real.py` - 실제 웹사이트 테스트
- `test_scraper_simple.py` - HTML 구조 확인용 테스트

### 생성된 파일
- `debug_search_page.png` - 디버깅용 스크린샷
- `search_result_page.html` - 검색 결과 HTML 저장
- `search_result_page.png` - 검색 결과 스크린샷

---

## 향후 개선 계획

1. **상세 페이지 스크래핑 구현**
   - `onclick` 이벤트 시뮬레이션
   - KORMARC 레코드 전체 추출

2. **ISBN 검색 개선**
   - `search_by_isbn()` 메서드 재구현
   - 직접 상세 페이지 접근 로직

3. **대규모 수집 최적화**
   - 페이징 처리 개선
   - 속도 제한(rate limiting) 추가
   - 재시도 로직 강화

4. **데이터 검증**
   - ISBN 유효성 검사
   - 누락된 필드 감지 및 경고

---

## 참고 자료

- **국립중앙도서관 서지정보**: https://www.nl.go.kr/seoji/
- **Playwright 문서**: https://playwright.dev/python/
- **KORMARC 형식**: `docs/NOWON_KORMARC_RULES.md`

---

## 작성자

**프로젝트**: kormarc.man
**업데이트 담당**: Claude Code Agent
**버전**: 1.0.0
