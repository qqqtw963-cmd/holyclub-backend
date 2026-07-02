# ECS production deploy checklist

HolyClub backend 운영 배포 시 이번 `home_content` 장애 복구에서 실제로 확인된 문제를 재발 방지하기 위한 체크리스트.

## 1. source of truth 정리
- 운영 복구에 사용한 수정이 반드시 **repo 기준 파일**에 반영되어 있어야 한다.
- `/tmp/holyclub-backend-hotfix*` 같은 임시 빌드 디렉터리는 참조용으로만 사용하고, 최종 배포 전에는 아래 파일들이 repo와 일치하는지 확인한다.
  - `Dockerfile`
  - `gunicorn.conf.py`
  - `requirements.txt`
  - `app/home_content/**`
  - `app/urls/api.py`
  - `config/settings/base.py`
  - `config/settings/prod.py`
  - `config/settings/test.py`

## 2. 이미지 빌드 전 필수 확인
- `requirements.txt`에서 PostgreSQL 드라이버가 운영 DB 인증 방식과 맞는지 확인한다.
  - 이번 장애 원인: `psycopg2-binary==2.9.5` 조합으로는 `SCRAM authentication requires libpq version 10 or above` 발생
  - 복구 기준: `psycopg2==2.9.10`
- `Dockerfile`에 `libpq-dev`가 포함되어 있는지 확인한다.
- 캐시 오염이 의심되면 `docker buildx build --no-cache ...` 로 재빌드한다.

## 3. gunicorn / ALB 정합성
- ALB target group 포트와 컨테이너 gunicorn bind 포트가 일치해야 한다.
- 현재 기준값:
  - gunicorn bind: `0.0.0.0:8000`
  - ECS/ALB health check 대상 포트: `8000`
- `gunicorn.conf.py`와 task definition의 container port mapping을 함께 확인한다.

## 4. 마이그레이션
- 새 앱(`home_content`) 또는 새 테이블이 포함된 배포라면, ECS 서비스 안정화와 별개로 **운영 마이그레이션**이 반드시 필요하다.
- 권장 방식:
  - ECS exec 임시 접속보다 **Fargate 단발 태스크**로 `python manage.py migrate --settings=config.settings.prod` 실행
- 이번 복구에서 확인된 실제 적용 항목:
  - `home_content.0001_initial`

## 5. ECS 배포 순서
1. 새 이미지 빌드/푸시
2. 새 task definition 등록
3. ECS 서비스 업데이트
4. 새 태스크 `RUNNING` 확인
5. ALB target health가 `healthy` 로 전환되는지 확인
6. 이전 태스크가 draining 후 정리되는지 확인
7. 필요한 경우 마이그레이션 단발 태스크 실행

## 6. 스모크 테스트
배포 후 아래 엔드포인트를 확인한다.

```bash
curl https://api.holyclub.co.kr/v1/home_content/current/
curl 'https://api.holyclub.co.kr/v1/notification/?limit=3&offset=0'
```

확인 포인트:
- `/v1/home_content/current/` → `200`
- `/v1/notification/` → `200`
- 랜딩 페이지 `https://holyclub.co.kr` 에서 hero 문구와 최신 소식 영역 정상 노출

상세 절차는 `docs/runtime-content-smoke-test.md` 참고.

## 7. 로그 확인 포인트
- CloudWatch app log
- `holyclub/prod/error`
- `/ecs/holyclub-api`

특히 아래 키워드를 우선 확인한다.
- `SCRAM authentication requires libpq version 10 or above`
- `UndefinedTable`
- gunicorn bind/boot failure
- Firebase credential initialization warning

## 8. 후속 운영 점검
- `home_content` 데이터가 실제 운영 의도에 맞게 활성화(`is_active=True`) 되어 있는지 확인
- Firebase 경고가 남아 있다면 `holyclub/firebase` secret 구조와 `credentials.Certificate(...)` 입력 형식을 점검
- 복구에 사용한 변경은 즉시 git commit / push 해서 다음 배포에서 재현 가능하게 만든다.
