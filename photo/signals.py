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
from .filters import apply_webtoon_filter
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# 로깅 설정
logger = logging.getLogger('django')


@receiver(pre_save, sender=MediaPost)
def apply_cartoon_before_save(sender, instance, **kwargs):
    """
    MediaPost 저장 전에 웹툰 스타일 적용 (선택적)
    원본은 original_file에 저장, 변환본은 file에 저장
    """
    # 1. 새로 업로드된 파일이 있고, 아직 처리되지 않은 경우만 실행
    if not instance.file:
        return

    # 이미 처리된 경우 (original_file이 있으면) 패스
    if instance.original_file:
        return

    # 2. 체크박스가 해제되어 있으면 변환을 수행하지 않고 그냥 종료 (원본으로 저장됨)
    if not instance.apply_webtoon_filter:
        logger.info(f"⏭️ [Webtoon Skip] 사용자가 변환을 선택하지 않았습니다: {instance.title}")
        return

    # 3. 이미지 파일인지 확인 (확장자 검사)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.heic']
    ext = os.path.splitext(instance.file.name)[1].lower()

    if ext not in valid_extensions:
        logger.info(f"⏭️ [Webtoon Skip] 이미지가 아닌 파일입니다: {instance.title} ({ext})")
        return

    try:
        logger.info(f"🎨 [Webtoon Filter] 웹툰 필터 적용 시작: {instance.title}")

        # 4. 원본 파일 읽기
        instance.file.open()
        original_data = instance.file.read()
        instance.file.close()

        # 5. 원본을 original_file에 별도 저장
        original_name = f"original_{instance.file.name.split('/')[-1]}"
        instance.original_file.save(
            original_name,
            ContentFile(original_data),
            save=False  # 아직 DB에 저장하지 않음
        )
        logger.info(f"💾 [Original Saved] 원본 보존 완료: {original_name}")

        # 6. 원본 이미지 데이터를 처리할 수 있도록 전달
        logger.info("🎨 [Webtoon Filter] Fal AI로 웹툰 스타일 변환 진행")
        webtoon_image = apply_webtoon_filter(original_data)

        # 7. 변환된 이미지를 file 필드에 저장 (기존 파일 교체)
        webtoon_name = f"webtoon_{instance.file.name.split('/')[-1]}"
        webtoon_data = webtoon_image.read()

        instance.file.save(
            webtoon_name,
            ContentFile(webtoon_data),
            save=False  # 아직 DB에 저장하지 않음
        )

        logger.info(f"✅ [Webtoon Applied] 웹툰 필터 적용 완료: {webtoon_name}")

    except Exception as e:
        logger.error(f"❌ [Webtoon Error] 웹툰 필터 적용 중 오류 발생: {str(e)}")
        # 오류 발생 시 변환 포기하고 원본으로 저장됨 (이전 필드 값 유지)


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
