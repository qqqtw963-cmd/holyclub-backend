# Runtime content smoke test

## 목적
- 홈 콘텐츠 `/v1/home_content/current/`
- 공지사항 `/v1/notification/`
- 기도 BGM `/v1/prayer_bgm_track/`

이 3개가 운영에서 실제로 앱/랜딩 페이지에 연결되는지 빠르게 확인하기 위한 스모크 테스트 절차입니다.

## 1) 마이그레이션 적용
```bash
python manage.py migrate --settings=config.settings.prod
```

`home_content` 앱이 새로 추가된 상태라면 이 단계가 먼저 되어야 합니다.

## 2) 샘플 데이터 생성
### 홈 콘텐츠 + 공지사항만
```bash
python manage.py seed_runtime_content --skip-bgm --settings=config.settings.prod
```

### 홈 콘텐츠 + 공지사항 + 기도 BGM
```bash
python manage.py seed_runtime_content \
  --bgm-file /absolute/path/to/sample.m4a \
  --bgm-title "기도 배경음 샘플" \
  --settings=config.settings.prod
```

## 3) API 확인
```bash
curl https://api.holyclub.co.kr/v1/home_content/current/
curl 'https://api.holyclub.co.kr/v1/notification/?limit=3&offset=0'
curl 'https://api.holyclub.co.kr/v1/prayer_bgm_track/?page_size=1'
```

## 4) 확인 포인트
- 랜딩 페이지 hero 문구가 샘플 홈 콘텐츠로 바뀌는지
- 랜딩 페이지 최신 소식 영역에 샘플 공지가 뜨는지
- 앱 프로필 > 공지사항 목록/상세가 열리는지
- 앱 기도 화면에서 샘플 BGM이 목록/재생 대상으로 보이는지

## 5) 장애 우선순위
1. `home_content/current` 500 여부
2. 마이그레이션 누락 여부
3. 운영 API base URL 연결 여부
4. 샘플 데이터 생성 여부
5. 실기기에서 공지/BGM 노출 여부
