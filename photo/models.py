from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=50, verbose_name="제목")
    
    # 학교 홍보용이므로 사진은 필수입니다.
    # upload_to='posts/'는 media/posts/ 폴더에 저장된다는 뜻입니다.
    image = models.ImageField(upload_to='posts/', verbose_name="홍보 사진") 
    
    content = models.TextField(verbose_name="내용", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")

    def __str__(self):
        return f"[{self.id}] {self.title}"