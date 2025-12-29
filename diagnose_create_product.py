import sys
import os

# Add detailed diagnosis for the create product issue
sys.path.insert(0, r'c:\Users\polar.KINGSTEEL\OneDrive - 鉅鋼機械股份有限公司 King Steel Machinery Co., Ltd\001-鉅鋼工作\2025\SDD\AuctionWebsite\ActionWebsite')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auction_site.settings')

import django
django.setup()

from auctions.excel_adapter import ExcelAdapter
from django.conf import settings

print("="*60)
print("DIAGNOSTIC TEST - CREATE PRODUCT SIMULATION")
print("="*60)

adapter = ExcelAdapter(settings.DATA_DIR)

# Test 1: Check if products.csv exists and is readable
print("\n1. Checking products.csv...")
try:
    products = adapter.get_all_products()
    print(f"   ✓ Successfully read {len(products)} products")
    print(f"   ✓ Products have these fields: {list(products[0].keys()) if products else 'No products'}")
except Exception as e:
    print(f"   ✗ Error reading products: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Simulate creating a product
print("\n2. Simulating product creation...")
test_product = {
    'name': 'Test Product',
    'start_price': 1000,
    'description': 'Test description',
    'image_url': '',
    'start_time': '2025-12-26T10:00:00',
    'end_time': '2025-12-27T10:00:00',
    'status': 'Upcoming'
}

try:
    new_id = adapter.save_product(test_product)
    print(f"   ✓ Product created successfully with ID: {new_id}")
    
    # Verify it was saved
    created_product = adapter.get_product_by_id(new_id)
    print(f"   ✓ Product retrieved: {created_product['name']}")
    
    # Clean up - delete the test product
    adapter.delete_product(new_id)
    print(f"   ✓ Test product deleted")
    
except Exception as e:
    print(f"   ✗ Error creating product: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check template context rendering
print("\n3. Testing template context...")
from django.template import Context, Template

# Simulate the template with empty product dict
template_code = """
<input name="name" value="{{ product.name|default:'' }}" />
<input name="start_price" value="{{ product.start_price|default:'' }}" />
Status: {{ product.status|default:'Upcoming' }}
"""

try:
    template = Template(template_code)
    context = Context({'product': {}, 'action': 'Create'})
    rendered = template.render(context)
    print("   ✓ Template rendered successfully with empty product dict:")
    print(rendered)
except Exception as e:
    print(f"   ✗ Template rendering error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("="*60)
