from django import forms
from .models import MediaPost, TextPost, CodeLink

class MediaPostForm(forms.ModelForm):
    class Meta:
        model = MediaPost
        fields = ['title', 'file', 'description', 'apply_webtoon_filter']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '사진 제목을 입력하세요'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '사진에 대한 설명을 자유롭게 남겨주세요'}),
            'apply_webtoon_filter': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class TextPostForm(forms.ModelForm):
    class Meta:
        model = TextPost
        fields = ['title', 'author_name', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '글 제목'}),
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '작성자 (이름)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': '내용을 입력하세요'}),
        }

class CodeLinkForm(forms.ModelForm):
    class Meta:
        model = CodeLink
        fields = ['title', 'category', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '자료 제목'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '자료 설명'}),
        }
