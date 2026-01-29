"""
[파일 경로] update_site.py
[설명] 
변경된 Serveo 주소(8db0...)를 Django 설정에 적용합니다.
"""
import os
import django

# Django 환경 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

# 👇 [수정됨] 방금 터미널에 뜬 최신 주소!
TARGET_DOMAIN = 'f8a684c0bda4c60c-152-67-193-142.serveousercontent.com' 
TARGET_NAME = 'School Archive Test'

try:
    # ID가 1번인 사이트 정보를 가져와서 수정합니다.
    site = Site.objects.get(id=1)
    site.domain = TARGET_DOMAIN
    site.name = TARGET_NAME
    site.save()
    print(f"\n✅ [성공] Django 사이트 설정이 '{TARGET_DOMAIN}'으로 변경되었습니다.")
    
    # 구글 콘솔 등록용 주소 생성
    callback_url = f"https://{TARGET_DOMAIN}/accounts/google/login/callback/"
    
    print("\n" + "="*60)
    print("🚨 [필수 확인] 구글 클라우드 콘솔에 이 주소가 등록되어 있나요?")
    print("="*60)
    print(f"👉 {callback_url}")
    print("="*60 + "\n")

except Site.DoesNotExist:
    Site.objects.create(domain=TARGET_DOMAIN, name=TARGET_NAME)
    print(f"✅ [성공] 새 Site 정보를 생성했습니다: {TARGET_DOMAIN}")