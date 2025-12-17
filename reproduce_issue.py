
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.append(os.getcwd())

from auctions.excel_adapter import ExcelAdapter
from auctions.services import BidService

def test_service():
    data_dir = os.path.join(os.getcwd(), 'data')
    print(f"Testing with data dir: {data_dir}")
    
    adapter = ExcelAdapter(data_dir)
    bid_service = BidService(adapter)
    
    # Test place_bid via BidService on Product 3
    print("\n--- Testing place_bid via BidService on Product 3 ---")
    try:
        pid = 3
        print(f"Placing bid on product {pid} for Testing User...")
        # Get product to find price
        p = adapter.get_product_by_id(pid)
        if not p:
            print("Product 2 not found!")
        else:
            current = float(p.get('current_price', 0) or 0)
            start = float(p.get('start_price', 0) or 0)
            base_price = max(current, start)
            if base_price == 0: base_price = 100 # Fallback
            
            price = int(base_price) + 50
            
            res = bid_service.place_bid(pid, 'Testing User', price)
            print(f"Success! Result: {res}")
            
    except Exception as e:
        print(f"FAILED place_bid: {e}")
        if hasattr(e, 'original_exception'):
             print(f"Original Exception: {e.original_exception}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_service()
