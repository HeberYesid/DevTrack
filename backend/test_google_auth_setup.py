import os
import django
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print(f"GOOGLE_CLIENT_ID from settings: '{settings.GOOGLE_CLIENT_ID}'")

try:
    import google.auth
    print(f"google-auth version: {google.auth.__version__}")
except ImportError:
    print("google-auth not installed")
