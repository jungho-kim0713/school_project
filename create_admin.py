"""
관리자 계정 자동 생성 스크립트
사용법: python create_admin.py
"""

import os
import django

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# 관리자 계정 정보
USERNAME = 'admin'
EMAIL = 'admin@school.com'
PASSWORD = 'admin123'  # 원하는 비밀번호로 변경 가능

# 이미 존재하는지 확인
if User.objects.filter(username=USERNAME).exists():
    print(f"❌ '{USERNAME}' 계정이 이미 존재합니다.")
    print("기존 계정으로 로그인하세요!")
else:
    # 슈퍼유저 생성
    User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print("✅ 관리자 계정 생성 완료!")
    print(f"")
    print(f"📋 로그인 정보:")
    print(f"   사용자 이름: {USERNAME}")
    print(f"   비밀번호: {PASSWORD}")
    print(f"")
    print(f"🔗 관리자 페이지: http://localhost:8000/admin")
