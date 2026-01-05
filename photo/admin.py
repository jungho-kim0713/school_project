from django.contrib import admin
from django.utils.html import format_html
from .models import MediaPost, TextPost, CodeLink, OfficialLink

admin.site.site_header = "학교 AI 홍보 플랫폼 관리"
admin.site.index_title = "콘텐츠 통합 관리소"

@admin.register(MediaPost)
class MediaPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'like_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'description')
    
    # 'file_url'과 'ai_caption'을 읽기 전용으로 화면에 표시합니다.
    readonly_fields = ('file_url', 'ai_caption')

    # 파일의 전체 URL을 보여주는 함수
    def file_url(self, obj):
        if obj.file:
            # 클릭 가능한 링크 형태로 보여줍니다.
            return format_html('<a href="{}" target="_blank">{}</a>', obj.file.url, obj.file.url)
        return "파일 없음"
    
    file_url.short_description = "파일 URL (OCI 저장소)"

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