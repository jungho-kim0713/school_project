"""
[파일 경로] config/urls.py
[설명] allauth 경로를 추가하여 로그인 페이지 404 에러를 해결했습니다.
"""
from django.contrib import admin
from django.urls import path, include  # include 모듈 필수!
from django.views.generic import RedirectView # 추가
from django.conf import settings
from django.conf.urls.static import static
from photo import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # [핵심] 로그인/로그아웃 경로 연결 (이게 없어서 그동안 404가 떴던 겁니다)
    # [핵심] 로그인/로그아웃 경로 연결
    path('accounts/', include('allauth.urls')),
    
    # [편의성] /login 접속 시 /accounts/login/으로 자동 이동
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    
    # [작성 기능]
    path('media/create/', views.media_create, name='media_create'),
    path('text/create/', views.text_create, name='text_create'),
    path('code/create/', views.code_create, name='code_create'),
    
    path('', views.index, name='index'),
]

# 미디어 파일(사진)과 정적 파일(CSS, JS)을 위한 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # [추가] 정적 파일 서빙