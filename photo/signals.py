"""
[파일 경로] photo/signals.py
[설명] 
1. MediaPost가 저장되면 실행됩니다.
2. 업로드된 파일이 '이미지'인 경우에만 Gemini AI (신형 SDK)를 호출합니다.
3. .env 파일의 'GEMINI_API_KEY'를 사용하여 인증합니다. (수정됨)
"""

import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MediaPost
from google import genai
from PIL import Image
from io import BytesIO

# 로깅 설정
logger = logging.getLogger('django')

@receiver(post_save, sender=MediaPost)
def generate_caption(sender, instance, created, **kwargs):
    """
    MediaPost 저장 시 호출되는 AI 분석 함수
    """
    # 1. 파일이 없거나, 이미 AI 설명이 있거나, 공개되지 않은 글이면 패스
    if not instance.file or instance.ai_caption:
        return

    # 2. 이미지 파일인지 확인 (확장자 검사)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic']
    ext = os.path.splitext(instance.file.name)[1].lower()
    
    if ext not in valid_extensions:
        logger.info(f"⏭️ [AI Skip] 이미지가 아닌 파일입니다: {instance.title} ({ext})")
        return

    try:
        logger.info(f"🤖 [AI Start] 이미지 분석 시작: {instance.title}")

        # 3. 구글 클라이언트 초기화 (환경 변수 이름 수정: GEMINI_API_KEY)
        api_key = os.getenv('GEMINI_API_KEY') # <--- 여기를 수정했습니다!
        
        if not api_key:
            logger.error("❌ .env 파일에서 'GEMINI_API_KEY'를 찾을 수 없습니다.")
            return

        client = genai.Client(api_key=api_key)

        # 4. 파일 읽기 (OCI 스토리지 -> 메모리)
        instance.file.open()
        image_data = instance.file.read()
        pil_image = Image.open(BytesIO(image_data))

        # 5. 프롬프트 설정
        prompt = (
            "이 학교 활동 사진을 자세히 보고 설명해줘. "
            "초등학생이나 학부모에게 말하듯이 '따뜻하고 친절한 해요체'를 써줘. "
            "핵심 내용만 3문장 이내로 요약해줘."
        )

        # 6. Gemini 2.0 Flash 호출
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, pil_image]
        )

        # 7. 결과 저장
        if response.text:
            logger.info(f"✅ [AI Success] 분석 완료: {response.text[:30]}...")
            
            # DB에 저장
            instance.ai_caption = response.text
            instance.save(update_fields=['ai_caption'])
            
    except Exception as e:
        logger.error(f"❌ [AI Error] Gemini 호출 중 오류 발생: {str(e)}")