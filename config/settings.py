"""
[파일 경로] config/settings.py
[설명] .env 파일을 사용하여 보안 키를 관리하도록 수정되었습니다.
       불필요한 OCI Access Key 관련 설정을 제거했습니다.
"""

from pathlib import Path
import os
from dotenv import load_dotenv # 패키지 로드

# 1. .env 파일 활성화
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECRET_KEY 가져오기
SECRET_KEY = os.getenv('SECRET_KEY')

# 개발 모드 (배포 시에는 False로 변경 권장)
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
    'photo',      # 우리 앱
    'storages',   # [필수] OCI 연동 라이브러리
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# ==========================================
# 🎨 정적 파일 설정
# ==========================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# ==========================================
# ☁️ OCI Object Storage 설정 (Native SDK)
# ==========================================
AWS_STORAGE_BUCKET_NAME = 'school-media'
OCI_NAMESPACE = 'axypprkugw7b'
OCI_REGION = 'ap-chuncheon-1'

# [제거됨] OCI Access Key/Secret Key 관련 설정은 Native SDK 방식에서 필요 없습니다.
# 인증은 ~/.oci/config와 pem 키 파일을 통해 이루어집니다.

# Django 6.0 호환 스토리지 설정
STORAGES = {
    "default": {
        "BACKEND": "config.storage.OCIStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# 미디어 파일 URL
MEDIA_URL = f'https://objectstorage.{OCI_REGION}.oraclecloud.com/n/{OCI_NAMESPACE}/b/{AWS_STORAGE_BUCKET_NAME}/o/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'