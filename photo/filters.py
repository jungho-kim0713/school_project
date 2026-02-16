"""
[파일 경로] photo/filters.py
[설명]
이미지를 애니메이션/웹툰 스타일로 변환하는 필터 함수들
- Gemini Anime Filter: Google Gemini를 사용한 깔끔한 애니메이션 스타일 변환
- Fal.ai SeeDream-4: 고품질 AI 웹툰 변환 (유료, 선택적)
"""

import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import os
import base64
import google.generativeai as genai

logger = logging.getLogger('django')


def apply_cartoon_filter(image_data, strength='strong'):
    """
    이미지에 카툰 필터를 적용합니다.

    Parameters:
    -----------
    image_data : bytes
        원본 이미지 데이터 (PIL Image 또는 bytes)
    strength : str
        필터 강도 ('weak', 'medium', 'strong')

    Returns:
    --------
    BytesIO
        카툰 필터가 적용된 이미지 (BytesIO 형태)
    """
    try:
        logger.info(f"🎨 [Cartoon Filter] 필터 적용 시작 (강도: {strength})")

        # 1. PIL Image -> numpy array로 변환
        if isinstance(image_data, bytes):
            pil_image = Image.open(BytesIO(image_data))
        else:
            pil_image = image_data

        # RGB로 변환 (RGBA 등 다른 모드 대응)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # numpy array로 변환 (OpenCV는 BGR 사용)
        img_array = np.array(pil_image)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        # 강도에 따른 파라미터 설정
        if strength == 'strong':
            # 강함: 확실한 만화 효과
            num_bilateral = 9  # 양방향 필터 반복 횟수
            color_levels = 8   # 색상 단계 (낮을수록 만화스러움)
            edge_threshold1 = 50
            edge_threshold2 = 150
        elif strength == 'medium':
            # 중간: 자연스러운 균형
            num_bilateral = 7
            color_levels = 12
            edge_threshold1 = 100
            edge_threshold2 = 200
        else:  # weak
            # 약함: 은은한 효과
            num_bilateral = 5
            color_levels = 16
            edge_threshold1 = 150
            edge_threshold2 = 250

        # 2. 색상 단순화 (만화처럼)
        # 양방향 필터를 여러 번 적용하여 부드럽게 하면서 경계는 유지
        color = img_bgr
        for _ in range(num_bilateral):
            color = cv2.bilateralFilter(color, d=9, sigmaColor=9, sigmaSpace=7)

        # 색상 레벨 감소 (양자화)
        # 256단계 색상을 color_levels 단계로 줄임
        div = 256 // color_levels
        color = color // div * div

        # 3. 경계선 추출 (만화의 윤곽선)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)  # 노이즈 제거

        # Canny Edge Detection으로 경계선 찾기
        edges = cv2.Canny(gray, edge_threshold1, edge_threshold2)

        # 경계선 두껍게 만들기 (만화 윤곽선처럼)
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        # 경계선을 3채널로 변환
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # 4. 단순화된 색상 + 경계선 합성
        # 경계선이 있는 곳은 검은색, 없는 곳은 단순화된 색상
        cartoon = cv2.bitwise_and(color, cv2.bitwise_not(edges))

        # 5. BGR -> RGB로 변환 후 PIL Image로
        cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
        cartoon_pil = Image.fromarray(cartoon_rgb)

        # 6. BytesIO로 변환하여 반환
        output = BytesIO()
        cartoon_pil.save(output, format='JPEG', quality=95)
        output.seek(0)

        logger.info("✅ [Cartoon Filter] 필터 적용 완료")
        return output

    except Exception as e:
        logger.error(f"❌ [Cartoon Filter] 필터 적용 중 오류: {str(e)}")
        # 오류 발생 시 원본 반환
        if isinstance(image_data, bytes):
            return BytesIO(image_data)
        else:
            output = BytesIO()
            image_data.save(output, format='JPEG', quality=95)
            output.seek(0)
            return output


def apply_gemini_anime_filter(image_data):
    """
    Google Gemini 2.5 Flash Image (Nano Banana)를 사용하여
    이미지를 깔끔한 애니메이션 스타일로 변환

    Parameters:
    -----------
    image_data : bytes
        원본 이미지 데이터

    Returns:
    --------
    BytesIO
        애니메이션 스타일로 변환된 이미지
    """
    try:
        logger.info("🎨 [Gemini Nano Banana] AI 웹툰 변환 시작")

        # 1. API 키 확인
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("❌ GEMINI_API_KEY가 없습니다.")
            # Fal.ai로 폴백
            return apply_seedream_filter(image_data)

        genai.configure(api_key=api_key)

        # 2. 원본 이미지 로드
        if isinstance(image_data, bytes):
            pil_image = Image.open(BytesIO(image_data))
        else:
            pil_image = image_data

        # 이미지를 RGB로 변환
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # 3. 프롬프트 설정
        prompt = (
            "Transform this image into a clean anime/webtoon style. "
            "Apply these characteristics: "
            "1. Clean line art with sharp, defined edges "
            "2. Cel shading for depth and dimension "
            "3. Bright and vibrant colors "
            "Keep the original composition and content, only change the artistic style to anime/webtoon."
        )

        # 4. Gemini 2.5 Flash Image 모델 호출
        try:
            # 이미지 편집 기능 사용 (Nano Banana)
            model = genai.GenerativeModel('gemini-2.5-flash')

            response = model.generate_content([
                prompt,
                pil_image
            ],
            generation_config={
                'response_modalities': ['image']  # 이미지 출력 요청
            })

            # 5. 응답에서 이미지 추출
            if hasattr(response, 'images') and response.images:
                # Gemini가 이미지를 반환한 경우
                output_image = response.images[0]
                output = BytesIO()
                output_image.save(output, format='JPEG', quality=95)
                output.seek(0)

                logger.info("✅ [Gemini Nano Banana] 웹툰 변환 완료")
                return output
            else:
                # 이미지 반환 실패 시 Fal.ai로 폴백
                logger.warning("⚠️ [Gemini] 이미지 생성 실패. Fal.ai로 전환")
                return apply_seedream_filter(image_data)

        except Exception as gemini_error:
            logger.error(f"❌ [Gemini] 모델 호출 실패: {str(gemini_error)}")
            logger.info("🔄 Fal.ai로 폴백")
            return apply_seedream_filter(image_data)

    except Exception as e:
        logger.error(f"❌ [Gemini Anime] 오류 발생: {str(e)}")
        # 최종 폴백: Fal.ai
        return apply_seedream_filter(image_data)


def apply_face_blur_and_cartoon(image_data, blur_strength=0.3):
    """
    얼굴 감지 후 얼굴 부분만 블러 처리하고 전체에 카툰 필터 적용
    (향후 고급 기능용 - 현재는 사용 안 함)

    Parameters:
    -----------
    image_data : bytes
        원본 이미지 데이터
    blur_strength : float
        블러 강도 (0.0 ~ 1.0)

    Returns:
    --------
    BytesIO
        처리된 이미지
    """
    # TODO: Haar Cascade 또는 dlib으로 얼굴 검출 후 선택적 블러
    # 현재는 전체 카툰 필터만 사용
    return apply_cartoon_filter(image_data, strength='strong')


def apply_seedream_filter(image_data, prompt="transform into Korean webtoon style"):
    """
    Fal.ai SeeDream-4 모델을 사용한 고품질 AI 웹툰 변환

    Parameters:
    -----------
    image_data : bytes
        원본 이미지 데이터
    prompt : str
        변환 프롬프트 (기본: 한국 웹툰 스타일)

    Returns:
    --------
    BytesIO
        AI 변환된 웹툰 스타일 이미지
    """
    try:
        import fal_client

        logger.info(f"🎨 [SeeDream] AI 웹툰 변환 시작")

        # 1. API 키 확인
        api_key = os.getenv('FAL_API_KEY')
        if not api_key or api_key == '여기에_Fal.ai_API_키_입력':
            logger.warning("⚠️ [SeeDream] FAL_API_KEY가 설정되지 않음. OpenCV 필터로 대체")
            return apply_cartoon_filter(image_data, strength='strong')

        # 2. 이미지를 base64로 인코딩
        if isinstance(image_data, bytes):
            pil_image = Image.open(BytesIO(image_data))
        else:
            pil_image = image_data

        # 임시 파일로 저장 (Fal.ai는 URL 또는 base64 필요)
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        image_url = f"data:image/png;base64,{img_base64}"

        # 3. Fal.ai API 호출
        os.environ['FAL_KEY'] = api_key

        result = fal_client.subscribe(
            "fal-ai/seedream-4-high-res",
            arguments={
                "image_url": image_url,
                "prompt": prompt,
                "num_inference_steps": 28,  # 품질 (높을수록 좋지만 느림)
                "guidance_scale": 7.5,
            }
        )

        # 4. 결과 이미지 다운로드
        if result and 'images' in result and len(result['images']) > 0:
            import requests
            output_url = result['images'][0]['url']
            response = requests.get(output_url)

            if response.status_code == 200:
                logger.info("✅ [SeeDream] AI 변환 완료")
                return BytesIO(response.content)
            else:
                logger.error(f"❌ [SeeDream] 이미지 다운로드 실패: {response.status_code}")
                return apply_cartoon_filter(image_data, strength='strong')
        else:
            logger.error("❌ [SeeDream] 결과 없음")
            return apply_cartoon_filter(image_data, strength='strong')

    except Exception as e:
        logger.error(f"❌ [SeeDream] 오류 발생: {str(e)}")
        logger.info("🔄 [SeeDream] OpenCV 필터로 대체")
        return apply_cartoon_filter(image_data, strength='strong')
