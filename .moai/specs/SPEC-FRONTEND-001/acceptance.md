---
id: SPEC-FRONTEND-001
version: "1.0.0"
status: "acceptance-criteria"
created: "2026-01-11"
updated: "2026-01-11"
author: "지니"
priority: "HIGH"
---

# SPEC-FRONTEND-001 인수 기준 (Acceptance.md)

## 테스트 시나리오 (Gherkin Format)

모든 시나리오는 Given-When-Then 형식으로 작성되어 자동화된 E2E 테스트 및 수동 검증에 사용됩니다.

---

## Scenario 1: 성공적인 KORMARC 생성

**Tag**: @happy-path @critical
**Priority**: P0

```gherkin
Feature: KORMARC 데이터 생성

Scenario: 유효한 도서 정보로 KORMARC 생성
  Given 사용자가 Next.js 웹앱에 접속했다
  And BookInfo 입력 폼이 렌더링되었다
  And 모든 입력 필드가 비어있다
  When 사용자가 다음 정보를 입력한다:
    | 필드명     | 값                  |
    | ISBN       | 9791162233149      |
    | 제목       | Python 프로그래밍  |
    | 저자       | 박응용             |
    | 출판사     | 한빛미디어         |
    | 발행년     | 2025               |
  And 사용자가 "KORMARC 생성" 버튼을 클릭한다
  Then 시스템은 로딩 스피너를 표시한다
  And "KORMARC 생성" 버튼은 비활성화된다
  And 3초 이내에 POST /api/kormarc/build API를 호출한다
  And API 응답이 성공하면 KORMARCRecord 객체를 수신한다
  And JSON/XML 미리보기 영역이 나타난다
  And JSON 탭에서 구조화된 KORMARC 데이터가 표시된다
  And XML 탭에서 MARCXML 표준 형식이 표시된다
  And 040 필드가 노란색(#FCD34D) 배경으로 하이라이트된다
  And "JSON 다운로드", "XML 다운로드" 버튼이 활성화된다
```

**구현 체크리스트**:
- [ ] POST /api/kormarc/build API 호출 성공
- [ ] 응답 데이터 타입이 KORMARCRecord 인터페이스 준수
- [ ] JSON/XML 탭 전환 동작 확인
- [ ] 040 필드 하이라이트 시각적 확인
- [ ] 버튼 활성화/비활성화 상태 확인

**성능 기준**:
- API 응답 시간: ≤ 3초 (P95)
- 데이터 렌더링: ≤ 500ms (JSON/XML 표시)

---

## Scenario 2: ISBN 실시간 검증 피드백

**Tag**: @validation @critical
**Priority**: P0

```gherkin
Feature: ISBN 입력 검증

Scenario: 잘못된 ISBN 형식 감지
  Given ISBN 입력 필드에 포커스한다
  When 사용자가 "123456789" (9자리)를 입력한다
  Then 500ms 디바운스 후 입력 필드의 테두리가 빨간색(#EF4444)으로 변한다
  And 필드 아래에 오류 메시지가 표시된다:
    "형식 오류: ISBN은 13자리여야 합니다"
  And "KORMARC 생성" 버튼은 비활성화 상태이다
  When 사용자가 "9791162233149" (13자리, 올바른)를 입력한다
  Then 500ms 디바운스 후 입력 필드의 테두리가 초록색(#10B981)으로 변한다
  And 오류 메시지가 사라진다
  And 필드 아래에 "유효한 ISBN입니다" 확인 메시지가 표시된다
  And "KORMARC 생성" 버튼은 활성화 상태이다

Scenario: ISBN 체크섬 검증
  Given ISBN 입력 필드에 포커스한다
  When 사용자가 "9791162233140" (체크섬 오류)를 입력한다
  Then 500ms 디바운스 후 테두리가 빨간색으로 변한다
  And 오류 메시지가 표시된다:
    "체크섬 오류: ISBN 유효성 검사 실패"
  And "KORMARC 생성" 버튼은 비활성화 상태이다
```

**구현 체크리스트**:
- [ ] Luhn 알고리즘 검증 구현
- [ ] 정규식 검증 (13자리 숫자)
- [ ] 500ms 디바운스 정확성 확인
- [ ] 테두리 색상 변경 시각적 확인
- [ ] 오류 메시지 정확성

**성능 기준**:
- ISBN 검증: ≤ 100ms
- UI 업데이트: ≤ 50ms

---

## Scenario 3: 필수 필드 미입력 시 버튼 비활성화

**Tag**: @validation @critical
**Priority**: P0

```gherkin
Feature: 필수 필드 검증

Scenario: 필수 필드 미입력 상태
  Given BookInfo 폼이 열려있다
  And 모든 입력 필드가 비어있다
  Then "KORMARC 생성" 버튼은 회색으로 비활성화되어 있다
  And 호버 시 툴팁이 표시된다:
    "필수 필드를 모두 입력해주세요"

Scenario: 부분 입력 시 버튼 비활성화
  Given BookInfo 폼이 열려있다
  When 사용자가 ISBN만 "9791162233149" 입력한다
  And 다른 필드(제목, 저자, 출판사, 발행년)는 비워둔다
  Then "KORMARC 생성" 버튼은 비활성화 상태이다

Scenario: 모든 필수 필드 입력 시 버튼 활성화
  Given BookInfo 폼이 열려있다
  When 사용자가 다음 필드를 입력한다:
    | 필드명     | 값                  |
    | ISBN       | 9791162233149      |
    | 제목       | Python 프로그래밍  |
    | 저자       | 박응용             |
    | 출판사     | 한빛미디어         |
    | 발행년     | 2025               |
  Then "KORMARC 생성" 버튼은 파란색으로 활성화된다
```

**구현 체크리스트**:
- [ ] 필수 필드 정의: ISBN, 제목, 저자, 출판사, 발행년
- [ ] 선택 필드 정의: 판차, 총서명
- [ ] 버튼 disabled 속성 동작
- [ ] 호버 시 aria-label 표시 (접근성)

---

## Scenario 4: 노원구 040 필드 검증 및 하이라이트

**Tag**: @kormarc @nowon @critical
**Priority**: P0

```gherkin
Feature: 노원구 040 필드 강조

Scenario: KORMARC 생성 후 040 필드 하이라이트
  Given KORMARC 레코드가 성공적으로 생성되었다
  And JSON/XML 미리보기가 표시되어 있다
  When JSON 탭을 클릭한다
  Then 040 필드가 노란색(#FCD34D) 배경으로 하이라이트된다
  And 040 필드 옆에 별표(⭐) 아이콘이 표시된다
  And 호버 시 툴팁이 나타난다:
    "노원구 시방서 필수 필드"

  When XML 탭을 클릭한다
  Then XML 형식의 040 필드도 동일하게 하이라이트된다
  And 노란색 배경이 유지된다

Scenario: ValidationStatus에서 Tier 3 검증 결과 표시
  Given KORMARC 레코드가 생성되었다
  And ValidationStatus 컴포넌트가 렌더링되었다
  Then ValidationStatus에는 다음과 같이 표시된다:
    | Tier | Status | Icon | Message |
    | 1    | 통과   | ✅   | 기술 검증 통과 |
    | 2    | 통과   | ✅   | 문법 검증 통과 |
    | 3    | 통과   | ✅   | 의미 검증 통과 (040 필드 존재) |
    | 4    | 경고   | ⚠️   | 정합성 부분 확인 필요 |
    | 5    | 통과   | ✅   | 기관 규정 준수 |
```

**구현 체크리스트**:
- [ ] 040 필드 감지 로직
- [ ] CSS 하이라이트 (bg-yellow-100, dark:bg-yellow-900)
- [ ] 툴팁 aria-label 추가
- [ ] ValidationStatus 컴포넌트 렌더링
- [ ] 각 Tier별 아이콘 및 색상 정의

---

## Scenario 5: KORMARC 내보내기 (JSON, XML, 클립보드)

**Tag**: @export @critical
**Priority**: P0

```gherkin
Feature: KORMARC 파일 다운로드

Scenario: JSON 파일 다운로드
  Given KORMARC 미리보기가 표시되어 있다
  And ExportButtons 컴포넌트가 렌더링되었다
  When 사용자가 "JSON 다운로드" 버튼을 클릭한다
  Then 브라우저 다운로드가 자동으로 시작된다
  And 파일명이 다음 형식을 따른다:
    kormarc_9791162233149_20260111143000.json
  And 파일 크기가 1KB 이상 1MB 이하이다
  And 파일 내용이 유효한 JSON 형식이다
  And 파일에 BookInfo 데이터가 포함된다

Scenario: XML 파일 다운로드
  Given KORMARC 미리보기가 표시되어 있다
  When 사용자가 "XML 다운로드" 버튼을 클릭한다
  Then 브라우저 다운로드가 자동으로 시작된다
  And 파일명이 다음 형식을 따른다:
    kormarc_9791162233149_20260111143000.xml
  And 파일 내용이 유효한 XML 형식이다
  And XML 선언과 MARCXML 요소를 포함한다

Scenario: 클립보드 복사 (선택사항)
  Given KORMARC 미리보기가 표시되어 있다
  When 사용자가 "클립보드 복사" 버튼을 클릭한다
  Then 토스트 메시지가 표시된다:
    "복사 완료!"
  And JSON 데이터가 시스템 클립보드에 저장된다
  And 붙여넣기(Ctrl+V)로 데이터를 확인할 수 있다
```

**구현 체크리스트**:
- [ ] Blob API로 파일 생성
- [ ] `<a href>` 요소로 다운로드 트리거
- [ ] 파일명 생성 로직 (ISBN + 타임스탐프)
- [ ] JSON 유효성 검사
- [ ] XML 유효성 검사
- [ ] navigator.clipboard.writeText() 구현 (선택)
- [ ] 토스트 메시지 표시

**성능 기준**:
- 다운로드 준비: ≤ 500ms
- 클립보드 복사: ≤ 100ms

---

## Scenario 6: API 오류 처리 및 재시도

**Tag**: @error-handling @critical
**Priority**: P1

```gherkin
Feature: API 오류 처리

Scenario: 네트워크 오류 (Connection Timeout)
  Given 사용자가 유효한 BookInfo를 입력했다
  And 백엔드 서버가 응답하지 않는다 (30초 이상)
  When "KORMARC 생성" 버튼을 클릭한다
  Then 30초 후 오류 메시지가 표시된다:
    "서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
  And "재시도" 버튼이 표시된다
  When 사용자가 "재시도" 버튼을 클릭한다
  Then API 요청이 다시 시도된다

Scenario: 서버 오류 (500 Internal Server Error)
  Given 사용자가 유효한 BookInfo를 입력했다
  And 백엔드 서버가 500 오류를 반환한다
  When "KORMARC 생성" 버튼을 클릭한다
  Then 친화적 오류 메시지가 표시된다:
    "서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
  And 스택 트레이스나 기술 세부정보는 노출되지 않는다
  And 로그: 브라우저 개발자 도구 콘솔에만 상세 오류 기록

Scenario: 데이터 검증 오류 (400 Bad Request)
  Given 사용자가 다음 잘못된 데이터를 입력했다:
    | 필드명     | 값              |
    | ISBN       | 123456789012    |
    | 제목       | <script>alert(1)</script> |
  And 클라이언트 검증을 무시하고 요청했다 (개발자 도구)
  Then 백엔드가 400 Bad Request를 반환한다
  And 사용자 친화적 메시지가 표시된다:
    "입력 데이터가 올바르지 않습니다."
```

**구현 체크리스트**:
- [ ] 타임아웃 설정 (30초)
- [ ] 재시도 로직 (최대 3회, exponential backoff)
- [ ] 오류 메시지 한국어 및 친화적
- [ ] 스택 트레이스 숨김
- [ ] 콘솔 로그 기록 (개발 모드)

---

## Scenario 7: 모바일 반응형 테스트

**Tag**: @responsive @critical
**Priority**: P1

```gherkin
Feature: 모바일 반응형 디자인

Scenario: 모바일 기기에서 레이아웃 (320px - 480px)
  Given 모바일 기기(iPhone 12, 390px width)를 사용한다
  When 웹앱에 접속한다
  Then 레이아웃이 모바일 최적화된다:
    | 요소        | 상태          |
    | 헤더        | 전체 폭 사용  |
    | 폼          | 단일 열       |
    | 입력 필드   | 전체 폭       |
    | 버튼        | 전체 폭       |
    | 미리보기    | 스크롤 가능   |
  And 가로 스크롤이 발생하지 않는다
  And 글자 크기는 16px 이상이다 (확대 방지)

Scenario: 태블릿에서 레이아웃 (768px - 1024px)
  Given 태블릿 기기(iPad Air, 820px width)를 사용한다
  When 웹앱에 접속한다
  Then 레이아웃이 2열로 표시된다:
    | 좌측       | 우측        |
    | BookInfo폼 | 미리보기    |
  And 각 열의 폭이 균형있게 배분된다

Scenario: 데스크톱에서 레이아웃 (1200px 이상)
  Given 데스크톱 컴퓨터(1920px width)를 사용한다
  When 웹앱에 접속한다
  Then 레이아웃이 최적 폭(1200px)으로 제한된다
  And 콘텐츠가 가운데 정렬된다
```

**구현 체크리스트**:
- [ ] Tailwind 반응형 클래스 사용 (sm:, md:, lg:, xl:)
- [ ] 모바일 우선 설계 (mobile-first)
- [ ] 터치 타겟 크기 최소 44x44px
- [ ] 뷰포트 메타 태그 설정
- [ ] 실제 기기 테스트 (또는 DevTools 에뮬레이션)

---

## Scenario 8: 다크 모드 토글 및 저장

**Tag**: @theme @optional
**Priority**: P2

```gherkin
Feature: 다크 모드 지원

Scenario: 다크 모드 토글
  Given 라이트 모드로 웹앱을 실행했다
  And 헤더에 다크 모드 토글 버튼(달/태양 아이콘)이 표시된다
  When 사용자가 다크 모드 토글 버튼을 클릭한다
  Then 다음과 같이 변경된다:
    | 요소      | 라이트 모드      | 다크 모드        |
    | 배경색    | 흰색(#FFFFFF)   | 검은색(#1F2937)  |
    | 텍스트색  | 검은색(#1F2937) | 흰색(#FFFFFF)    |
    | 버튼      | 파란색(#3B82F6) | 파란색 어두운 버전 |
  And 토글이 즉시 적용된다 (페이지 새로고침 없음)

Scenario: 다크 모드 저장
  Given 다크 모드로 변경했다
  When 페이지를 새로고침한다
  Then 다크 모드가 유지된다
  And localStorage에 "theme": "dark" 저장된다

Scenario: 시스템 설정 자동 감지
  Given 처음 접속하는 사용자이다
  And 시스템 설정이 다크 모드이다 (macOS Dark Mode, Windows Dark Mode)
  When 웹앱에 접속한다
  Then 자동으로 다크 모드가 활성화된다
  And prefers-color-scheme 미디어 쿼리가 적용된다
```

**구현 체크리스트**:
- [ ] 다크 모드 토글 버튼 UI
- [ ] localStorage 저장 로직
- [ ] prefers-color-scheme 미디어 쿼리
- [ ] Tailwind dark: 클래스 정의
- [ ] 모든 색상 대비 확인 (light, dark)

---

## Scenario 9: 접근성 검사 (WCAG 2.1 AA)

**Tag**: @accessibility @critical
**Priority**: P1

```gherkin
Feature: 접근성 준수

Scenario: 키보드 네비게이션
  Given 마우스를 사용하지 않는다
  When Tab 키로 폼 필드를 순회한다
  Then 순서가 논리적이다:
    ISBN → 제목 → 저자 → 출판사 → 발행년 → 판차 → 총서명 → 생성 버튼
  When Enter 키를 누른다
  Then 포커스된 버튼이 클릭된다
  When Escape 키를 누른다 (모달이 있을 경우)
  Then 모달이 닫힌다

Scenario: 스크린 리더 지원
  Given NVDA 또는 JAWS 스크린 리더를 사용한다
  When 웹앱을 네비게이션한다
  Then 다음이 읽혀진다:
    | 요소              | 읽음 내용 |
    | ISBN 필드         | "ISBN 입력, 필수" |
    | 생성 버튼(비활성) | "KORMARC 생성 버튼, 비활성화됨, 필수 필드를 모두 입력해주세요" |
    | 하이라이트 필드   | "040 필드, 노원구 시방서 필수 필드" |

Scenario: 색상 대비
  Given 모든 텍스트 요소를 확인한다
  Then 색상 대비가 다음을 충족한다:
    | 크기        | 기준 |
    | 일반 텍스트 | 4.5:1 이상 (AA) |
    | 큰 텍스트   | 3:1 이상 (AA) |
    | UI 컴포넌트 | 3:1 이상 (AA) |
  And 색상만으로 정보 전달하지 않는다 (아이콘, 텍스트 함께 사용)
```

**구현 체크리스트**:
- [ ] aria-label, aria-describedby 추가
- [ ] tabindex 관리
- [ ] 포커스 스타일 명확
- [ ] 시맨틱 HTML (button, label, input)
- [ ] axe DevTools 검사 (자동화)
- [ ] 수동 검사 (NVDA, JAWS)

---

## Scenario 10: E2E 전체 플로우 (입력 → 생성 → 다운로드)

**Tag**: @e2e @critical
**Priority**: P0

```gherkin
Feature: 전체 사용자 플로우

Scenario: 완전한 KORMARC 생성 및 다운로드
  Given 사용자가 웹앱에 처음 접속한다
  When 페이지가 완전히 로드된다 (FCP < 1.5s)
  Then BookInfo 폼이 렌더링된다

  When 사용자가 다음을 입력한다:
    | ISBN       | 9791162233149      |
    | 제목       | Python 프로그래밍  |
    | 저자       | 박응용             |
    | 출판사     | 한빛미디어         |
    | 발행년     | 2025               |
  And 판차, 총서명은 비워둔다 (선택사항)
  And 각 필드에서 실시간 검증이 동작한다 (500ms)

  When "KORMARC 생성" 버튼을 클릭한다
  And 로딩 스피너가 표시된다
  And 3초 이내에 API 응답이 반환된다

  Then KORMARC 미리보기가 표시된다
  And JSON/XML 탭 전환이 동작한다
  And 040 필드가 하이라이트된다
  And ValidationStatus에서 Tier 1-5 결과를 확인한다

  When "JSON 다운로드" 버튼을 클릭한다
  Then 파일이 다운로드된다
  And 파일명: kormarc_9791162233149_{timestamp}.json
  And 파일 내용이 유효한 JSON이다

  When "다시 생성" 버튼을 클릭한다 (선택사항)
  Then 폼이 초기화되고 새로운 입력을 받을 수 있다
```

**구현 체크리스트**:
- [ ] Playwright E2E 테스트 작성
- [ ] 전체 플로우 자동화 스크립트
- [ ] 성능 측정 (FCP, LCP, CLS)
- [ ] 브라우저별 테스트 (Chrome, Firefox, Safari)

---

## 성능 기준 (Performance Metrics)

### Web Vitals

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| FCP (First Contentful Paint) | < 1.5초 | Lighthouse, web-vitals library |
| LCP (Largest Contentful Paint) | < 2.5초 | Lighthouse, web-vitals library |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse, web-vitals library |
| TTFB (Time to First Byte) | < 500ms | Lighthouse, network tab |

### 기타 성능 지표

| 작업 | 목표 | 측정 방법 |
|------|------|----------|
| ISBN 검증 | < 100ms | Chrome DevTools, 프로파일러 |
| API 응답 시간 | < 3초 (P95) | Network tab, Application Insights |
| 번들 크기 | < 200KB (gzipped) | next/bundle-analyzer |
| 캐시 히트율 | > 80% | TanStack Query DevTools |

---

## 품질 기준 (Quality Gates)

### 테스트 커버리지

| 항목 | 목표 | 측정 방법 |
|------|------|----------|
| 전체 커버리지 | ≥ 80% | vitest coverage |
| 라인 커버리지 | ≥ 80% | vitest --coverage |
| 브랜치 커버리지 | ≥ 75% | vitest --coverage |
| 함수 커버리지 | ≥ 80% | vitest --coverage |

### 코드 품질

| 항목 | 기준 | 확인 방법 |
|------|------|----------|
| ESLint 경고 | 0개 | npm run lint |
| TypeScript 오류 | 0개 | npx tsc --noEmit |
| 보안 취약점 | 0개 (Critical) | npm audit, snyk |
| 접근성 위반 | 0개 (Critical) | axe DevTools, WAVE |

### E2E 테스트

| 항목 | 기준 |
|------|------|
| 시나리오 1-10 통과 | 100% (모든 브라우저) |
| 브라우저 호환성 | Chrome, Firefox, Safari, Edge 최신 2개 버전 |

---

## 배포 전 체크리스트

### 기능 검증
- [ ] 모든 EARS 요구사항 구현
- [ ] 10개 시나리오 E2E 테스트 통과
- [ ] API 통합 테스트 성공 (실제 또는 Mock 백엔드)
- [ ] 오류 처리 시나리오 검증

### 성능 및 호환성
- [ ] Lighthouse 점수 ≥ 90 (Performance, Accessibility, Best Practices)
- [ ] Web Vitals 기준 충족 (FCP, LCP, CLS)
- [ ] 크로스 브라우저 테스트 통과 (4개 브라우저)
- [ ] 반응형 디자인 확인 (3가지 해상도)

### 보안 및 접근성
- [ ] OWASP TOP 10 검사 통과
- [ ] WCAG 2.1 AA 준수
- [ ] 의존성 보안 감사 (npm audit)
- [ ] 민감 정보 노출 확인 없음

### 배포 준비
- [ ] 환경 변수 설정 (NEXT_PUBLIC_API_BASE_URL)
- [ ] .env.production 파일 확인
- [ ] 프로덕션 빌드 테스트 (npm run build && npm start)
- [ ] GitHub Actions 또는 Vercel CI/CD 설정

---

## 주요 성공 지표 (KPI)

| KPI | 목표 | 측정 방법 |
|-----|------|----------|
| 사용자 만족도 | ≥ 4.5/5.0 | 설문조사 (선택) |
| 오류율 | < 0.1% | 에러 추적 (Sentry, LogRocket) |
| 성능 점수 | ≥ 90/100 | Lighthouse |
| 접근성 점수 | ≥ 90/100 | axe DevTools |
| 테스트 커버리지 | ≥ 80% | vitest |

---

**작성일**: 2026-01-11
**상태**: Acceptance Criteria Draft
**테스트 자동화**: Vitest (단위), Playwright (E2E)
**수동 테스트**: 각 시나리오별 QA 팀 검증 필요

---

## 문의 및 승인

**SPEC 작성자**: 지니
**검토자**: (Backend Lead, Frontend Lead, QA Lead)
**승인자**: 프로젝트 매니저

---

## 부록: 테스트 환경 설정

### 개발 환경
```bash
npm install
npm run dev
# http://localhost:3000
```

### 테스트 실행
```bash
# 단위 테스트
npm run test

# E2E 테스트
npm run test:e2e

# 커버리지 리포트
npm run test:coverage
```

### Mock 백엔드 (선택)
```bash
# Mswjs를 사용한 API Mock
npm install msw
# Mock 서버 시작 (개발 중)
```

---

**End of Acceptance Criteria Document**
