"""
[파일 경로] photo/views.py
[설명] 검색 기능(q)이 고도화된 뷰입니다.
사용자 입력(제목, 사용자 설명)과 AI 분석(AI 설명)을 동시에 검색(OR 조건)합니다.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q  # 검색 기능을 위해 추가 (OR 연산)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import MediaPost, TextPost, CodeLink, OfficialLink, Comment
from .forms import MediaPostForm, TextPostForm, CodeLinkForm
import json

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
            Q(description__icontains=query)  # <--- 사용자 설명 추가됨
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
    # 5. HTML 렌더링
    return render(request, 'index.html', context)

# ----------------------------
# 📝 작성 기능 (Views) 
# 모델별로 별도 페이지 없이 처리하거나, 리디렉션만 함
# ----------------------------

@login_required
def media_create(request):
    if request.method == 'POST':
        form = MediaPostForm(request.POST, request.FILES)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json' or 'fetch' in request.headers.get('accept', '')

        if form.is_valid():
            post = form.save(commit=False)
            post.is_public = True # 기본적으로 공개 (관리자가 추후 숨김 가능)
            post.save()
            if is_ajax:
                return JsonResponse({"status": "success", "message": "사진이 업로드 되었습니다."})
            return redirect('/?tab=media') # 갤러리 탭으로 복귀
        else:
            if is_ajax:
                return JsonResponse({"status": "error", "message": "입력값이 올바르지 않습니다.", "errors": form.errors}, status=400)
    return redirect('/')

@login_required
def text_create(request):
    if request.method == 'POST':
        form = TextPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/?tab=text') # 게시판 탭으로 복귀
    return redirect('/')

@login_required
def code_create(request):
    if request.method == 'POST':
        form = CodeLinkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/?tab=code') # 자료실 탭으로 복귀
    return redirect('/')

# ----------------------------
# ❤️ 좋아요 & 💬 댓글 기능
# ----------------------------

@login_required
def toggle_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(MediaPost, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({'status': 'success', 'liked': liked, 'likes_count': post.likes.count()})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(MediaPost, id=post_id)
        content = request.POST.get('content')
        if not content:
            try:
                data = json.loads(request.body)
                content = data.get('content')
            except:
                pass
        
        if content:
            comment = Comment.objects.create(post=post, author=request.user, content=content)
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json' or 'fetch' in request.headers.get('accept', '')
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'comment_id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%m.%d %H:%M')
                })
            return redirect('/?tab=media')
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.author or request.user.is_superuser:
            comment.delete()
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('accept') == 'application/json' or 'fetch' in request.headers.get('accept', '')
            if is_ajax:
                return JsonResponse({'status': 'success'})
            return redirect('/?tab=media')
    return JsonResponse({'status': 'error'}, status=403)