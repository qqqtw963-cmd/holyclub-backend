# holyclub-backend

HolyClub 전용 Django backend repository.

## Goals
- HolyClub 전용 API / auth / content backend
- AWS Seoul (`ap-northeast-2`) 기준 운영
- OpenAPI 유지 (`/openapi.json`)
- ECS Fargate + RDS PostgreSQL + S3 + Secrets Manager 배포 기준

## Current status
- `overcomer-django/src`를 기반으로 초기 스캐폴드 분리 완료
- 브랜드/도메인/시크릿 네이밍을 HolyClub 기준으로 전환 중
- Docker / ECR / ECS 배포 뼈대 정리 예정

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.test
python manage.py runserver
```

## Next steps
1. HolyClub 도메인/시크릿/버킷 이름 확정
2. local/dev/prod 설정 분리 정리
3. ECR/ECS 배포 경로 연결
4. RN generated client와 호환되는 핵심 API 우선 유지
