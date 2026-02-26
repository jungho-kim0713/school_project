from django.db import models

# 1. 이미지 및 영상 게시판 모델
class MediaPost(models.Model):
    title = models.CharField(max_length=100, verbose_name="제목")
    file = models.FileField(upload_to='media_posts/', verbose_name="이미지/영상 파일 (애니메이션 스타일)")
    original_file = models.FileField(upload_to='media_posts/originals/', verbose_name="원본 파일 (관리자 전용)", blank=True, null=True)
    ai_caption = models.TextField(verbose_name="AI 분석 설명", blank=True, null=True)
    description = models.TextField(verbose_name="설명", blank=True)
    like_count = models.PositiveIntegerField(default=0, verbose_name="좋아요 수")
    is_public = models.BooleanField(default=True, verbose_name="공개 여부")
    apply_webtoon_filter = models.BooleanField(default=False, verbose_name="웹툰체로 변환")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return f"[미디어] {self.title}"

# 2. 글 게시판 모델
class TextPost(models.Model):
    title = models.CharField(max_length=100, verbose_name="제목")
    content = models.TextField(verbose_name="본문 내용")
    author_name = models.CharField(max_length=50, verbose_name="작성자(학생명)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return f"[글] {self.title}"

# 3. 코드 및 프로젝트 공유 모델
class CodeLink(models.Model):
    CATEGORY_CHOICES = [
        ('GAME', '웹 게임'),
        ('COLAB', '구글 Colab'),
        ('GITHUB', 'GitHub 리포지토리'),
        ('OTHER', '기타 코드'),
    ]
    title = models.CharField(max_length=100, verbose_name="프로젝트 제목")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER', verbose_name="유형")
    url = models.URLField(verbose_name="공유 URL")
    description = models.TextField(verbose_name="설명", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return f"[코드] {self.title}"

# 4. 학교 공식 채널 링크 모델
class OfficialLink(models.Model):
    ICON_CHOICES = [
        ('YOUTUBE', '유튜브'),
        ('INSTAGRAM', '인스타그램'),
        ('BLOG', '블로그'),
        ('HOMEPAGE', '홈페이지'),
    ]
    title = models.CharField(max_length=50, verbose_name="사이트 이름")
    icon_type = models.CharField(max_length=20, choices=ICON_CHOICES, verbose_name="아이콘 종류")
    url = models.URLField(verbose_name="링크 주소")

    def __str__(self):
        return f"[링크] {self.title}"