import os
import django
import sys

# Add project root to path (explicitly, though it should be there)
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')
django.setup()

print("Django setup done")

try:
    print("Attempting to import auctions.services...")
    from auctions.services import BidService
    print("Import BidService: SUCCESS")
except Exception as e:
    print("Import FAILED")
    import traceback
    traceback.print_exc()
