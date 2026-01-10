# 구현 계획: SPEC-VALIDATION-001

**TAG**: `[SPEC-VALIDATION-001]`

---

## 1. 구현 개요

### 1.1 목표
KORMARC Parser 종합 검증 시스템을 4단계에 걸쳐 구현하여, 100개 수집 레코드의 품질을 자동 검증하고 상세 보고서를 생성한다.

### 1.2 전체 일정
- **Phase 1**: 핵심 검증 구현 (우선순위 1)
- **Phase 2**: 의미 검증 (우선순위 1)
- **Phase 3**: 표준 준수 및 교차 검증 (우선순위 2)
- **Phase 4**: 보고서 및 문서화 (우선순위 2)

### 1.3 성공 기준
- 5단계 검증 계층 모두 구현 완료
- 100개 레코드 일괄 검증 성공
- 테스트 커버리지 85% 이상 달성
- 검증 보고서 Markdown/JSON 형식 생성

---

## 2. Phase 1: 핵심 검증 구현

### 2.1 목표
구조 검증 및 Nowon 검증기를 구현하여 기본 검증 프레임워크를 완성한다.

### 2.2 작업 항목

#### 2.2.1 구조 검증기 생성
**파일**: `src/kormarc/validators/structure_validator.py`

**구현 내용**:
- Leader 검증: 24자 고정 길이, 각 위치별 값 범위
- Directory 검증: 12자 단위 엔트리, 필드 태그/길이/시작위치
- Fields 검증: 필드 구분자, 서브필드 구분자, 레코드 종결자

**클래스 설계**:
```python
class StructureValidator:
    def validate_leader(self, leader: str) -> ValidationResult
    def validate_directory(self, directory: str) -> ValidationResult
    def validate_fields(self, fields: list) -> ValidationResult
    def validate(self, record: KORMARCRecord) -> ValidationResult
```

**테스트 파일**: `tests/validators/test_structure_validator.py`

**예상 작업 시간**: 2-3일

#### 2.2.2 Nowon 검증기 생성
**파일**: `src/kormarc/validators/nowon_validator.py`

**구현 내용**:
- 040 필드 형식 검증: `040   ##$aNLK$bkor$c(NLK)$dNLK$eKORMARC2014`
- 필수 서브필드 확인: $a, $b, $c, $d, $e
- 고정값 검증: 각 서브필드 정확한 값 매칭

**클래스 설계**:
```python
class NowonValidator:
    REQUIRED_040_FORMAT = {
        'a': 'NLK',
        'b': 'kor',
        'c': '(NLK)',
        'd': 'NLK',
        'e': 'KORMARC2014'
    }

    def validate_040_field(self, field_040: Field) -> ValidationResult
    def validate(self, record: KORMARCRecord) -> ValidationResult
```

**테스트 파일**: `tests/validators/test_nowon_validator.py`

**예상 작업 시간**: 1-2일

#### 2.2.3 일괄 검증 스크립트 생성
**파일**: `scripts/validate_100_records.py`

**구현 내용**:
- 데이터베이스에서 100개 레코드 로드
- 각 레코드에 대해 구조 검증 및 Nowon 검증 실행
- 검증 결과 수집 및 통계 생성
- 프로그레스 바 표시 (Rich 라이브러리 사용)

**주요 함수**:
```python
def load_records_from_db(db_path: str) -> list[KORMARCRecord]
def validate_single_record(record: KORMARCRecord) -> ValidationReport
def validate_batch(records: list[KORMARCRecord]) -> BatchValidationReport
def main()
```

**예상 작업 시간**: 1-2일

#### 2.2.4 샘플 테스트
**대상**: 20개 샘플 레코드

**검증 항목**:
- 구조 검증 통과율 확인
- Nowon 040 필드 형식 준수 확인
- 오류 메시지 정확성 검증

**예상 작업 시간**: 1일

### 2.3 Phase 1 산출물
- `src/kormarc/validators/structure_validator.py`
- `src/kormarc/validators/nowon_validator.py`
- `scripts/validate_100_records.py`
- `tests/validators/test_structure_validator.py`
- `tests/validators/test_nowon_validator.py`
- Phase 1 검증 결과 보고서 (샘플 20개 레코드)

---

## 3. Phase 2: 의미 검증

### 3.1 목표
필드 간 관계 검증 및 필수 필드 확인을 통해 의미 수준 검증을 구현한다.

### 3.2 작업 항목

#### 3.2.1 의미 검증기 생성
**파일**: `src/kormarc/validators/semantic_validator.py`

**구현 내용**:
- 필수 필드 존재 확인: 001, 040, 245, 260
- 권장 필드 확인: 020 (ISBN), 650 (주제명)
- 조건부 필수 필드: 100 (저자명, 단행본), 300 (형태사항, 물리자료)
- 필드 간 관계 검증: 예) 100 + 245 조합

**클래스 설계**:
```python
class SemanticValidator:
    REQUIRED_FIELDS = ['001', '040', '245', '260']
    RECOMMENDED_FIELDS = ['020', '650']
    CONDITIONAL_REQUIRED = {
        '100': lambda record: record.is_monograph(),
        '300': lambda record: record.is_physical_material()
    }

    def validate_required_fields(self, record: KORMARCRecord) -> ValidationResult
    def validate_field_relationships(self, record: KORMARCRecord) -> ValidationResult
    def validate(self, record: KORMARCRecord) -> ValidationResult
```

**테스트 파일**: `tests/validators/test_semantic_validator.py`

**예상 작업 시간**: 2-3일

#### 3.2.2 필드 간 관계 검증 로직
**검증 규칙 예시**:
- 100 필드 (저자명) 존재 시 → 245 필드 (표제)도 필수
- 260 필드 (발행사항) → 최소 발행년 ($c) 필수
- 300 필드 (형태사항) → 최소 수량 ($a) 필수

**예상 작업 시간**: 1-2일

#### 3.2.3 통합 테스트
**대상**: 50개 레코드 (Phase 1 샘플 20개 + 추가 30개)

**검증 항목**:
- 필수 필드 누락 감지
- 조건부 필수 필드 로직 정확성
- 필드 간 관계 검증 정확성

**예상 작업 시간**: 1일

### 3.3 Phase 2 산출물
- `src/kormarc/validators/semantic_validator.py`
- `tests/validators/test_semantic_validator.py`
- Phase 2 검증 결과 보고서 (샘플 50개 레코드)

---

## 4. Phase 3: 표준 준수 및 교차 검증

### 4.1 목표
pymarc 라이브러리 통합 및 라운드트립 변환 테스트를 통해 표준 준수를 검증한다.

### 4.2 작업 항목

#### 4.2.1 pymarc 라이브러리 통합
**파일**: `src/kormarc/validators/standard_validator.py`

**구현 내용**:
- pymarc 설치 및 import
- KORMARC 레코드 → pymarc Record 변환
- pymarc 파싱 성공 여부 확인
- 파싱 실패 시 비표준 플래그 설정

**클래스 설계**:
```python
class StandardValidator:
    def parse_with_pymarc(self, record: KORMARCRecord) -> pymarc.Record | None
    def validate_pymarc_compatibility(self, record: KORMARCRecord) -> ValidationResult
    def validate(self, record: KORMARCRecord) -> ValidationResult
```

**테스트 파일**: `tests/validators/test_standard_validator.py`

**예상 작업 시간**: 2-3일

#### 4.2.2 교차 검증기 생성
**파일**: `src/kormarc/validators/cross_validator.py`

**구현 내용**:
- Record → XML 변환 (KORMARCRecord → MARCXML)
- XML → Record 변환 (MARCXML → KORMARCRecord)
- 라운드트립 일관성 검증 (원본 ≈ 변환 후)
- pymarc 객체 일관성 검증

**클래스 설계**:
```python
class CrossValidator:
    def record_to_xml(self, record: KORMARCRecord) -> str
    def xml_to_record(self, xml: str) -> KORMARCRecord
    def validate_roundtrip(self, record: KORMARCRecord) -> ValidationResult
    def validate(self, record: KORMARCRecord) -> ValidationResult
```

**테스트 파일**: `tests/validators/test_cross_validator.py`

**예상 작업 시간**: 2-3일

#### 4.2.3 통합 테스트
**대상**: 전체 100개 레코드

**검증 항목**:
- pymarc 파싱 성공률 (목표: 95% 이상)
- 라운드트립 일관성 검증
- 비표준 레코드 플래깅 정확성

**예상 작업 시간**: 1일

### 4.3 Phase 3 산출물
- `src/kormarc/validators/standard_validator.py`
- `src/kormarc/validators/cross_validator.py`
- `tests/validators/test_standard_validator.py`
- `tests/validators/test_cross_validator.py`
- Phase 3 검증 결과 보고서 (전체 100개 레코드)

---

## 5. Phase 4: 보고서 및 문서화

### 5.1 목표
종합 검증 보고서를 생성하고 발견사항을 문서화한다.

### 5.2 작업 항목

#### 5.2.1 보고서 생성기 생성
**파일**: `src/kormarc/validators/report_generator.py`

**구현 내용**:
- Markdown 형식 보고서 생성
- JSON 형식 구조화된 데이터 출력
- 통계 요약: 성공/실패 건수, 검증 단계별 통과율
- 오류 목록: 필드 위치, 오류 내용, 수정 제안

**클래스 설계**:
```python
class ReportGenerator:
    def generate_markdown(self, results: list[ValidationResult]) -> str
    def generate_json(self, results: list[ValidationResult]) -> str
    def generate_summary_statistics(self, results: list[ValidationResult]) -> dict
    def save_report(self, report: str, output_path: str)
```

**테스트 파일**: `tests/validators/test_report_generator.py`

**예상 작업 시간**: 2-3일

#### 5.2.2 전체 100개 레코드 검증
**실행 스크립트**: `scripts/validate_100_records.py` (업데이트)

**검증 흐름**:
1. 데이터베이스에서 100개 레코드 로드
2. 각 레코드에 대해 5단계 검증 실행
3. 검증 결과 수집 및 데이터베이스 저장
4. 보고서 생성 및 저장

**출력 파일**:
- `data/validation_reports/validation_report_100_records.md`
- `data/validation_reports/validation_report_100_records.json`

**예상 작업 시간**: 1일

#### 5.2.3 발견사항 및 권장사항 문서화
**파일**: `docs/VALIDATION_FINDINGS.md`

**포함 내용**:
- 검증 결과 요약
- 발견된 문제점 분류 (구조, 의미, 표준 준수)
- 개선 권장사항
- 향후 검증 규칙 추가 제안

**예상 작업 시간**: 1-2일

### 5.3 Phase 4 산출물
- `src/kormarc/validators/report_generator.py`
- `tests/validators/test_report_generator.py`
- `data/validation_reports/validation_report_100_records.md`
- `data/validation_reports/validation_report_100_records.json`
- `docs/VALIDATION_FINDINGS.md`

---

## 6. 기술 접근 방법

### 6.1 아키텍처 패턴
- **검증기 패턴**: 각 검증기는 독립적인 클래스로 구현
- **조합 패턴**: ValidationOrchestrator가 모든 검증기를 조합
- **전략 패턴**: 검증 규칙을 동적으로 교체 가능

### 6.2 오류 처리 전략
- 각 검증 단계는 실패해도 다음 단계 계속 실행
- 모든 오류는 ValidationResult 객체에 수집
- 치명적 오류 (구조 검증 실패) 시에만 중단

### 6.3 성능 최적화
- 배치 처리: 한 번에 여러 레코드 로드
- 병렬 처리 (선택): 독립적인 레코드 검증 병렬화
- 캐싱: 반복 검증 시 결과 재사용

### 6.4 테스트 전략
- **단위 테스트**: 각 검증기별 독립 테스트
- **통합 테스트**: 전체 검증 파이프라인 테스트
- **회귀 테스트**: 기존 레코드 검증 결과 비교

---

## 7. 리스크 완화 계획

### 7.1 pymarc 비호환 리스크
**완화 방안**:
- Phase 1에서 샘플 레코드로 사전 테스트
- 파싱 실패 시 내부 검증기로 fallback
- 비표준 플래그 설정 및 수동 검토 권장

### 7.2 성능 저하 리스크
**완화 방안**:
- 프로그레스 바로 진행 상황 추적
- 배치 크기 조정 (예: 10개씩)
- 병렬 처리 옵션 제공 (선택)

### 7.3 오탐 리스크
**완화 방안**:
- Phase 별 샘플 레코드 수동 검토
- 검증 규칙 정밀 조정
- 경고 수준 분류 (ERROR, WARNING, INFO)

---

## 8. 품질 게이트

### 8.1 Phase 별 성공 기준

**Phase 1**:
- 구조 검증기 단위 테스트 100% 통과
- Nowon 검증기 단위 테스트 100% 통과
- 샘플 20개 레코드 검증 성공

**Phase 2**:
- 의미 검증기 단위 테스트 100% 통과
- 샘플 50개 레코드 검증 성공
- 필수 필드 누락 감지율 100%

**Phase 3**:
- pymarc 파싱 성공률 95% 이상
- 라운드트립 일관성 검증 95% 이상
- 전체 100개 레코드 검증 완료

**Phase 4**:
- Markdown/JSON 보고서 생성 성공
- 발견사항 문서화 완료
- 테스트 커버리지 85% 이상

### 8.2 전체 프로젝트 성공 기준
- 5단계 검증 계층 모두 구현 완료
- 100개 레코드 일괄 검증 성공
- 종합 검증 보고서 생성
- TRUST-5 품질 기준 충족

---

## 9. 데이터베이스 변경사항

### 9.1 새로운 테이블 생성
**테이블**: `validation_results`

**스키마**:
```sql
CREATE TABLE validation_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    validation_status TEXT CHECK(validation_status IN ('valid', 'invalid', 'non-standard')),
    validation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_version TEXT,
    errors JSON,
    warnings JSON,
    tier1_passed BOOLEAN,
    tier2_passed BOOLEAN,
    tier3_passed BOOLEAN,
    tier4_passed BOOLEAN,
    tier5_passed BOOLEAN,
    FOREIGN KEY (record_id) REFERENCES kormarc_records(id)
);
```

### 9.2 기존 테이블 변경
**테이블**: `kormarc_records`

**추가 컬럼** (선택):
```sql
ALTER TABLE kormarc_records ADD COLUMN last_validated TIMESTAMP;
ALTER TABLE kormarc_records ADD COLUMN validation_status TEXT;
```

---

## 10. 산출물 체크리스트

### 10.1 코드 산출물
- [ ] `src/kormarc/validators/structure_validator.py`
- [ ] `src/kormarc/validators/nowon_validator.py`
- [ ] `src/kormarc/validators/semantic_validator.py`
- [ ] `src/kormarc/validators/standard_validator.py`
- [ ] `src/kormarc/validators/cross_validator.py`
- [ ] `src/kormarc/validators/report_generator.py`
- [ ] `scripts/validate_100_records.py`

### 10.2 테스트 산출물
- [ ] `tests/validators/test_structure_validator.py`
- [ ] `tests/validators/test_nowon_validator.py`
- [ ] `tests/validators/test_semantic_validator.py`
- [ ] `tests/validators/test_standard_validator.py`
- [ ] `tests/validators/test_cross_validator.py`
- [ ] `tests/validators/test_report_generator.py`

### 10.3 문서 산출물
- [ ] `data/validation_reports/validation_report_100_records.md`
- [ ] `data/validation_reports/validation_report_100_records.json`
- [ ] `docs/VALIDATION_FINDINGS.md`

### 10.4 데이터베이스 산출물
- [ ] `validation_results` 테이블 생성
- [ ] 100개 레코드 검증 결과 저장

---

## 11. 다음 단계

### 11.1 즉시 실행
- `/moai:2-run SPEC-VALIDATION-001` 명령 실행
- Phase 1 TDD 개발 시작
- 구조 검증기 RED-GREEN-REFACTOR 사이클

### 11.2 장기 계획
- Phase 1-4 순차 실행
- 각 Phase 완료 후 중간 보고서 생성
- 전체 완료 후 `/moai:3-sync SPEC-VALIDATION-001` 실행

---

**문서 버전**: 1.0.0
**최종 수정**: 2026-01-10
**승인 상태**: 계획됨 (Planned)
**TAG**: `[SPEC-VALIDATION-001]`
