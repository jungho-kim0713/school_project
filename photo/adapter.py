"""
[파일 경로] photo/adapter.py
[설명] 
1. CustomAccountAdapter: 일반 계정 관리 (기존 유지)
2. CustomSocialAccountAdapter: 구글 로그인 시 회원가입을 가로채서 비활성화 (신규 추가)
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
import logging

logger = logging.getLogger('django')

# 1. 일반 계정 어댑터 (기존 로직)
class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user

    def respond_user_inactive(self, request, user):
        # 비활성화 유저 접속 시 에러 메시지 표시
        logger.warning(f"🔒 [Login Blocked] 승인 대기 계정 접속 시도: {user.email}")
        messages.error(request, "🔒 회원가입 승인 대기 중입니다. 관리자 승인 후 이용 가능합니다.")
        return super().respond_user_inactive(request, user)


# 2. [신규] 소셜 로그인(구글) 전용 어댑터
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        구글 로그인으로 회원이 생성될 때 호출됩니다.
        """
        logger.info("🛑 [Social Adapter] 구글 회원가입 감지됨!")
        
        # 부모 클래스의 save_user를 호출하여 유저 객체 생성
        user = super().save_user(request, sociallogin, form)
        
        # 관리자가 아니면 강제 비활성화
        if not user.is_superuser:
            logger.info(f"🛑 [Social Adapter] {user.email} 계정을 비활성화(False) 처리합니다.")
            user.is_active = False
            user.save()  # DB에 즉시 반영
        else:
            logger.info("✅ [Social Adapter] 관리자 계정이므로 통과합니다.")
            
        return user