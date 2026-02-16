"""
[파일 경로] photo/signals.py
[설명]
1. MediaPost가 저장되면 실행됩니다.
2. 업로드된 파일이 '이미지'인 경우:
   - 원본을 original_file에 저장
   - 카툰 필터를 적용하여 file에 저장
   - Gemini AI로 캡션 생성
3. .env 파일의 'GEMINI_API_KEY'를 사용하여 인증합니다.
"""

import os
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from .models import MediaPost
from .filters import apply_gemini_anime_filter
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# 로깅 설정
logger = logging.getLogger('django')


@receiver(pre_save, sender=MediaPost)
def apply_cartoon_before_save(sender, instance, **kwargs):
    """
    MediaPost 저장 전에 카툰 필터 적용
    원본은 original_file에 저장, 변환본은 file에 저장
    """
    # 1. 새로 업로드된 파일이 있고, 아직 처리되지 않은 경우만 실행
    if not instance.file:
        return

    # 이미 처리된 경우 (original_file이 있으면) 패스
    if instance.original_file:
        return

    # 2. 이미지 파일인지 확인 (확장자 검사)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic']
    ext = os.path.splitext(instance.file.name)[1].lower()

    if ext not in valid_extensions:
        logger.info(f"⏭️ [Cartoon Skip] 이미지가 아닌 파일입니다: {instance.title} ({ext})")
        return

    try:
        logger.info(f"🎨 [Cartoon Filter] 카툰 필터 적용 시작: {instance.title}")

        # 3. 원본 파일 읽기
        instance.file.open()
        original_data = instance.file.read()
        instance.file.close()

        # 4. 원본을 original_file에 저장
        original_name = f"original_{instance.file.name.split('/')[-1]}"
        instance.original_file.save(
            original_name,
            ContentFile(original_data),
            save=False  # 아직 DB에 저장하지 않음
        )
        logger.info(f"💾 [Original Saved] 원본 저장 완료: {original_name}")

        # 5. Gemini 2.5 Flash Image (Nano Banana)를 사용한 고품질 애니메이션 변환
        # Gemini가 실패하면 자동으로 Fal.ai로 폴백
        logger.info("🎨 [Anime Filter] AI 애니메이션 스타일로 변환 시작 (Gemini → Fal.ai 폴백)")
        anime_image = apply_gemini_anime_filter(original_data)

        # 6. 변환된 애니메이션 이미지를 file에 저장 (기존 파일 교체)
        anime_name = f"anime_{instance.file.name.split('/')[-1]}"
        anime_data = anime_image.read()

        # 기존 file 필드 내용을 애니메이션 스타일로 교체
        instance.file.save(
            anime_name,
            ContentFile(anime_data),
            save=False  # 아직 DB에 저장하지 않음
        )

        logger.info(f"✅ [Anime Applied] 애니메이션 스타일 적용 완료: {anime_name}")

    except Exception as e:
        logger.error(f"❌ [Cartoon Error] 카툰 필터 적용 중 오류: {str(e)}")
        # 오류 발생 시 원본 그대로 유지


@receiver(post_save, sender=MediaPost)
def generate_caption(sender, instance, created, **kwargs):
    """
    MediaPost 저장 후 AI 캡션 생성
    (카툰 필터가 적용된 이미지로 분석)
    """
    # 1. 이미 AI 설명이 있으면 패스
    if instance.ai_caption:
        return

    # 2. 파일이 없으면 패스
    if not instance.file:
        return

    # 3. 이미지 파일인지 확인
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic']
    ext = os.path.splitext(instance.file.name)[1].lower()

    if ext not in valid_extensions:
        logger.info(f"⏭️ [AI Skip] 이미지가 아닌 파일입니다: {instance.title} ({ext})")
        return

    try:
        logger.info(f"🤖 [AI Start] 이미지 분석 시작: {instance.title}")

        # 4. 구글 클라이언트 초기화
        api_key = os.getenv('GEMINI_API_KEY')

        if not api_key:
            logger.error("❌ .env 파일에서 'GEMINI_API_KEY'를 찾을 수 없습니다.")
            return

        genai.configure(api_key=api_key)

        # 5. 파일 읽기 (변환된 이미지 사용)
        instance.file.open()
        image_data = instance.file.read()
        pil_image = Image.open(BytesIO(image_data))

        # 6. 프롬프트 설정
        prompt = (
            "이 학교 활동 사진을 자세히 보고 설명해줘. "
            "초등학생이나 학부모에게 말하듯이 '따뜻하고 친절한 해요체'를 써줘. "
            "핵심 내용만 3문장 이내로 요약해줘."
        )

        # 7. Gemini 2.0 Flash 호출
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content([prompt, pil_image])

        # 8. 결과 저장
        if response.text:
            logger.info(f"✅ [AI Success] 분석 완료: {response.text[:30]}...")

            # DB에 저장
            instance.ai_caption = response.text
            instance.save(update_fields=['ai_caption'])

    except Exception as e:
        logger.error(f"❌ [AI Error] Gemini 호출 중 오류 발생: {str(e)}")
