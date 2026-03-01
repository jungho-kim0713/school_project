import os
import requests
import json
import base64
from dotenv import load_dotenv

load_dotenv('c:/jungho_webhome/school_cloud/.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def test_openai_image_generation():
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-image-1.5",
        "prompt": "A cute cat sleeping on a sofa, clean anime style.",
        "n": 1,
        "size": "1024x1024"
    }

    try:
        print("🚀 Sending request to OpenAI API...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                if 'b64_json' in result['data'][0]:
                    img_data = base64.b64decode(result['data'][0]['b64_json'])
                    with open("c:/jungho_webhome/school_cloud/test_output.jpg", "wb") as f:
                        f.write(img_data)
                    print("✅ Success! Image saved to test_output.jpg")
                else:
                    print("❌ Missing b64_json in response")
                    print(json.dumps(result, indent=2))
            else:
                print("❌ Unexpected data format")
        else:
            print("❌ Error from API:")
            print(json.dumps(response.json(), indent=2))
            
    except Exception as e:
        print(f"🚨 Exception occurred: {e}")

if __name__ == "__main__":
    test_openai_image_generation()
