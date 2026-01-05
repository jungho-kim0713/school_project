"""
[파일 경로] photo/views.py
[설명] 4가지 모델의 데이터를 모두 가져와 index.html로 전달합니다.
"""
from django.shortcuts import render
from .models import MediaPost, TextPost, CodeLink, OfficialLink

def index(request):
    # 1. 각 모델에서 최신 데이터 가져오기
    media_posts = MediaPost.objects.all().order_by('-created_at')
    text_posts = TextPost.objects.all().order_by('-created_at')
    code_links = CodeLink.objects.all().order_by('-created_at')
    official_links = OfficialLink.objects.all()

    # 2. 하나의 context 꾸러미에 담기
    context = {
        'media_posts': media_posts,
        'text_posts': text_posts,
        'code_links': code_links,
        'official_links': official_links,
    }

    # 3. HTML 렌더링
    return render(request, 'index.html', context)