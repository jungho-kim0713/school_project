import google.generativeai as genai
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import MediaPost
from PIL import Image
import io
import logging
import os # os 모듈 추가

# 시스템 로그 설정을 가져옵니다.
logger = logging.getLogger('django')

# ==========================================
# 🔑 Gemini API 키 설정 (환경변수 사용)
# ==========================================
# .env 파일에서 키를 가져옵니다.
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 키가 제대로 로드되었는지 확인
if not GEMINI_API_KEY:
    logger.error("🚨 [AI 설정 오류] .env 파일에 GEMINI_API_KEY가 없습니다!")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 🤖 AI 이미지 분석 시그널
# ==========================================
@receiver(post_save, sender=MediaPost)
def analyze_image_with_gemini(sender, instance, created, **kwargs):
    if not created or instance.ai_caption:
        return

    # 키가 없는 경우 중단
    if not GEMINI_API_KEY:
        return

    try:
        logger.info(f"🤖 [AI Start] 분석 시작: {instance.title}")
        
        with instance.file.open('rb') as f:
            image_bytes = f.read()
            if len(image_bytes) == 0:
                logger.warning("⚠️ [AI Warning] 이미지 파일 크기가 0입니다.")
                return
            image = Image.open(io.BytesIO(image_bytes))

        # gemini-3-flash-preview 사용
        model = genai.GenerativeModel('gemini-3-flash-preview')
        prompt = (
            "이 사진은 학교 활동을 기록한 사진이야. "
            "이 사진의 상황을 학생들에게 설명하듯이, 따뜻하고 긍정적인 말투(해요체)로 2~3문장 요약해줘."
        )
        
        response = model.generate_content([prompt, image])
        ai_result = response.text
        
        logger.info(f"✅ [AI Success] 분석 완료: {ai_result[:30]}...")

        instance.ai_caption = ai_result
        instance.save(update_fields=['ai_caption'])

    except Exception as e:
        logger.error(f"❌ [AI Error] 분석 중 오류 발생: {e}")

# ==========================================
# 🗑️ 파일 삭제 자동화 시그널
# ==========================================
@receiver(post_delete, sender=MediaPost)
def cleanup_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        try:
            logger.info(f"🗑️ [File Delete] OCI 파일 삭제 시도: {instance.file.name}")
            instance.file.delete(save=False) 
            logger.info(f"✅ [File Delete] OCI 파일 삭제 완료")
        except Exception as e:
            logger.error(f"⚠️ [File Delete Error] 삭제 실패: {e}")