from django.shortcuts import render
from .models import Post

def index(request):
    # 최신 글 순서대로 가져오기
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'posts': posts})