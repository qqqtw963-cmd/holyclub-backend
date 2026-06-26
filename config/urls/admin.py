from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path
from django.utils.safestring import mark_safe

# admin.site.site_header = "페이지 상단 헤더 제목 변경(화면에 보이는 큰 어드민 제목)"
# admin.site.site_title = "브라우저 탭 제목 변경"
# admin.site.index_title = "메인페이지의 '사이트 관리' 제목 변경"

urlpatterns = [
    path("ckeditor/", include("ckeditor_uploader.urls")),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    path("", admin.site.urls),
]
admin.site.unregister(Group)
