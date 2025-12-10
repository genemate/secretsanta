# PYTHONANYWHERE WSGI CONFIGURATION

import os
import sys

# Add your project directory to the sys.path
path = '/home/genemator/secret-santa-bot'  # Замените YOUR_USERNAME на ваш username
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'secret_santa.settings'

# Load .env file
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Initialize Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
