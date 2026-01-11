# SPEC-FRONTEND-001: 구현 계획

**SPEC ID**: SPEC-FRONTEND-001
**제목**: KORMARC 웹 인터페이스 프론트엔드 UI 구현
**작성자**: 지니
**버전**: 1.0.0
**상태**: 계획 수립 완료

---

## 1. 기술 스택 (Technology Stack)

### 핵심 의존성

```json
{
  "next": "15.1+",
  "react": "19.0+",
  "typescript": "5.7+",
  "tailwindcss": "4.0+",
  "react-hook-form": "7.54+",
  "zod": "3.24+",
  "shadcn-ui": "0.0.1",
  "axios": "1.6+"
}
```

### 개발 의존성

```json
{
  "typescript": "^5.7",
  "vitest": "^1.0",
  "@testing-library/react": "^14.0",
  "@testing-library/jest-dom": "^6.1",
  "@playwright/test": "^1.40",
  "eslint": "^8.0",
  "prettier": "^3.1"
}
```

---

## 2. 프로젝트 구조 (Project Structure)

```
app/
├── layout.tsx                          # Root layout (Providers 포함)
├── page.tsx                            # 홈 페이지 (/kormarc)
├── components/
│   ├── BookInfoForm.tsx                # 도서 정보 입력 폼 (부모)
│   ├── fields/
│   │   ├── ISBNInput.tsx               # ISBN 입력 필드
│   │   ├── TitleInput.tsx              # 제목 입력 필드
│   │   ├── AuthorInput.tsx             # 저자 입력 필드
│   │   ├── PublisherInput.tsx          # 출판사 입력 필드
│   │   └── PublicationYearInput.tsx    # 발행년도 입력 필드
│   ├── ValidationStatus.tsx            # 검증 상태 시각화
│   ├── KORMARCPreview.tsx              # JSON/XML 결과 표시
│   ├── ExportButtons.tsx               # 다운로드/복사 버튼
│   ├── LoadingSpinner.tsx              # 로딩 스피너
│   ├── ErrorAlert.tsx                  # 오류 알림
│   └── ErrorBoundary.tsx               # 오류 경계
├── api/
│   ├── kormarc/route.ts                # POST /api/kormarc (프록시)
│   └── book/route.ts                   # GET /api/book/search (프록시)
├── lib/
│   ├── types.ts                        # TypeScript 인터페이스 정의
│   ├── schemas.ts                      # Zod 유효성 검사 스키마
│   ├── api-client.ts                   # API 클라이언트 함수
│   ├── constants.ts                    # 상수 및 설정값
│   ├── validators.ts                   # 커스텀 검증 함수
│   └── storage.ts                      # localStorage 유틸리티
├── hooks/
│   ├── useFormState.ts                 # 폼 상태 관리
│   ├── useLocalStorage.ts              # localStorage 훅
│   └── useAPICall.ts                   # API 호출 훅
├── __tests__/
│   ├── unit/
│   │   ├── components/
│   │   │   ├── BookInfoForm.test.tsx
│   │   │   ├── ISBNInput.test.tsx
│   │   │   └── ValidationStatus.test.tsx
│   │   └── lib/
│   │       ├── schemas.test.ts
│   │       └── validators.test.ts
│   ├── integration/
│   │   └── api-flow.test.ts
│   └── e2e/
│       ├── book-creation.spec.ts
│       └── export-functionality.spec.ts
└── styles/
    └── globals.css                     # 전역 스타일
```

---

## 3. 구현 단계 (Implementation Phases)

### Phase 1: 프로젝트 초기 설정 (Priority: HIGH)

**목표**: Next.js 15 프로젝트 셋업 및 개발 환경 구성

**작업 항목**:
- [ ] Next.js 15 프로젝트 초기화
- [ ] TypeScript 설정
- [ ] Tailwind CSS 설정
- [ ] Shadcn UI 컴포넌트 라이브러리 설정
- [ ] ESLint/Prettier 구성
- [ ] 기본 레이아웃 및 페이지 구조 생성
- [ ] API 라우트 기본 구조

**기대 결과**: 개발 환경 완전히 구성됨, 로컬 개발 서버 실행 가능

**예상 파일 수**: 8-10개

---

### Phase 2: 폼 컴포넌트 및 검증 시스템 (Priority: HIGH)

**목표**: BookInfoForm, 각 입력 필드, Zod 검증 스키마 구현

**작업 항목**:
- [ ] Zod 유효성 검사 스키마 작성 (schemas.ts)
- [ ] BookInfoForm 컴포넌트 구현
- [ ] ISBNInput 컴포넌트 구현 (실시간 체크섬 검증)
- [ ] TitleInput, AuthorInput, PublisherInput, PublicationYearInput 구현
- [ ] 필드별 에러 메시지 표시
- [ ] React Hook Form 통합

**기대 결과**: 완전히 검증되는 입력 폼, 실시간 피드백

**예상 파일 수**: 10-12개

---

### Phase 3: KORMARC 생성 API 통합 (Priority: HIGH)

**목표**: 백엔드 /api/kormarc/build 엔드포인트 연동

**작업 항목**:
- [ ] api-client.ts 작성 (axios 기반)
- [ ] /api/kormarc 프록시 라우트 구현
- [ ] /api/book/search 프록시 라우트 구현 (선택)
- [ ] 오류 처리 로직 (네트워크 오류, 타임아웃)
- [ ] 재시도 로직 구현
- [ ] API 응답 타입 정의

**기대 결과**: 백엔드와의 안정적인 통신

**예상 파일 수**: 4-5개

---

### Phase 4: 결과 표시 및 내보내기 (Priority: HIGH)

**목표**: KORMARCPreview, ExportButtons 컴포넌트 구현

**작업 항목**:
- [ ] KORMARCPreview 컴포넌트 (JSON/XML 탭)
- [ ] 코드 하이라이팅 (Prism 또는 Highlight.js)
- [ ] ExportButtons 컴포넌트
  - JSON 다운로드
  - XML 다운로드
  - 클립보드 복사
- [ ] 다운로드 파일명 포맷팅 (KORMARC_YYYY-MM-DD_HHmmss.json)

**기대 결과**: 사용자가 결과를 다양한 형식으로 내보낼 수 있음

**예상 파일 수**: 3-4개

---

### Phase 5: 상태 표시 및 로딩 UI (Priority: HIGH)

**목표**: 로딩 스피너, 에러 알림, 검증 상태 시각화

**작업 항목**:
- [ ] LoadingSpinner 컴포넌트
- [ ] ErrorAlert 컴포넌트 (명확한 메시지)
- [ ] ValidationStatus 컴포넌트 (5단계 색상 표시)
- [ ] 로딩/에러 상태 전역 관리 (Zustand 고려)

**기대 결과**: 사용자에게 명확한 시각적 피드백 제공

**예상 파일 수**: 4-5개

---

### Phase 6: 폼 자동 저장 기능 (Priority: MEDIUM)

**목표**: localStorage 활용한 자동 저장 및 복원

**작업 항목**:
- [ ] useLocalStorage 커스텀 훅 구현
- [ ] 폼 상태 저장 로직
- [ ] 페이지 로드 시 복원 로직
- [ ] 초기화 버튼 구현 (저장된 데이터 삭제)
- [ ] 자동 저장 간격 설정 (1초)

**기대 결과**: 실수로 인한 데이터 손실 방지

**예상 파일 수**: 3-4개

---

### Phase 7: 단위 및 통합 테스트 (Priority: MEDIUM)

**목표**: Vitest, React Testing Library로 테스트 작성 (≥85% 커버리지)

**작업 항목**:
- [ ] 컴포넌트 유닛 테스트 작성
  - BookInfoForm
  - ISBNInput
  - ValidationStatus
  - ExportButtons
- [ ] 함수 유닛 테스트
  - Zod 스키마 검증
  - API 클라이언트 함수
  - 커스텀 검증 함수
- [ ] 통합 테스트
  - 전체 폼 제출 플로우
  - API 호출 흐름
  - 오류 처리 시나리오

**기대 결과**: 85% 이상 테스트 커버리지

**예상 파일 수**: 12-15개

---

### Phase 8: E2E 테스트 (Priority: MEDIUM)

**목표**: Playwright로 사용자 시나리오 E2E 테스트

**작업 항목**:
- [ ] 도서 정보 입력 → KORMARC 생성 → 내보내기 플로우
- [ ] ISBN 검증 오류 처리 테스트
- [ ] API 오류 처리 테스트
- [ ] 폼 자동 저장 테스트
- [ ] 여러 브라우저에서의 크로스 브라우저 테스트

**기대 결과**: 주요 사용자 시나리오 검증

**예상 파일 수**: 3-4개

---

### Phase 9: 접근성 및 성능 최적화 (Priority: MEDIUM)

**목표**: WCAG 2.1 AA 준수, 성능 지표 달성

**작업 항목**:
- [ ] WCAG 2.1 AA 컴플라이언스 검증
  - 키보드 네비게이션
  - 스크린 리더 호환성
  - 색상 대비 (WCAG AA: 4.5:1)
  - alt 텍스트 및 aria-label
- [ ] 성능 최적화
  - 번들 크기 분석 및 최적화 (< 100KB gzipped)
  - FCP < 1.5초 달성
  - Lighthouse 점수 ≥ 90

**기대 결과**: WCAG 2.1 AA 달성, 성능 지표 충족

**예상 파일 수**: 2-3개 (기존 파일 수정)

---

## 4. 기술적 고려사항 (Technical Considerations)

### 백엔드 의존성
- **SPEC-WEB-001** 백엔드가 안정적으로 동작해야 함
- API 응답 시간이 P95 < 200ms 이상이어야 프론트엔드 성능 달성 가능

### 네트워크 안정성
- 느린 네트워크에서도 사용 가능한 UI
- 재시도 로직 (exponential backoff)
- 오프라인 폼 데이터 저장 (localStorage)

### 브라우저 호환성
- Chrome, Firefox, Safari, Edge 최신 2버전 지원
- async/await 문법 사용 (Babel 트랜스파일)
- CSS Grid/Flexbox 호환성 확인

### 보안
- XSS 방지: React 자동 이스케이프
- CSRF 토큰 (필요시)
- Content Security Policy (CSP) 헤더

---

## 5. 리스크 분석 및 완화 (Risk Management)

### Risk 1: 백엔드 API 변경

**설명**: SPEC-WEB-001 API 스펙이 변경되어 프론트엔드 호환성 문제 발생

**가능성**: 중간 | **영향**: 높음

**완화 방안**:
- API 클라이언트를 별도 파일 (api-client.ts)에서 관리
- 타입 정의를 명확히 유지
- 주기적인 통합 테스트 실행

---

### Risk 2: 네트워크 오류 및 타임아웃

**설명**: 느린 네트워크 또는 API 서버 응답 불가로 인한 사용자 경험 저하

**가능성**: 높음 | **영향**: 중간

**완화 방안**:
- 명확한 오류 메시지 제공
- 자동 재시도 로직 (최대 3회)
- 로딩 상태 표시
- localStorage 임시 저장

---

### Risk 3: 폼 데이터 손실

**설명**: 페이지 새로고침 또는 브라우저 종료로 인한 사용자 입력 데이터 손실

**가능성**: 중간 | **영향**: 중간

**완화 방안**:
- localStorage 자동 저장 (Phase 6)
- 초기화 버튼을 통한 명시적 삭제
- 저장된 데이터 복원 기능

---

### Risk 4: 테스트 커버리지 부족

**설명**: 테스트 부족으로 인한 버그 발생

**가능성**: 중간 | **영향**: 높음

**완화 방안**:
- Phase 7, 8에서 85% 이상 커버리지 목표
- E2E 테스트로 주요 시나리오 검증

---

## 6. 일정 (Timeline)

**우선순위 기반 마일스톤** (시간 추정 없음 - TRUST 원칙)

| Phase | 단계명 | 상태 | 의존성 |
|-------|--------|------|--------|
| 1 | 프로젝트 초기 설정 | 대기 | 없음 |
| 2 | 폼 컴포넌트 및 검증 | 대기 | Phase 1 |
| 3 | KORMARC API 통합 | 대기 | Phase 2 |
| 4 | 결과 표시 및 내보내기 | 대기 | Phase 3 |
| 5 | 상태 표시 UI | 대기 | Phase 4 |
| 6 | 폼 자동 저장 | 대기 | Phase 2 |
| 7 | 단위/통합 테스트 | 대기 | Phase 5 |
| 8 | E2E 테스트 | 대기 | Phase 7 |
| 9 | 접근성/성능 최적화 | 대기 | Phase 8 |

---

## 7. 리소스 및 인원 (Resources)

- **개발자**: 1-2명 (프론트엔드 전담)
- **QA 테스터**: 1명 (테스트 및 검증)
- **디자인**: Shadcn UI 기본 디자인 활용 (별도 디자인 작업 없음)

---

## 8. 의존성 및 협력 (Dependencies)

- **SPEC-WEB-001**: 백엔드 API 안정성
- **SPEC-VALIDATION-001**: ISBN 검증 알고리즘 (백엔드)

---

## 9. 다음 단계 (Next Steps)

1. **Phase 1 시작**: `/moai:2-run SPEC-FRONTEND-001`로 구현 시작
2. **주기적 검토**: 각 Phase 완료 후 검증
3. **테스트 실행**: Unit, Integration, E2E 테스트 자동 실행
4. **배포**: Phase 9 완료 후 Vercel 배포
