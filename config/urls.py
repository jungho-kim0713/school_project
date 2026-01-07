"""
[파일 경로] config/urls.py
[설명] 
1. allauth URL을 포함시켜 /accounts/login, /accounts/google/login 등을 활성화합니다.
2. photo 앱의 URL도 그대로 유지합니다.
"""
from django.contrib import admin
from django.urls import path, include  # include 모듈 필수!
from django.conf import settings
from django.conf.urls.static import static
from photo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # [핵심] 이 줄이 있어야 로그인/로그아웃/회원가입 기능이 작동합니다!
    path('accounts/', include('allauth.urls')),
    
    path('', views.index, name='index'),
]

# 미디어 파일(사진)을 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)