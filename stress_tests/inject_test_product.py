import sys
import os
import pytz
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from auctions.excel_adapter import ExcelAdapter

def setup_test_product():
    DATA_DIR = os.path.join(os.getcwd(), 'data')
    adapter = ExcelAdapter(DATA_DIR)
    
    product_id = 9999
    print(f"Adding/Resetting stress test product {product_id} in LIVE environment...")
    
    # We use update_product or manually inject to ensure it's 'Open'
    # Actually, let's use save_product to be safe, but it generates ID.
    # We will manually handle products.csv for this specific hack.
    
    f, df = adapter._lock_and_read(adapter.products_path)
    try:
        # Remove if exists
        df = df[df['id'] != product_id]
        
        # Add new
        new_prod = {
            'id': product_id,
            'name': 'STRESS_TEST_DO_NOT_BID',
            'start_price': 100,
            'current_price': 100,
            'status': 'Open',
            'start_time': '2020-01-01T00:00',
            'end_time': '2099-01-01T00:00',
            'brand': 'SYSTEM_TEST',
            'description': 'Automated stress test product',
            'bids_count': 0,
            'highest_bidder_id': ''
        }
        import pandas as pd
        df = pd.concat([df, pd.DataFrame([new_prod])], ignore_index=True)
        adapter._write_and_unlock(f, df)
        print(f"✅ Success: Product {product_id} is now OPEN in live system.")
    except Exception as e:
        print(f"❌ Error: {e}")
        try: adapter._write_and_unlock(f, df)
        except: pass

if __name__ == "__main__":
    setup_test_product()
