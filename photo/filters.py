"""
[파일 경로] photo/filters.py
[설명]
이미지를 AI 한국 웹툰 스타일로 변환하는 필터 함수
- Gemini Webtoon Filter: Google Gemini를 사용한 고품질 웹툰 스타일 변환
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import os
import base64
import json
import requests
import fal_client

logger = logging.getLogger('django')


def apply_webtoon_filter(image_data):
    """
    Google Gemini를 사용하여 이미지를 깔끔한 한국 웹툰/만화 스타일로 변환

    Parameters:
    -----------
    image_data : bytes
        원본 이미지 데이터

    Returns:
    --------
    BytesIO
        웹툰 스타일로 변환된 이미지
    """
    try:
        logger.info("🎨 [Fal Webtoon] AI 웹툰 변환 시작")

        # 1. API 키 확인 및 설정
        api_key = os.getenv('FAL_API_KEY')
        if not api_key:
            logger.error("❌ FAL_API_KEY가 없습니다.")
            return get_original_image_bytes(image_data)
        
        # fal_client 내부적으로 FAL_KEY 환경변수를 사용
        os.environ['FAL_KEY'] = api_key

        # 2. 원본 이미지 로드 및 Base64 인코딩 준비
        if isinstance(image_data, bytes):
            pil_image = Image.open(BytesIO(image_data))
        else:
            pil_image = image_data

        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # 3. 프롬프트 설정
        prompt = (
            "Modern webtoon art style, high-quality digital 2D illustration, "
            "sharp and clean line art, professional cel shading, "
            "flat colors with vibrant and saturated tones. "
            "Minimalist background, crisp edges, cinematic lighting. "
            "No sketch lines, no screentones, no halftone patterns."
        )

        # 4. Fal AI API 호출 (Seedream v4 Edit - 원본 이미지 편집 전용 모델)
        try:
            handler = fal_client.submit(
                "fal-ai/bytedance/seedream/v4/edit",
                arguments={
                    "prompt": prompt,
                    "image_urls": [f"data:image/jpeg;base64,{img_b64_str}"]
                }
            )
            
            result = handler.get()
            
            if 'images' in result and len(result['images']) > 0:
                img_url = result['images'][0].get('url')
                if img_url:
                    # 결과 이미지 다운로드
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        output = BytesIO(img_response.content)
                        logger.info("✅ [Fal Webtoon] 웹툰 변환 완료 (Seedream v4.5)")
                        return output
                    else:
                        logger.error(f"❌ [Fal] 이미지 다운로드 실패: {img_response.status_code}")
                        return get_original_image_bytes(image_data)
                else:
                    logger.warning("⚠️ [Fal] 응답 이미지 URL을 찾을 수 없습니다.")
                    return get_original_image_bytes(image_data)
            else:
                logger.warning(f"⚠️ [Fal] 올바른 이미지가 반환되지 않았습니다: {json.dumps(result)[:200]}")
                return get_original_image_bytes(image_data)

        except Exception as fal_error:
            logger.error(f"❌ [Fal] 요청 오류 발생: {str(fal_error)}")
            return get_original_image_bytes(image_data)

    except Exception as e:
        logger.error(f"❌ [Fal Webtoon] 전체 오류 발생: {str(e)}")
        return get_original_image_bytes(image_data)

def get_original_image_bytes(image_data):
    """오류 발생 시 원본 이미지를 BytesIO로 반환하는 헬퍼 함수"""
    if isinstance(image_data, bytes):
        return BytesIO(image_data)
    else:
        output = BytesIO()
        image_data.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output

