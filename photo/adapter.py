"""
[파일 경로] photo/adapter.py
[설명] 
1. 계정 비활성화 시 보여줄 템플릿을 'waiting_approval.html'로 변경했습니다.
2. 파일명 충돌을 원천 차단하여 디자인 적용을 보장합니다.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import render
import logging

logger = logging.getLogger('django')

# 1. 일반 계정 어댑터
class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user

    def respond_user_inactive(self, request, user):
        logger.warning(f"🔒 [Login Blocked] 승인 대기 계정 접속 시도: {user.email}")
        
        # [핵심 변경] 이름이 겹치지 않는 우리만의 파일을 렌더링합니다.
        return render(request, 'account/waiting_approval.html')


# 2. 소셜 로그인(구글) 전용 어댑터
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        logger.info("🛑 [Social Adapter] 구글 회원가입 감지됨!")
        user = super().save_user(request, sociallogin, form)
        
        if not user.is_superuser:
            logger.info(f"🛑 [Social Adapter] {user.email} 계정을 비활성화(False) 처리합니다.")
            user.is_active = False
            user.save()
        else:
            logger.info("✅ [Social Adapter] 관리자 계정이므로 통과합니다.")
            
        return user