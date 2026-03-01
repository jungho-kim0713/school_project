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


