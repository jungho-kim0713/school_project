"""
[파일 경로] config/settings.py
[설명] 
1. 서브 도메인 'archive.sdjgh-ai.kr'을 정식 호스트로 등록했습니다.
2. CSRF 신뢰 도메인에도 해당 서브 도메인을 추가했습니다.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# 1. .env 파일 활성화
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

# [배포 설정] 운영 모드 적용 (보안 및 성능 최적화)
DEBUG = False

# [수정됨] 서브 도메인 허용
ALLOWED_HOSTS = ['*', 'archive.sdjgh-ai.kr']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 앱 순서 유지
    'photo',      
    'storages',   

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'config.urls'

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
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

AWS_STORAGE_BUCKET_NAME = 'school-media'
OCI_NAMESPACE = 'axypprkugw7b'
OCI_REGION = 'ap-chuncheon-1'

if DEBUG:
    # [로컬 개발] 내 컴퓨터의 'media' 폴더 사용
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    # [운영 서버] OCI Object Storage 사용
    STORAGES = {
        "default": {"BACKEND": "config.storage.OCIStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    MEDIA_URL = f'https://objectstorage.{OCI_REGION}.oraclecloud.com/n/{OCI_NAMESPACE}/b/{AWS_STORAGE_BUCKET_NAME}/o/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

ACCOUNT_LOGIN_METHODS = {'email'} 
ACCOUNT_SIGNUP_FIELDS = ['email']
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_SESSION_REMEMBER = True

ACCOUNT_ADAPTER = 'photo.adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'photo.adapter.CustomSocialAccountAdapter'

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

# 보안 설정 (HTTPS)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

# [수정됨] 서브 도메인 추가
CSRF_TRUSTED_ORIGINS = [
    'https://*.serveousercontent.com',
    'https://*.serveo.net',
    'https://archive.sdjgh-ai.kr', # 우리의 진짜 서비스 주소
    'https://*.sdjgh-ai.kr',       # [Cloudflare] 모든 서브 도메인 신뢰
]