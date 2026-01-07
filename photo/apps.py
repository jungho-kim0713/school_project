from django.apps import AppConfig

class PhotoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photo'

    def ready(self):
        """
        앱 시작 시 signals.py를 안전하게 불러옵니다.
        """
        try:
            import photo.signals
        except ImportError:
            pass