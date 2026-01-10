# SPEC-WEB-001 인수 기준 (Acceptance Criteria)

## 문서 메타데이터

- **SPEC ID**: SPEC-WEB-001
- **제목**: KORMARC 웹 애플리케이션 인수 기준
- **작성자**: 지니
- **작성일**: 2026-01-11
- **버전**: 1.0.0

---

## 테스트 시나리오 (Test Scenarios)

### Scenario 1: 성공적인 KORMARC 생성 (기본 플로우)

```gherkin
Given 사용자가 KORMARC 웹 애플리케이션에 접속했다
  And 도서 정보 입력 폼이 표시되었다
When 사용자가 다음 정보를 입력한다:
  | 필드           | 값                        |
  |----------------|---------------------------|
  | ISBN           | 9791162233149             |
  | 제목           | Python 프로그래밍         |
  | 저자           | 박응용                    |
  | 출판사         | 한빛미디어                |
  | 발행년         | 2025                      |
  And "KORMARC 생성" 버튼을 클릭한다
Then 시스템은 BookInfo를 KORMARC 레코드로 변환한다
  And KORMARC JSON/XML 미리보기를 표시한다
  And 040 필드가 노란색으로 하이라이트된다
  And "JSON 다운로드", "XML 다운로드" 버튼이 활성화된다
  And 5단계 검증 결과가 모두 "✅ 통과"로 표시된다
```

**예상 결과**:

- KORMARC JSON 구조:
  ```json
  {
    "leader": "00000nam  2200000   450 ",
    "fields": [
      {"tag": "001", "value": "..."},
      {"tag": "020", "subfields": [{"code": "a", "value": "9791162233149"}]},
      {"tag": "040", "subfields": [
        {"code": "a", "value": "NLK"},
        {"code": "b", "value": "kor"},
        {"code": "c", "value": "(NLK)"},
        {"code": "d", "value": "NLK"},
        {"code": "e", "value": "KORMARC2014"}
      ]},
      {"tag": "245", "subfields": [{"code": "a", "value": "Python 프로그래밍"}]}
    ]
  }
  ```

**검증 포인트**:
- [ ] ISBN 체크섬 검증 통과
- [ ] 040 필드 형식이 노원구 시방서 준수
- [ ] JSON과 XML 모두 생성됨
- [ ] 미리보기에서 040 필드 하이라이트 확인

---

### Scenario 2: ISBN DB 부재 시 Playwright 스크래핑

```gherkin
Given 사용자가 ISBN "9788970509143"을 입력했다
  And 해당 ISBN이 로컬 DB에 존재하지 않는다
When 사용자가 "자동 정보 수집" 버튼을 클릭한다
Then 시스템은 "국립중앙도서관에서 정보 수집 중..." 메시지를 표시한다
  And Playwright가 국립중앙도서관 웹사이트에 접속한다
  And ISBN을 검색하여 도서 정보를 추출한다
  And 추출된 정보 (제목, 저자, 출판사, 발행년)를 폼에 자동 입력한다
  And 수집된 정보를 로컬 DB에 저장한다
  And "정보 수집 완료" 성공 메시지를 표시한다
```

**Playwright 스크래핑 단계**:

1. **검색 페이지 접속**: `https://www.nl.go.kr/`
2. **ISBN 입력**: 검색창에 "9788970509143" 입력
3. **검색 실행**: 검색 버튼 클릭
4. **결과 대기**: `.book-item` 셀렉터 대기 (최대 10초)
5. **정보 추출**:
   - 제목: `.book-title` 텍스트
   - 저자: `.book-author` 텍스트
   - 출판사: `.book-publisher` 텍스트
   - 발행년: `.book-year` 텍스트에서 정규식 추출 (`\d{4}`)
6. **DB 저장**: `books` 테이블에 INSERT

**예상 응답** (GET /api/book/search?isbn=9788970509143):

```json
{
  "success": true,
  "source": "scraping",
  "book_info": {
    "isbn": "9788970509143",
    "title": "데이터베이스 설계",
    "author": "김영철",
    "publisher": "한국방송통신대학교출판부",
    "publication_year": 2015
  },
  "collected_at": "2026-01-11T10:30:00Z"
}
```

**검증 포인트**:
- [ ] 로컬 DB 조회 시도 (SELECT 쿼리 실행)
- [ ] DB 미존재 시 Playwright 실행
- [ ] 국립중앙도서관 웹사이트 접속 성공
- [ ] 도서 정보 추출 성공
- [ ] 폼에 자동 입력된 정보 확인
- [ ] DB 저장 확인 (재조회 시 "database" source)
- [ ] 로딩 메시지 표시 및 성공 메시지 표시

---

### Scenario 3: ISBN 검증 실패

```gherkin
Given 사용자가 ISBN 입력 필드에 "123456789012X"를 입력했다
When 시스템이 ISBN 체크섬 검증을 수행한다
Then 입력 필드에 빨간색 테두리가 표시된다
  And "ISBN 체크섬이 올바르지 않습니다. 13자리 숫자를 확인해주세요." 오류 메시지가 표시된다
  And "KORMARC 생성" 버튼이 비활성화된다
```

**ISBN 체크섬 알고리즘**:

1. 처음 12자리 숫자 추출
2. 홀수 자리 (1, 3, 5, ...) × 1, 짝수 자리 (2, 4, 6, ...) × 3
3. 모든 곱의 합계 계산
4. 합계를 10으로 나눈 나머지
5. 10 - 나머지 = 체크섬 (단, 10이면 0)
6. 13번째 자리 숫자와 일치 여부 확인

**예시 검증**:

- 입력: `9791162233149`
- 계산: `(9×1 + 7×3 + 9×1 + 1×3 + 1×1 + 6×3 + 2×1 + 2×3 + 3×1 + 3×3 + 1×1 + 4×3) = 131`
- 나머지: `131 % 10 = 1`
- 체크섬: `10 - 1 = 9`
- 13번째 자리: `9` → **일치 (유효)**

- 입력: `123456789012X` → **형식 오류 (문자 포함)**
- 입력: `1234567890120` → 체크섬 `0`, 실제 `0` → **유효**
- 입력: `1234567890125` → 체크섬 `0`, 실제 `5` → **불일치 (무효)**

**검증 포인트**:
- [ ] 실시간 검증 (디바운스 500ms)
- [ ] 유효하지 않은 ISBN 입력 시 빨간색 테두리
- [ ] 오류 메시지 표시
- [ ] "KORMARC 생성" 버튼 비활성화

---

### Scenario 4: 노원구 040 필드 검증

```gherkin
Given KORMARC 레코드가 생성되었다
When 시스템이 5단계 검증을 수행한다
Then Tier 3 의미 검증에서 040 필드를 확인한다
  And 040 필드 형식이 "040 ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014"인지 검증한다
  And 검증 결과를 "노원구 시방서 준수: ✅ 통과" 상태로 표시한다
```

**노원구 시방서 040 필드 규칙**:

- **$a (원편목기관)**: `NLK` (국립중앙도서관)
- **$b (목록언어)**: `kor` (한국어)
- **$c (변환기관)**: `(NLK)` (괄호 포함)
- **$d (수정기관)**: `NLK`
- **$e (목록규칙)**: `KORMARC2014`

**5단계 검증 구조**:

1. **Tier 1 (구조 검증)**: Leader, 필수 태그 존재 여부
2. **Tier 2 (형식 검증)**: ISBN 형식, 데이터 타입 일치
3. **Tier 3 (의미 검증)**: 040 필드 규칙 준수 (노원구 시방서)
4. **Tier 4 (관계 검증)**: 필드 간 일관성 (예: ISBN과 245 제목)
5. **Tier 5 (품질 검증)**: 데이터 완전성, 중복 제거

**검증 예시**:

- **통과**:
  ```json
  {
    "tag": "040",
    "subfields": [
      {"code": "a", "value": "NLK"},
      {"code": "b", "value": "kor"},
      {"code": "c", "value": "(NLK)"},
      {"code": "d", "value": "NLK"},
      {"code": "e", "value": "KORMARC2014"}
    ]
  }
  ```

- **실패** (변환기관 괄호 누락):
  ```json
  {
    "tag": "040",
    "subfields": [
      {"code": "c", "value": "NLK"}  // 괄호 누락
    ]
  }
  ```

**검증 포인트**:
- [ ] Tier 3 검증 실행
- [ ] 040 필드 각 서브필드 값 확인
- [ ] 노원구 시방서 규칙 준수 확인
- [ ] 검증 결과 UI에 표시 (✅ 또는 ❌)

---

### Scenario 5: 국립중앙도서관 API 우선 정책

```gherkin
Given 국립중앙도서관 오픈 API가 설정되었다
  And 사용자가 ISBN "9788970509143"을 입력했다
When 시스템이 도서 정보를 수집한다
Then 먼저 로컬 DB를 조회한다
  And DB에 없으면 국립중앙도서관 오픈 API를 호출한다
  And API 응답이 성공하면 수집된 정보를 반환한다
But API 호출이 실패하면 (타임아웃, 오류 등)
Then Playwright 스크래핑으로 fallback한다
  And 스크래핑 결과를 반환한다
```

**데이터 수집 순서**:

```
1. 로컬 DB 조회
   ├─ 성공 → 즉시 반환 (source: "database")
   └─ 실패 → 2단계 진행

2. 국립중앙도서관 API 호출
   ├─ 성공 → DB 저장 후 반환 (source: "api")
   └─ 실패 (타임아웃/오류) → 3단계 진행

3. Playwright 스크래핑
   ├─ 성공 → DB 저장 후 반환 (source: "scraping")
   └─ 실패 → 오류 메시지 반환
```

**API 호출 예시** (가상):

```bash
GET https://www.nl.go.kr/openapi/search?isbn=9788970509143&key=YOUR_API_KEY
```

**응답 예시**:

```json
{
  "status": "success",
  "result": {
    "title": "데이터베이스 설계",
    "author": "김영철",
    "publisher": "한국방송통신대학교출판부",
    "pub_year": "2015"
  }
}
```

**Fallback 시나리오**:

- **API 타임아웃** (5초 초과) → Playwright 실행
- **API 오류** (500, 503) → Playwright 실행
- **API 키 없음** → 직접 Playwright 실행 (API 스킵)

**검증 포인트**:
- [ ] 로컬 DB 조회 시도
- [ ] API 호출 시도 (API 키 설정 시)
- [ ] API 성공 시 DB 저장 및 반환
- [ ] API 실패 시 Playwright fallback
- [ ] 각 단계별 `source` 필드 확인 ("database", "api", "scraping")

---

## 추가 인수 기준 (Additional Acceptance Criteria)

### 성능 기준 (Performance Criteria)

- **API 응답 시간**:
  - P50 (중앙값): < 100ms
  - P95 (95 퍼센타일): < 200ms
  - P99 (99 퍼센타일): < 500ms

- **Playwright 스크래핑 시간**:
  - P50: < 3초
  - P95: < 5초
  - P99: < 10초

- **Frontend 초기 로딩**:
  - First Contentful Paint (FCP): < 1.5초
  - Time to Interactive (TTI): < 3.0초
  - Largest Contentful Paint (LCP): < 2.5초

### 품질 기준 (Quality Criteria)

- **테스트 커버리지**:
  - Backend (pytest): ≥85%
  - Frontend (Vitest): ≥80%
  - E2E (Playwright): 핵심 플로우 100%

- **접근성**:
  - WCAG 2.1 AA 준수
  - 키보드 네비게이션: 모든 기능 Tab/Enter로 접근 가능
  - 스크린 리더: NVDA, JAWS 호환성
  - 색상 대비: 최소 4.5:1

- **브라우저 지원**:
  - Chrome 최신 2개 버전
  - Firefox 최신 2개 버전
  - Safari 최신 2개 버전
  - Edge 최신 2개 버전

### 보안 기준 (Security Criteria)

- **XSS 방지**: 모든 사용자 입력 이스케이핑 (React 기본 제공)
- **CORS 정책**: Next.js 도메인만 FastAPI 접근 허용
- **Rate Limiting**: 사용자당 1분에 60 요청 제한
- **Secrets 관리**: 환경 변수로 API 키 관리 (`.env` 파일)

### 사용성 기준 (Usability Criteria)

- **오류 메시지**: 사용자 친화적이고 구체적인 메시지 제공
- **로딩 상태**: 모든 비동기 작업에 로딩 스피너 표시
- **피드백**: 작업 성공 시 Toast 메시지 표시
- **입력 검증**: 실시간 피드백 (디바운스 500ms)

---

## Definition of Done (DoD)

각 Phase 완료 시 다음 조건을 만족해야 합니다:

### Phase 완료 조건

- [ ] 모든 코드 작성 완료
- [ ] 단위 테스트 작성 및 통과 (커버리지 목표 달성)
- [ ] 통합 테스트 작성 및 통과
- [ ] 코드 리뷰 완료 (Ruff, ESLint 통과)
- [ ] 문서 업데이트 (API 문서, README 등)
- [ ] E2E 테스트 통과 (해당 Phase가 UI 포함 시)

### 전체 SPEC 완료 조건

- [ ] 모든 Phase 완료
- [ ] 전체 E2E 테스트 통과
- [ ] 성능 목표 달성 (Lighthouse 점수 ≥90)
- [ ] 접근성 검사 통과 (axe-core)
- [ ] 보안 검사 통과 (OWASP 체크리스트)
- [ ] 프로덕션 배포 준비 완료

---

## 테스트 데이터 (Test Data)

### 유효한 ISBN (Valid ISBNs)

- `9791162233149` - Python 프로그래밍 (한빛미디어)
- `9788970509143` - 데이터베이스 설계 (한국방송통신대학교출판부)
- `9788960771802` - 클린 코드 (인사이트)

### 무효한 ISBN (Invalid ISBNs)

- `123456789012X` - 문자 포함
- `1234567890125` - 체크섬 불일치
- `12345` - 길이 부족

### 노원구 시방서 테스트 케이스

- **통과**: 040 필드가 규칙 준수
- **실패**: 040 필드 중 일부 서브필드 누락
- **실패**: 040$c에 괄호 누락

---

## 추적성 태그 (Traceability Tags)

- `#SPEC-WEB-001`
- `#Acceptance-Criteria`
- `#Gherkin`
- `#Test-Scenarios`
- `#Playwright-Testing`
- `#Performance-Criteria`
