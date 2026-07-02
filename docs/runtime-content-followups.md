# Runtime content and Firebase follow-ups

## 1. `home_content` 운영 데이터 점검
현재 API는 fallback 없이도 정상 응답 가능 상태로 복구되었지만, 운영 데이터는 별도로 점검이 필요하다.

### 확인 항목
- 운영 DB에 `home_content` 레코드가 실제로 존재하는지
- 기대하는 hero 문구가 최신 활성 레코드(`is_active=True`) 기준으로 내려가는지
- fallback 응답(`is_active=False`)에 의존하지 않는지

### 권장 조치
- 운영 관리자 또는 shell에서 `HomeContent` 레코드 상태 확인
- 필요 시 운영용 seed 또는 admin 등록으로 대표 레코드 1건 활성화
- 새 레코드 등록 시 기존 활성 레코드가 자동 비활성화되는지 확인

## 2. Firebase warning 후속 점검
현재 설정은 Firebase 자격 증명 초기화 실패 시 앱 전체를 죽이지 않고 경고만 남기도록 되어 있다.

### 현재 코드 위치
- `config/settings/base.py`
- `FIREBASE_ENABLED`
- `FIREBASE_INIT_ERROR`

### 확인 항목
- AWS Secrets Manager `holyclub/firebase` 값이 `firebase_admin.credentials.Certificate(...)` 가 기대하는 JSON 구조인지
- private key 줄바꿈/escape가 깨지지 않았는지
- 운영에서 푸시 알림 기능이 실제로 필요한 시점인지
- 필요 없다면 warning 레벨 유지, 필요하다면 secret 정합성 먼저 복구

### 권장 조치
1. secret payload shape 검증
2. 운영 환경에서 단발 태스크로 Firebase init smoke check
3. 푸시 발송 기능에서 `FIREBASE_ENABLED` false 시 graceful degradation 여부 확인

## 3. 문서/운영 절차
- 배포 전: `docs/ecs-production-deploy-checklist.md`
- 배포 후: `docs/runtime-content-smoke-test.md`

위 두 문서를 배포 기준 문서로 유지하고, 이번 장애에서 확인된 신규 운영 규칙이 있으면 즉시 추가한다.
