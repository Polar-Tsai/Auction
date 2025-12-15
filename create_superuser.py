import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created.")
    else:
        print("Superuser 'admin' already exists.")
except Exception as e:
    print(f"Error: {e}")
