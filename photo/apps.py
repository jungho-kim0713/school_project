from django.apps import AppConfig

class PhotoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photo'

    def ready(self):
        """
        Django 앱이 시작될 때 signals.py를 임포트하여
        이벤트 리스너(AI 분석기, 파일 삭제기)를 등록합니다.
        """
        # [수정] 절대 경로 import 대신 상대 경로 .signals 사용 시도
        # 또는 try-except로 감싸서 에러 원인을 더 명확히 파악하거나,
        # 순환 참조를 피하기 위해 함수 내부에서 import
        try:
            from . import signals
        except ImportError:
            # 만약 상대 경로가 안 되면 절대 경로 시도
            import photo.signals