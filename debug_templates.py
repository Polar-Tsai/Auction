import os
import django
from django.conf import settings
from django.template import Template, Context, Engine

# Configure minimal Django settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=[
            'django.contrib.staticfiles',
            'auctions',
        ],
        BASE_DIR=BASE_DIR,
    )
    django.setup()

def check_template(filename):
    print(f"Checking {filename}...")
    try:
        with open(os.path.join(BASE_DIR, 'templates', filename), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse
        # We assume base.html exists, but we might just test the template content directly if it extends.
        # If it extends, we need the engine to find base.html
        engine = Engine.get_default()
        t = engine.from_string(content)
        print(f"✅ {filename} Syntax OK")
    except Exception as e:
        print(f"❌ {filename} Error: {e}")

if __name__ == "__main__":
    check_template('admin_product_form.html')
    check_template('admin_products_list.html')
    check_template('admin_dashboard.html')
