"""
[파일 경로] config/urls.py
[설명] allauth 경로를 추가하여 로그인 페이지 404 에러를 해결했습니다.
"""
from django.contrib import admin
from django.urls import path, include  # include 모듈 필수!
from django.conf import settings
from django.conf.urls.static import static
from photo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # [핵심] 로그인/로그아웃 경로 연결 (이게 없어서 그동안 404가 떴던 겁니다)
    path('accounts/', include('allauth.urls')),
    
    path('', views.index, name='index'),
]

# 미디어 파일(사진)을 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)