#!/usr/bin/env python
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_finance.settings')
django.setup()
User = get_user_model()

def main():
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'ChangeMe123!')

    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists")
        return
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created")

if __name__ == '__main__':
    main()
