"""
WSGI config for secret_santa project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secret_santa.settings')

application = get_wsgi_application()
