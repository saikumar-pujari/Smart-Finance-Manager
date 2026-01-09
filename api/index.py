import os

# Point Django to the settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_finance.settings')

# ASGI application for serverless
from django.core.asgi import get_asgi_application
app = get_asgi_application()
