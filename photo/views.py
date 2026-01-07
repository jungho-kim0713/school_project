"""
[파일 경로] photo/views.py
[설명] 검색 기능(q)이 고도화된 뷰입니다.
사용자 입력(제목, 사용자 설명)과 AI 분석(AI 설명)을 동시에 검색(OR 조건)합니다.
"""
from django.shortcuts import render
from django.db.models import Q  # 검색 기능을 위해 추가 (OR 연산)
from .models import MediaPost, TextPost, CodeLink, OfficialLink

def index(request):
    # 1. 검색어 가져오기 (GET 파라미터 'q')
    query = request.GET.get('q', '')

    # 2. 모델별 데이터 가져오기 (기본: 최신순 정렬)
    media_posts = MediaPost.objects.all().order_by('-created_at')
    text_posts = TextPost.objects.all().order_by('-created_at')
    code_links = CodeLink.objects.all().order_by('-created_at')
    official_links = OfficialLink.objects.all() # 링크는 순서 상관 없음

    # 3. 검색어가 있는 경우 필터링 (Triple Hybrid Search)
    if query:
        # [핵심] 이미지 갤러리 검색: 제목 OR 사용자 설명 OR AI 설명
        # 이 세 가지 필드 중 하나라도 검색어를 포함하면 결과에 나옵니다.
        media_posts = media_posts.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |  # <--- 사용자 설명 추가됨
            Q(ai_caption__icontains=query)
        )
        
        # [보너스] 게시판과 코드 자료실도 제목으로 검색되도록 유지
        text_posts = text_posts.filter(title__icontains=query)
        code_links = code_links.filter(title__icontains=query)

    # 4. 하나의 context 꾸러미에 담기
    context = {
        'media_posts': media_posts,
        'text_posts': text_posts,
        'code_links': code_links,
        'official_links': official_links,
        'search_term': query, # 검색어를 템플릿 검색창에 남겨두기 위해 전달
    }

    # 5. HTML 렌더링
    return render(request, 'index.html', context)