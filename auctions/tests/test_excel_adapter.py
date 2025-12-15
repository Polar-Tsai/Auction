import tempfile
import os
import pandas as pd
from django.test import SimpleTestCase
from auctions.excel_adapter import ExcelAdapter

class ExcelAdapterTests(SimpleTestCase):
    def test_save_bid_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            # Setup
            adapter = ExcelAdapter(d)
            # Products
            pd.DataFrame([{
                'id':1, 'name':'Test', 'current_price': 100, 'bids_count':0
            }]).to_csv(os.path.join(d, 'products.csv'), index=False)
            # Empty Bids
            pd.DataFrame(columns=['id','product_id','bidder_id','amount','bid_timestamp']).to_csv(os.path.join(d,'bids.csv'), index=False)
            
            # Test save_bid
            res = adapter.save_bid(1, 'E001', 150)
            self.assertTrue(res['success'])
            self.assertEqual(res['newPrice'], 150)
            
            # Verify persistence
            df_prod = pd.read_csv(os.path.join(d, 'products.csv'))
            df_bids = pd.read_csv(os.path.join(d, 'bids.csv'))
            
            self.assertEqual(df_prod.iloc[0]['current_price'], 150)
            self.assertEqual(df_prod.iloc[0]['bids_count'], 1)
            self.assertEqual(len(df_bids), 1)
            self.assertEqual(df_bids.iloc[0]['amount'], 150)

    def test_get_employee_by_employeeId(self):
        with tempfile.TemporaryDirectory() as d:
            emp_path = os.path.join(d, 'employees.csv')
            df = pd.DataFrame([{'id':1,'employeeId':'0001','name':'張三','department':'採購部'}])
            df.to_csv(emp_path, index=False)
            pd.DataFrame(columns=['id']).to_csv(os.path.join(d,'products.csv'), index=False)
            pd.DataFrame(columns=['id']).to_csv(os.path.join(d,'bids.csv'), index=False)
            
            adapter = ExcelAdapter(d)
            emp = adapter.get_employee_by_employeeId('0001')
            self.assertIsNotNone(emp)
            self.assertEqual(emp['name'], '張三')

