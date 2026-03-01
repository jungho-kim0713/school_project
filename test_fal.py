import os
import fal_client
from dotenv import load_dotenv

load_dotenv('c:/jungho_webhome/school_cloud/.env')

api_key = os.getenv('FAL_API_KEY')
if api_key:
    os.environ['FAL_KEY'] = api_key

sample_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/320px-Cat03.jpg"

prompt = (
    "Modern webtoon art style, high-quality digital 2D illustration, "
    "sharp and clean line art, professional cel shading, "
    "flat colors with vibrant and saturated tones. "
    "No sketch lines, no screentones, no halftone patterns."
)

candidates = [
    # IllustriousXL - 일러스트/애니메이션 특화 모델
    ("fal-ai/illustrious-xl/image-to-image", {
        "prompt": prompt,
        "image_url": sample_image_url,
        "strength": 0.7
    }),
    # fast-sdxl 애니메이션 i2i
    ("fal-ai/fast-sdxl/image-to-image", {
        "prompt": prompt,
        "image_url": sample_image_url,
        "strength": 0.7
    }),
    # anime-specific 다른 후보
    ("fal-ai/aura-sr", {
        "image_url": sample_image_url,
    }),
]

for model_id, arguments in candidates:
    print(f"▶️  Testing: {model_id}")
    try:
        handler = fal_client.submit(model_id, arguments=arguments)
        result = handler.get()
        if 'images' in result and result['images']:
            print(f"  ✅ 성공! URL: {result['images'][0].get('url', '?')[:80]}...")
        elif 'image' in result:
            print(f"  ✅ 성공! URL: {result['image'].get('url', '?')[:80]}...")
        else:
            print(f"  ⚠️  응답 왔지만 이미지 없음: {str(result)[:100]}")
    except Exception as e:
        print(f"  ❌ 실패: {str(e)[:120]}")
    print()
