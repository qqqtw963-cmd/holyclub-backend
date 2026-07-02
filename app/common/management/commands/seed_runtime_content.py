from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from app.home_content.models import HomeContent
from app.notification.models import Notification
from app.prayer_bgm_track.models import PrayerBgmTrack


class Command(BaseCommand):
    help = "홈 콘텐츠/공지사항/기도 BGM 스모크 테스트용 샘플 데이터를 생성하거나 갱신합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--bgm-file",
            type=str,
            required=False,
            help="기도 BGM 샘플로 등록할 오디오 파일 절대경로 또는 상대경로",
        )
        parser.add_argument(
            "--bgm-title",
            type=str,
            required=False,
            default="기도 배경음 샘플",
            help="기도 BGM 샘플 제목",
        )
        parser.add_argument(
            "--skip-bgm",
            action="store_true",
            help="기도 BGM 샘플 생성을 건너뜁니다.",
        )

    def handle(self, *args, **options):
        home_content = self._seed_home_content()
        notification = self._seed_notification()

        self.stdout.write(self.style.SUCCESS(f"home_content ready: id={home_content.id}"))
        self.stdout.write(self.style.SUCCESS(f"notification ready: id={notification.id}"))

        if options["skip_bgm"]:
            self.stdout.write(self.style.WARNING("BGM sample skipped by --skip-bgm"))
            return

        bgm_file = options.get("bgm_file")
        if not bgm_file:
            self.stdout.write(
                self.style.WARNING(
                    "BGM sample not created. Re-run with --bgm-file /absolute/path/to/sample.m4a or use --skip-bgm."
                )
            )
            return

        track = self._seed_bgm_track(bgm_file=bgm_file, title=options["bgm_title"])
        self.stdout.write(self.style.SUCCESS(f"prayer_bgm_track ready: id={track.id}"))

    def _seed_home_content(self):
        HomeContent.objects.filter(is_active=True).update(is_active=False)
        home_content, _ = HomeContent.objects.update_or_create(
            main_title="신앙이 자꾸 끊기는 이유는 흩어져 있기 때문입니다.",
            defaults={
                "eyebrow": "하나님과 더 가까워지는 거룩한 습관",
                "sub_title": "HolyClub은 말씀, 기도, 묵상, 기록을 하나의 리듬으로 묶어 신앙이 습관이 되도록 돕습니다.",
                "highlight_text": "흩어진 신앙을 다시 하나로",
                "cta_text": "출시 소식 보기",
                "cta_link": "https://holyclub.co.kr/#start",
                "is_active": True,
            },
        )
        return home_content

    def _seed_notification(self):
        notification, _ = Notification.objects.update_or_create(
            title="HolyClub 테스트 공지",
            defaults={
                "content": "<p>이 공지는 홈 랜딩/앱 공지 연동 스모크 테스트용 샘플입니다.</p>",
            },
        )
        return notification

    def _seed_bgm_track(self, bgm_file: str, title: str):
        source_path = Path(bgm_file).expanduser()
        if not source_path.exists() or not source_path.is_file():
            raise CommandError(f"BGM file not found: {source_path}")

        existing_track = PrayerBgmTrack.objects.filter(title=title).first()
        if existing_track is None:
            existing_track = PrayerBgmTrack(title=title, duration_seconds=1, is_active=True)
        else:
            existing_track.is_active = True

        with source_path.open("rb") as fp:
            existing_track.audio_file.save(source_path.name, File(fp), save=False)

        existing_track.save()
        PrayerBgmTrack.objects.exclude(pk=existing_track.pk).update(is_active=False)
        return existing_track
