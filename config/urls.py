from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from photo import views  # photo 앱의 views 가져오기

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  # 메인 주소 접속 시 index 뷰 실행
]

# 미디어 파일(사진)을 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)