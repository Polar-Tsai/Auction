import os
import sys
import django
from django.core.management import call_command
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

print("Starting custom test runner...")
try:
    call_command('test', 'auctions.tests.test_services', verbosity=2)
except Exception as e:
    print("Exception during test run:")
    traceback.print_exc()
except SystemExit as e:
    print(f"SystemExit: {e}")
