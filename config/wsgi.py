import os

from django.core.wsgi import get_wsgi_application

# settings.py가 어디 있는지 알려주는 역할
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()