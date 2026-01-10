# 인수 기준: SPEC-VALIDATION-001

**TAG**: `[SPEC-VALIDATION-001]`

---

## 1. 개요

### 1.1 목적
KORMARC Parser 종합 검증 시스템의 인수 기준을 정의하여, 구현 완료 후 품질 및 기능 요구사항 충족 여부를 검증한다.

### 1.2 인수 범위
- 5단계 검증 계층 전체 동작 검증
- 100개 레코드 일괄 검증 성공 확인
- 보고서 생성 및 형식 검증
- TRUST-5 품질 기준 충족 확인

---

## 2. 인수 시나리오 (Given-When-Then)

### Scenario 1: 유효한 레코드 검증

**시나리오 ID**: AC-001
**우선순위**: HIGH
**설명**: 모든 필수 필드를 포함하고 Nowon 사양을 준수하는 유효한 KORMARC 레코드를 검증한다.

**Given** (전제 조건):
- 유효한 KORMARC 레코드가 준비되어 있다
- 레코드는 다음 필수 필드를 모두 포함한다:
  - 001 (제어번호): "KOR2024000001"
  - 040 (목록작성기관): "040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014"
  - 245 (표제): "245 00$a파이썬 프로그래밍"
  - 260 (발행사항): "260   $a서울$b한빛미디어$c2024"
- 레코드 구조가 KORMARC 2014 표준을 준수한다
  - Leader: 24자 고정 길이
  - Directory: 12자 단위 엔트리
  - Fields: 올바른 구분자 사용

**When** (실행):
- 검증 시스템이 해당 레코드에 대해 전체 검증을 실행한다
- 5단계 검증 계층이 순차적으로 실행된다:
  1. Tier 1: 구조 검증
  2. Tier 2: 데이터 무결성 검증
  3. Tier 3: 의미 검증
  4. Tier 4: 표준 준수 검증
  5. Tier 5: 교차 검증

**Then** (기대 결과):
- 모든 5단계 검증 계층이 통과해야 한다
  - `tier1_passed = True`
  - `tier2_passed = True`
  - `tier3_passed = True`
  - `tier4_passed = True`
  - `tier5_passed = True`
- 검증 보고서에 "100% 준수" 표시가 나타나야 한다
- 레코드 상태가 "valid"로 표시되어야 한다
  - `validation_status = "valid"`
- 오류 목록이 비어 있어야 한다
  - `errors = []`
- 경고 목록이 비어 있어야 한다
  - `warnings = []`
- 검증 결과가 데이터베이스 `validation_results` 테이블에 저장되어야 한다

**검증 방법**:
```python
# pytest 테스트 케이스
def test_valid_record_validation():
    # Given
    record = create_valid_kormarc_record()
    validator = ValidationOrchestrator()

    # When
    result = validator.validate(record)

    # Then
    assert result.tier1_passed is True
    assert result.tier2_passed is True
    assert result.tier3_passed is True
    assert result.tier4_passed is True
    assert result.tier5_passed is True
    assert result.validation_status == "valid"
    assert len(result.errors) == 0
    assert len(result.warnings) == 0
```

---

### Scenario 2: 040 필드 형식 오류 감지

**시나리오 ID**: AC-002
**우선순위**: HIGH
**설명**: Nowon 사양을 위반하는 040 필드 형식을 정확하게 감지한다.

**Given** (전제 조건):
- KORMARC 레코드가 준비되어 있다
- 레코드는 다른 필수 필드를 모두 포함하지만, 040 필드 형식이 잘못되었다
- 잘못된 040 필드 예시:
  - `040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2`
    (정확한 형식: `$eKORMARC2014`)

**When** (실행):
- Nowon 검증기가 실행된다
- 040 필드 형식 검증이 수행된다

**Then** (기대 결과):
- Tier 3 의미 검증이 실패해야 한다
  - `tier3_passed = False`
- 검증 상태가 "invalid"로 표시되어야 한다
  - `validation_status = "invalid"`
- 특정 오류 메시지가 생성되어야 한다:
  - 오류 내용: "040 필드 $e 오류: 'KORMARC2014' 필요, 'KORMARC2' 발견"
  - 오류 위치: `field_tag = "040", subfield_code = "e"`
- 오류 메시지에 올바른 형식이 명시되어야 한다:
  - 예상 형식: `040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014`
- 검증 보고서에 오류가 포함되어야 한다

**검증 방법**:
```python
# pytest 테스트 케이스
def test_invalid_040_field_detection():
    # Given
    record = create_kormarc_record_with_invalid_040()
    validator = NowonValidator()

    # When
    result = validator.validate_040_field(record.get_field("040"))

    # Then
    assert result.passed is False
    assert result.error_message == "040 필드 $e 오류: 'KORMARC2014' 필요, 'KORMARC2' 발견"
    assert result.field_tag == "040"
    assert result.subfield_code == "e"
    assert "040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014" in result.expected_format
```

---

### Scenario 3: 100개 레코드 일괄 검증

**시나리오 ID**: AC-003
**우선순위**: HIGH
**설명**: 데이터베이스에 저장된 100개의 KORMARC 레코드를 일괄 검증하고 종합 보고서를 생성한다.

**Given** (전제 조건):
- `data/kormarc_prototype_100.db` 데이터베이스에 100개의 KORMARC 레코드가 저장되어 있다
- 검증 시스템이 초기화되어 있다
- 출력 디렉토리 `data/validation_reports/`가 존재한다

**When** (실행):
- 일괄 검증 스크립트 `scripts/validate_100_records.py`가 실행된다
- 각 레코드에 대해 5단계 검증이 순차적으로 수행된다
- 검증 진행 상황이 프로그레스 바로 표시된다

**Then** (기대 결과):
- 모든 100개 레코드가 검증되어야 한다
  - 처리된 레코드 수: 100
- 검증 보고서가 생성되어야 한다:
  - Markdown 형식: `data/validation_reports/validation_report_100_records.md`
  - JSON 형식: `data/validation_reports/validation_report_100_records.json`
- 검증 보고서에 성공률이 표시되어야 한다:
  - 전체 성공률: `XX%`
  - 단계별 성공률:
    - Tier 1 (구조 검증): `XX%`
    - Tier 2 (데이터 무결성): `XX%`
    - Tier 3 (의미 검증): `XX%`
    - Tier 4 (표준 준수): `XX%`
    - Tier 5 (교차 검증): `XX%`
- 실패한 레코드 목록이 포함되어야 한다:
  - 레코드 ID
  - 실패한 검증 단계
  - 구체적인 오류 메시지
- Markdown 보고서 형식 예시:
  ```markdown
  # KORMARC 검증 보고서

  ## 요약
  - 총 레코드 수: 100
  - 성공: 85
  - 실패: 15
  - 전체 성공률: 85%

  ## 단계별 성공률
  - Tier 1 (구조 검증): 100%
  - Tier 2 (데이터 무결성): 95%
  - Tier 3 (의미 검증): 90%
  - Tier 4 (표준 준수): 88%
  - Tier 5 (교차 검증): 85%

  ## 실패 레코드
  | 레코드 ID | 실패 단계 | 오류 메시지 |
  |-----------|-----------|-------------|
  | 5 | Tier 3 | 040 필드 형식 오류 |
  | 12 | Tier 2 | 필수 필드 245 누락 |
  ```
- JSON 보고서에 구조화된 데이터가 포함되어야 한다:
  ```json
  {
    "summary": {
      "total": 100,
      "success": 85,
      "failed": 15,
      "success_rate": 0.85
    },
    "tier_success_rates": {
      "tier1": 1.0,
      "tier2": 0.95,
      "tier3": 0.90,
      "tier4": 0.88,
      "tier5": 0.85
    },
    "failed_records": [
      {"record_id": 5, "failed_tier": "tier3", "error": "040 필드 형식 오류"},
      {"record_id": 12, "failed_tier": "tier2", "error": "필수 필드 245 누락"}
    ]
  }
  ```

**검증 방법**:
```python
# pytest 테스트 케이스
def test_batch_validation_100_records():
    # Given
    db_path = "data/kormarc_prototype_100.db"
    output_dir = "data/validation_reports/"

    # When
    result = run_batch_validation(db_path, output_dir)

    # Then
    assert result.total_records == 100
    assert result.processed_records == 100

    # 보고서 파일 존재 확인
    assert os.path.exists(f"{output_dir}/validation_report_100_records.md")
    assert os.path.exists(f"{output_dir}/validation_report_100_records.json")

    # Markdown 보고서 내용 검증
    with open(f"{output_dir}/validation_report_100_records.md") as f:
        report_md = f.read()
        assert "총 레코드 수: 100" in report_md
        assert "전체 성공률:" in report_md
        assert "## 실패 레코드" in report_md

    # JSON 보고서 내용 검증
    with open(f"{output_dir}/validation_report_100_records.json") as f:
        report_json = json.load(f)
        assert report_json["summary"]["total"] == 100
        assert "tier_success_rates" in report_json
        assert "failed_records" in report_json
```

---

### Scenario 4: 필수 필드 누락 감지

**시나리오 ID**: AC-004
**우선순위**: HIGH
**설명**: 필수 필드가 누락된 레코드를 정확하게 감지하고 거부한다.

**Given** (전제 조건):
- KORMARC 레코드가 준비되어 있다
- 레코드는 필수 필드 245 (표제)가 누락되어 있다
- 다른 필드는 모두 유효하다

**When** (실행):
- 의미 검증기가 필수 필드 확인을 실행한다

**Then** (기대 결과):
- Tier 3 의미 검증이 실패해야 한다
  - `tier3_passed = False`
- 검증 상태가 "invalid"로 표시되어야 한다
- 오류 메시지가 생성되어야 한다:
  - "필수 필드 245 누락"
- 레코드가 데이터베이스에 저장되지 않아야 한다 (또는 "invalid" 상태로 저장)

**검증 방법**:
```python
def test_missing_required_field_detection():
    # Given
    record = create_kormarc_record_missing_field_245()
    validator = SemanticValidator()

    # When
    result = validator.validate_required_fields(record)

    # Then
    assert result.passed is False
    assert "필수 필드 245 누락" in result.error_message
    assert result.missing_fields == ["245"]
```

---

### Scenario 5: pymarc 비호환 레코드 처리

**시나리오 ID**: AC-005
**우선순위**: MEDIUM
**설명**: pymarc 라이브러리가 파싱할 수 없는 비표준 레코드를 감지하고 적절히 처리한다.

**Given** (전제 조건):
- KORMARC 레코드가 준비되어 있다
- 레코드는 구조적으로 유효하지만 pymarc가 파싱할 수 없는 형식이다
  - 예: 비표준 인코딩, 커스텀 확장 필드

**When** (실행):
- 표준 준수 검증기가 pymarc 파싱을 시도한다
- pymarc 파싱이 실패한다

**Then** (기대 결과):
- Tier 4 표준 준수 검증이 실패하거나 경고를 출력해야 한다
  - `tier4_passed = False` 또는 `tier4_warning = True`
- 검증 상태가 "non-standard"로 표시되어야 한다
  - `validation_status = "non-standard"`
- 호환성 경고가 생성되어야 한다:
  - "pymarc 파싱 실패: 비표준 MARC 형식 감지"
- 내부 검증기로 fallback하여 나머지 검증을 계속 진행해야 한다
- 수동 검토 권장 메시지가 포함되어야 한다

**검증 방법**:
```python
def test_pymarc_incompatible_record_handling():
    # Given
    record = create_nonstandard_kormarc_record()
    validator = StandardValidator()

    # When
    result = validator.validate_pymarc_compatibility(record)

    # Then
    assert result.pymarc_parseable is False
    assert result.validation_status == "non-standard"
    assert "pymarc 파싱 실패" in result.warning_message
    assert "수동 검토 권장" in result.recommendation
```

---

## 3. 성공 기준 (Success Criteria)

### 3.1 기능 성공 기준

**필수 기능 (MUST HAVE)**:
- [ ] 5단계 검증 계층 모두 구현 완료
- [ ] 필수 필드(001, 040, 245, 260) 검증 정확도 100%
- [ ] Nowon 040 필드 형식 검증 정확도 100%
- [ ] 100개 레코드 일괄 검증 성공
- [ ] Markdown 및 JSON 형식 보고서 생성

**권장 기능 (SHOULD HAVE)**:
- [ ] pymarc 교차 검증 성공률 95% 이상
- [ ] 라운드트립 변환 일관성 95% 이상
- [ ] 검증 오류 메시지에 수정 제안 포함

**선택 기능 (COULD HAVE)**:
- [ ] HTML 형식 보고서 생성
- [ ] 외부 MARC 검증기 통합
- [ ] 사용자 정의 검증 규칙 지원

### 3.2 성능 성공 기준

- [ ] 단일 레코드 검증 시간: 1초 이내
- [ ] 100개 레코드 일괄 검증 시간: 5분 이내
- [ ] 보고서 생성 시간: 30초 이내
- [ ] 메모리 사용량: 500MB 이내

### 3.3 품질 성공 기준 (TRUST-5)

**Test-first**:
- [ ] 테스트 커버리지 85% 이상
- [ ] 모든 검증기에 대한 단위 테스트 존재
- [ ] 통합 테스트 100% 통과

**Readable**:
- [ ] 모든 함수에 docstring 존재
- [ ] 변수 및 함수명이 명확하고 설명적
- [ ] 코드 린터(ruff) 경고 0개

**Unified**:
- [ ] 일관된 코드 스타일 적용 (black, isort)
- [ ] 검증 결과 형식 통일 (ValidationResult 클래스)
- [ ] 오류 메시지 형식 통일

**Secured**:
- [ ] SQL 인젝션 방지 (파라미터화된 쿼리)
- [ ] 입력 데이터 검증 (Pydantic 모델)
- [ ] 오류 처리 시 민감 정보 노출 방지

**Trackable**:
- [ ] 모든 검증 결과 데이터베이스 저장
- [ ] 검증 버전 정보 기록
- [ ] Git 커밋 메시지에 `[SPEC-VALIDATION-001]` 태그 포함

---

## 4. 검증 환경

### 4.1 테스트 환경
- Python 버전: 3.12+
- 운영체제: Ubuntu 22.04 LTS, Windows 11, macOS Sonoma
- 데이터베이스: SQLite 3.40+
- 테스트 프레임워크: pytest 8.0+

### 4.2 테스트 데이터
- 샘플 레코드: 20개 (Phase 1)
- 중간 테스트: 50개 (Phase 2)
- 전체 검증: 100개 (Phase 3-4)
- 데이터 소스: `data/kormarc_prototype_100.db`

### 4.3 검증 도구
- 단위 테스트: pytest
- 커버리지 측정: pytest-cov
- 린터: ruff
- 타입 체킹: mypy

---

## 5. 인수 체크리스트

### 5.1 기능 검증
- [ ] Scenario 1 (유효한 레코드 검증) 통과
- [ ] Scenario 2 (040 필드 오류 감지) 통과
- [ ] Scenario 3 (100개 레코드 일괄 검증) 통과
- [ ] Scenario 4 (필수 필드 누락 감지) 통과
- [ ] Scenario 5 (pymarc 비호환 처리) 통과

### 5.2 품질 검증
- [ ] 테스트 커버리지 85% 이상
- [ ] 린터 경고 0개
- [ ] 타입 체크 오류 0개
- [ ] 모든 단위 테스트 통과
- [ ] 모든 통합 테스트 통과

### 5.3 문서 검증
- [ ] `docs/VALIDATION_FINDINGS.md` 작성 완료
- [ ] README 업데이트 (사용법 추가)
- [ ] API 문서 생성 (sphinx 또는 pdoc)
- [ ] 검증 보고서 샘플 제공

### 5.4 배포 준비
- [ ] `pyproject.toml` 의존성 업데이트
- [ ] 설치 스크립트 테스트
- [ ] 실행 스크립트 테스트 (`scripts/validate_100_records.py`)
- [ ] CI/CD 파이프라인 통과 (GitHub Actions)

---

## 6. 인수 절차

### 6.1 Phase 별 인수

**Phase 1 인수**:
1. Scenario 1, 2 실행 및 통과 확인
2. 샘플 20개 레코드 검증 결과 검토
3. 구조 및 Nowon 검증기 코드 리뷰

**Phase 2 인수**:
1. Scenario 4 실행 및 통과 확인
2. 샘플 50개 레코드 검증 결과 검토
3. 의미 검증기 코드 리뷰

**Phase 3 인수**:
1. Scenario 5 실행 및 통과 확인
2. 전체 100개 레코드 검증 결과 검토
3. 표준 준수 및 교차 검증기 코드 리뷰

**Phase 4 인수**:
1. Scenario 3 실행 및 통과 확인
2. 보고서 형식 및 내용 검증
3. 문서화 완성도 검토

### 6.2 최종 인수
1. 모든 인수 시나리오 (AC-001 ~ AC-005) 통과 확인
2. 성공 기준 체크리스트 100% 완료 확인
3. TRUST-5 품질 기준 충족 확인
4. 프로덕션 배포 준비 완료 확인

---

## 7. 인수 결과 보고

### 7.1 보고서 형식
**제목**: SPEC-VALIDATION-001 인수 결과 보고서

**포함 내용**:
- 인수 시나리오별 결과 (통과/실패)
- 성공 기준 달성률
- 발견된 이슈 목록 및 해결 상태
- 최종 인수 승인 여부

### 7.2 승인 조건
- 모든 필수 인수 시나리오 통과
- 테스트 커버리지 85% 이상
- TRUST-5 품질 기준 충족
- 프로덕션 배포 가능 상태

---

**문서 버전**: 1.0.0
**최종 수정**: 2026-01-10
**승인 상태**: 계획됨 (Planned)
**TAG**: `[SPEC-VALIDATION-001]`
