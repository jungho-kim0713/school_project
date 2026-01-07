"""
[파일 경로] photo/adapter.py
[설명] 
django-allauth의 기본 동작을 가로채서(Override),
회원가입 직후 사용자를 '비활성화(is_active=False)' 상태로 만듭니다.
관리자가 승인해주어야 로그인이 가능해집니다.
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages
from django.shortcuts import resolve_url

class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        """
        회원가입 시 사용자 정보를 저장하는 순간 호출됩니다.
        """
        # 1. 부모 클래스의 save_user를 호출하여 유저 객체를 일단 만듭니다.
        user = super().save_user(request, sociallogin, form)
        
        # 2. [핵심] 유저를 강제로 비활성화합니다.
        # 관리자(is_superuser)가 아니면 모두 비활성화
        if not user.is_superuser:
            user.is_active = False
            user.save()
        
        return user

    def respond_user_inactive(self, request, user):
        """
        비활성화된 유저가 로그인을 시도했을 때 호출됩니다.
        """
        # 사용자에게 안내 메시지를 띄웁니다.
        messages.error(request, "🔒 회원가입 승인 대기 중입니다. 관리자 승인 후 이용 가능합니다.")
        return super().respond_user_inactive(request, user)