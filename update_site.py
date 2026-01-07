"""
[파일 경로] update_site.py
[설명] Serveo가 만들어준 새 주소를 Django와 구글 로그인 설정에 적용합니다.
"""
import os
import django

# Django 환경 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

# 👇 [수정] 여기에 serveo 주소를 붙여넣으세요! (https:// 빼고 도메인만)
# 예: TARGET_DOMAIN = 'myschool.serveo.net'
TARGET_DOMAIN = 'd16481a48f9c6c54-152-67-193-142.serveousercontent.com' 
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
    print("🚨 [필수] 구글 클라우드 콘솔에 아래 주소를 등록하세요!")
    print("="*60)
    print(f"\n👉 {callback_url}\n")
    print("="*60)
    print("1. 위 주소(https 포함)를 복사하세요.")
    print("2. 구글 클라우드 콘솔 > 사용자 인증 정보 > 승인된 리디렉션 URI 목록")
    print("3. 기존 주소를 지우고 위 주소를 새로 등록하세요.")
    print("4. 등록 후 브라우저에서 https://{TARGET_DOMAIN} 으로 접속하세요.")
    print("="*60 + "\n")

except Site.DoesNotExist:
    Site.objects.create(domain=TARGET_DOMAIN, name=TARGET_NAME)
    print(f"✅ [성공] 새 Site 정보를 생성했습니다: {TARGET_DOMAIN}")