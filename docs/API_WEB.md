# KORMARC Web API 레퍼런스

**버전**: 1.0.0
**기준일**: 2026-01-11
**SPEC**: SPEC-WEB-001

## 개요

KORMARC Web API는 100개의 프로토타입 KORMARC 레코드에 대한 읽기 전용 REST API를 제공합니다. 이 API는 레코드 조회, 검색 및 메타데이터 제공 기능을 지원합니다.

### 기본 정보

- **Base URL**: `http://localhost:8000`
- **프로토콜**: HTTP/1.1
- **인증**: 불필요 (읽기 전용 공개 API)
- **응답 형식**: JSON
- **문자 인코딩**: UTF-8

### 주요 특징

- 페이지네이션 지원 (모든 목록 엔드포인트)
- SQLite FTS5 기반 전문 검색
- FastAPI 자동 생성 문서 (Swagger UI, ReDoc)
- CORS 지원 (프론트엔드 통합)

---

## 인증

현재 버전은 인증이 필요하지 않습니다. 모든 엔드포인트는 공개 접근이 가능합니다.

---

## 공통 응답 형식

### 성공 응답

모든 성공 응답은 HTTP 200 상태 코드와 함께 JSON 형식으로 반환됩니다.

### 에러 응답

에러 발생 시 다음 형식으로 응답합니다:

```json
{
  "detail": "에러 메시지"
}
```

**HTTP 상태 코드**:
- `400 Bad Request`: 잘못된 요청 파라미터
- `404 Not Found`: 리소스를 찾을 수 없음
- `422 Unprocessable Entity`: 유효하지 않은 데이터 형식
- `500 Internal Server Error`: 서버 내부 오류

---

## 엔드포인트

### 1. 헬스 체크

시스템 상태를 확인합니다.

**엔드포인트**: `GET /health`

**요청 예시**:
```bash
curl http://localhost:8000/health
```

**응답 예시**:
```json
{
  "status": "healthy"
}
```

**응답 코드**:
- `200 OK`: 서비스 정상 작동

---

### 2. API 정보

API 메타데이터를 제공합니다.

**엔드포인트**: `GET /`

**요청 예시**:
```bash
curl http://localhost:8000/
```

**응답 예시**:
```json
{
  "name": "KORMARC Web API",
  "version": "1.0.0",
  "description": "Read-only API for KORMARC record browsing and search"
}
```

**응답 코드**:
- `200 OK`: 정상 응답

---

### 3. 레코드 목록 조회

페이지네이션된 KORMARC 레코드 목록을 조회합니다.

**엔드포인트**: `GET /api/v1/records`

**쿼리 파라미터**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `page` | integer | 아니오 | 1 | 페이지 번호 (1부터 시작) |
| `size` | integer | 아니오 | 20 | 페이지당 항목 수 (최대 100) |

**요청 예시**:
```bash
# 첫 번째 페이지 (기본값)
curl http://localhost:8000/api/v1/records

# 두 번째 페이지, 10개씩
curl "http://localhost:8000/api/v1/records?page=2&size=10"
```

**응답 예시**:
```json
{
  "items": [
    {
      "id": "KDC000001",
      "title": "Python 프로그래밍 입문",
      "author": "홍길동",
      "publisher": "테크출판사",
      "pub_year": "2023",
      "isbn": "979-11-1234567-8-9",
      "kdc": "005.133",
      "language": "kor"
    },
    {
      "id": "KDC000002",
      "title": "데이터 과학 기초",
      "author": "김영희",
      "publisher": "데이터북스",
      "pub_year": "2024",
      "isbn": "979-11-9876543-2-1",
      "kdc": "005.7",
      "language": "kor"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20
}
```

**응답 필드**:
- `items`: 레코드 배열
  - `id`: 레코드 ID (고유 식별자)
  - `title`: 도서 제목
  - `author`: 저자명
  - `publisher`: 출판사명
  - `pub_year`: 출판년도
  - `isbn`: ISBN (있는 경우)
  - `kdc`: 한국십진분류법 분류번호
  - `language`: 언어 코드 (kor, eng, jpn 등)
- `total`: 전체 레코드 수
- `page`: 현재 페이지 번호
- `size`: 페이지당 항목 수

**응답 코드**:
- `200 OK`: 정상 응답
- `400 Bad Request`: 잘못된 페이지 번호 (page < 1)
- `422 Unprocessable Entity`: 유효하지 않은 파라미터 타입

---

### 4. 레코드 상세 조회

특정 레코드의 상세 정보를 조회합니다.

**엔드포인트**: `GET /api/v1/records/{record_id}`

**경로 파라미터**:

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `record_id` | string | 예 | 레코드 고유 ID |

**요청 예시**:
```bash
curl http://localhost:8000/api/v1/records/KDC000001
```

**응답 예시**:
```json
{
  "id": "KDC000001",
  "title": "Python 프로그래밍 입문",
  "author": "홍길동",
  "publisher": "테크출판사",
  "pub_year": "2023",
  "pub_place": "서울",
  "isbn": "979-11-1234567-8-9",
  "kdc": "005.133",
  "language": "kor",
  "description": "Python 프로그래밍의 기초부터 고급까지 다루는 입문서",
  "pages": "350",
  "size": "23cm",
  "subject": ["Python", "프로그래밍", "컴퓨터언어"],
  "notes": ["색인 수록", "부록: 예제 코드"],
  "marc_fields": [
    {
      "tag": "245",
      "indicators": "10",
      "subfields": [
        {"code": "a", "value": "Python 프로그래밍 입문"},
        {"code": "b", "value": "기초에서 응용까지"}
      ]
    },
    {
      "tag": "260",
      "indicators": "  ",
      "subfields": [
        {"code": "a", "value": "서울"},
        {"code": "b", "value": "테크출판사"},
        {"code": "c", "value": "2023"}
      ]
    }
  ]
}
```

**응답 필드**:
- 기본 필드 (레코드 목록과 동일): `id`, `title`, `author`, `publisher`, `pub_year`, `isbn`, `kdc`, `language`
- 추가 필드:
  - `pub_place`: 출판지
  - `description`: 도서 설명
  - `pages`: 페이지 수
  - `size`: 도서 크기
  - `subject`: 주제어 배열
  - `notes`: 비고 사항 배열
  - `marc_fields`: 원본 MARC 필드 배열
    - `tag`: MARC 태그 (예: "245", "260")
    - `indicators`: 지시자 (2자리 문자열)
    - `subfields`: 하위 필드 배열
      - `code`: 하위 필드 코드 (a-z, 0-9)
      - `value`: 하위 필드 값

**응답 코드**:
- `200 OK`: 정상 응답
- `404 Not Found`: 레코드를 찾을 수 없음
- `422 Unprocessable Entity`: 유효하지 않은 레코드 ID 형식

---

### 5. 전문 검색

SQLite FTS5를 사용하여 레코드를 검색합니다.

**엔드포인트**: `GET /api/v1/search`

**쿼리 파라미터**:

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `q` | string | 아니오 | "" | 검색 키워드 |
| `page` | integer | 아니오 | 1 | 페이지 번호 (1부터 시작) |
| `size` | integer | 아니오 | 20 | 페이지당 항목 수 (최대 100) |

**검색 대상 필드**:
- 제목 (`title`)
- 저자 (`author`)
- 출판사 (`publisher`)
- 주제어 (`subject`)
- 설명 (`description`)

**요청 예시**:
```bash
# 키워드 검색
curl "http://localhost:8000/api/v1/search?q=Python"

# 복합 키워드 검색
curl "http://localhost:8000/api/v1/search?q=프로그래밍%20입문"

# 페이지네이션 포함
curl "http://localhost:8000/api/v1/search?q=서울&page=1&size=10"

# 검색어 없음 (전체 레코드 반환)
curl "http://localhost:8000/api/v1/search"
```

**응답 예시**:
```json
{
  "items": [
    {
      "id": "KDC000001",
      "title": "Python 프로그래밍 입문",
      "author": "홍길동",
      "publisher": "테크출판사",
      "pub_year": "2023",
      "isbn": "979-11-1234567-8-9",
      "kdc": "005.133",
      "language": "kor"
    }
  ],
  "total": 15,
  "page": 1,
  "size": 20
}
```

**검색 동작**:
- 검색어가 비어있으면 전체 레코드 목록 반환 (레코드 목록 조회와 동일)
- 키워드는 공백으로 구분되며 OR 연산 수행
- 부분 일치 및 형태소 분석 지원 (FTS5 기본 동작)
- 대소문자 구분 없음

**응답 필드**:
- 레코드 목록 조회와 동일한 형식
- `total`: 검색 결과 총 개수

**응답 코드**:
- `200 OK`: 정상 응답 (결과가 없어도 200 반환)
- `422 Unprocessable Entity`: 유효하지 않은 파라미터 타입

---

## 페이지네이션

모든 목록 엔드포인트는 일관된 페이지네이션을 제공합니다.

### 파라미터

- `page`: 페이지 번호 (1부터 시작)
- `size`: 페이지당 항목 수 (기본값: 20, 최대: 100)

### 응답 형식

```json
{
  "items": [...],
  "total": 전체_항목_수,
  "page": 현재_페이지,
  "size": 페이지당_항목수
}
```

### 페이지 계산

- 총 페이지 수: `Math.ceil(total / size)`
- 다음 페이지: `page + 1` (page * size < total인 경우)
- 이전 페이지: `page - 1` (page > 1인 경우)

---

## CORS 설정

API는 다음 오리진에서의 요청을 허용합니다:

- `http://localhost:5173` (Vite 개발 서버)
- `http://localhost:3000` (일반 개발 서버)

**허용 메서드**: GET, POST, PUT, DELETE, OPTIONS
**허용 헤더**: 모든 헤더
**자격 증명**: 허용

프로덕션 환경에서는 실제 프론트엔드 도메인으로 설정해야 합니다.

---

## 속도 제한

현재 버전은 속도 제한이 없습니다. 향후 프로덕션 배포 시 다음과 같은 제한이 추가될 예정입니다:

- 초당 요청 수: 10 req/s
- 분당 요청 수: 100 req/min
- 일일 요청 수: 10,000 req/day

---

## OpenAPI 문서

FastAPI는 자동으로 OpenAPI 3.0 명세를 생성합니다.

### 대화형 문서

**Swagger UI**: http://localhost:8000/docs
- API 엔드포인트 테스트 가능
- 실시간 요청/응답 확인

**ReDoc**: http://localhost:8000/redoc
- 깔끔한 문서 레이아웃
- 검색 및 탐색 기능

### OpenAPI JSON

**엔드포인트**: `GET /openapi.json`

OpenAPI 3.0 스키마를 JSON 형식으로 제공합니다.

```bash
curl http://localhost:8000/openapi.json
```

---

## 예제 코드

### Python (requests)

```python
import requests

# 기본 URL
BASE_URL = "http://localhost:8000"

# 레코드 목록 조회
response = requests.get(f"{BASE_URL}/api/v1/records", params={"page": 1, "size": 20})
records = response.json()
print(f"총 {records['total']}개 레코드 중 {len(records['items'])}개 조회")

# 레코드 상세 조회
record_id = records['items'][0]['id']
response = requests.get(f"{BASE_URL}/api/v1/records/{record_id}")
record_detail = response.json()
print(f"제목: {record_detail['title']}")

# 검색
response = requests.get(f"{BASE_URL}/api/v1/search", params={"q": "Python", "page": 1, "size": 10})
search_results = response.json()
print(f"검색 결과: {search_results['total']}개")
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// 레코드 목록 조회
async function getRecords(page = 1, size = 20) {
  const response = await fetch(`${BASE_URL}/api/v1/records?page=${page}&size=${size}`);
  const data = await response.json();
  console.log(`총 ${data.total}개 레코드 중 ${data.items.length}개 조회`);
  return data;
}

// 레코드 상세 조회
async function getRecordDetail(recordId) {
  const response = await fetch(`${BASE_URL}/api/v1/records/${recordId}`);
  const data = await response.json();
  console.log(`제목: ${data.title}`);
  return data;
}

// 검색
async function searchRecords(query, page = 1, size = 20) {
  const response = await fetch(`${BASE_URL}/api/v1/search?q=${encodeURIComponent(query)}&page=${page}&size=${size}`);
  const data = await response.json();
  console.log(`검색 결과: ${data.total}개`);
  return data;
}

// 사용 예시
getRecords(1, 10).then(data => {
  const firstRecordId = data.items[0].id;
  return getRecordDetail(firstRecordId);
});

searchRecords("Python", 1, 20);
```

### cURL

```bash
# 레코드 목록 조회
curl "http://localhost:8000/api/v1/records?page=1&size=20"

# 레코드 상세 조회
curl "http://localhost:8000/api/v1/records/KDC000001"

# 검색
curl "http://localhost:8000/api/v1/search?q=Python&page=1&size=20"

# 헬스 체크
curl "http://localhost:8000/health"
```

---

## 문제 해결

### 일반적인 에러

**404 Not Found - 레코드를 찾을 수 없음**:
```json
{
  "detail": "Record not found: INVALID_ID"
}
```
- 해결: 올바른 레코드 ID를 사용하세요. 레코드 목록 조회로 유효한 ID를 확인할 수 있습니다.

**400 Bad Request - 잘못된 페이지 번호**:
```json
{
  "detail": "Page number must be >= 1"
}
```
- 해결: 페이지 번호는 1 이상이어야 합니다.

**422 Unprocessable Entity - 유효하지 않은 파라미터**:
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["query", "page"],
      "msg": "Input should be a valid integer"
    }
  ]
}
```
- 해결: 파라미터 타입을 확인하세요. `page`와 `size`는 정수형이어야 합니다.

### CORS 에러

프론트엔드에서 API 호출 시 CORS 에러가 발생하면:

1. 프론트엔드 오리진이 허용 목록에 있는지 확인
2. 개발 환경: `http://localhost:5173` 또는 `http://localhost:3000` 사용
3. 프로덕션 환경: `main.py`의 CORS 설정을 프론트엔드 도메인으로 업데이트

---

## 향후 계획

다음 기능이 향후 버전에 추가될 예정입니다:

### v1.1.0
- 레코드 내보내기 (`GET /api/v1/export/json`, `GET /api/v1/export/marcxml`)
- 검색어 자동완성 (`GET /api/v1/search/suggest`)

### v1.2.0
- 통계 API (`GET /api/v1/stats`)
- 필드별 검색 (제목, 저자, 출판사 등 개별 검색)

### v2.0.0
- 사용자 인증 (선택적)
- 북마크 기능
- 검색 히스토리

---

## 관련 문서

- **[아키텍처 문서](ARCHITECTURE_WEB.md)** - 백엔드 시스템 설계
- **[SPEC 문서](../.moai/specs/SPEC-WEB-001/spec.md)** - 요구사항 명세
- **[README](../README.md)** - 프로젝트 개요 및 빠른 시작

---

**문서 버전**: 1.0.0
**최종 업데이트**: 2026-01-11
**작성자**: 지니 (SPEC-WEB-001 구현팀)
