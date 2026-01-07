"""
[파일 경로] config/settings.py
[설명] 
1. 누락되었던 allauth(소셜 로그인) 앱들을 다시 등록했습니다.
2. 템플릿 경로를 올바르게 설정하여 CSS 문제를 해결했습니다.
3. 구글 로그인 시 회원가입 단계를 건너뛰도록 설정했습니다.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 1. .env 파일 활성화
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

# 개발 모드
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # [핵심] 소셜 로그인 관련 앱 (다시 추가함)
    'django.contrib.sites',  # 필수
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', # 구글 로그인

    'photo',      # 우리 앱
    'storages',   # OCI 연동
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # [필수] allauth 계정 미들웨어
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'config.urls'

# [핵심] 템플릿 설정 (CSS 문제 해결용)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # 우리가 만든 templates 폴더를 1순위로!
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # [필수] allauth가 정상 작동하려면 꼭 있어야 함
                'django.template.context_processors.request', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# OCI Object Storage 설정
AWS_STORAGE_BUCKET_NAME = 'school-media'
OCI_NAMESPACE = 'axypprkugw7b'
OCI_REGION = 'ap-chuncheon-1'

STORAGES = {
    "default": {"BACKEND": "config.storage.OCIStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

MEDIA_URL = f'https://objectstorage.{OCI_REGION}.oraclecloud.com/n/{OCI_NAMESPACE}/b/{AWS_STORAGE_BUCKET_NAME}/o/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 🔐 인증 및 소셜 로그인 설정 (여기 중요!)
# ==========================================
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_ADAPTER = 'photo.adapter.CustomAccountAdapter'

# [핵심] 귀찮은 회원가입 폼 건너뛰기
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_SECRET_KEY'),
            'key': ''
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    }
}