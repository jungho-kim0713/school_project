from django.contrib import admin
from django.utils.html import format_html
from .models import MediaPost, TextPost, CodeLink, OfficialLink, Comment

admin.site.site_header = "학교 AI 홍보 플랫폼 관리"
admin.site.index_title = "콘텐츠 통합 관리소"

@admin.register(MediaPost)
class MediaPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_likes_count', 'is_public', 'created_at', 'has_original')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description')

    def get_likes_count(self, obj):
        return obj.likes.count()
    get_likes_count.short_description = '좋아요 수'

    # 'file_url', 'original_file_url'을 읽기 전용으로 화면에 표시
    readonly_fields = ('file_url', 'original_file_url', 'file_preview', 'original_preview')

    # 카툰 필터 적용된 파일의 URL
    def file_url(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.url)
        return "파일 없음"
    file_url.short_description = "🎨 변환된 파일 URL (애니메이션 스타일)"

    # 원본 파일의 URL (관리자 전용)
    def original_file_url(self, obj):
        if obj.original_file:
            return format_html(
                '<a href="{}" target="_blank" style="color: red; font-weight: bold;">⚠️ 원본 파일 보기 (개인정보 포함)</a>',
                obj.original_file.url
            )
        return "원본 없음"
    original_file_url.short_description = "📁 원본 파일 URL (관리자 전용)"

    # 카툰 필터 적용된 이미지 미리보기
    def file_preview(self, obj):
        if obj.file:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border: 2px solid #4CAF50;" />',
                obj.file.url
            )
        return "미리보기 없음"
    file_preview.short_description = "🎨 애니메이션 스타일 미리보기"

    # 원본 이미지 미리보기
    def original_preview(self, obj):
        if obj.original_file:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border: 2px solid #f44336;" />',
                obj.original_file.url
            )
        return "원본 없음"
    original_preview.short_description = "📁 원본 이미지 미리보기 (관리자 전용)"

    # 목록에서 원본 보유 여부 표시
    def has_original(self, obj):
        if obj.original_file:
            return format_html('<span style="color: green;">{}</span>', '✅')
        return format_html('<span style="color: gray;">{}</span>', '❌')
    has_original.short_description = "원본 보유"

@admin.register(TextPost)
class TextPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'created_at')
    search_fields = ('title', 'author_name')

@admin.register(CodeLink)
class CodeLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')

@admin.register(OfficialLink)
class OfficialLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_type', 'url')
    list_editable = ('url',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    search_fields = ('content', 'author__username')

# ----------------------------------------------------
# 5. [NEW] 사용자 일괄 등록 (CSV) 기능 추가
# ----------------------------------------------------
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html
import csv
import io

class CustomUserAdmin(UserAdmin):
    change_list_template = 'admin/auth/user/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='user_upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_file")
            
            if not csv_file:
                messages.error(request, "파일이 없습니다.")
                return redirect("..")
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "CSV 파일만 업로드 가능합니다.")
                return redirect("..")

            try:
                decoded_file = csv_file.read().decode('utf-8-sig') # BOM 처리
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                
                success_count = 0
                skip_count = 0
                
                for row in csv_data:
                    email = row.get('email', '').strip()
                    name = row.get('name', '').strip()
                    
                    if not email:
                        continue
                        
                    if User.objects.filter(email=email).exists():
                        skip_count += 1
                        continue
                    
                    # 유저 생성 (비밀번호 없음, 즉시 활성화)
                    user = User.objects.create_user(
                        username=email, # username을 이메일로 설정
                        email=email,
                        first_name=name,
                        password=None
                    )
                    user.is_active = True # 핵심: 즉시 승인
                    user.set_unusable_password()
                    user.save()
                    success_count += 1
                    
                messages.success(request, f"✅ {success_count}명 등록 완료 (사전 등록된 계정 포함 건너뜀: {skip_count}명)")
                return redirect("admin:auth_user_changelist")
                
            except Exception as e:
                messages.error(request, f"업로드 중 오류 발생: {str(e)}")
                return redirect("..")

        # GET 요청 시 폼 렌더링
        context = {
            # 필요한 경우 admin context 추가
            **self.admin_site.each_context(request),
        }
        return render(request, "admin/upload_csv.html", context)

# 기존 User Admin 해제 후 커스텀 등록
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)