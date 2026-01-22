import tempfile
import os
import pandas as pd
from django.test import SimpleTestCase
from auctions.excel_adapter import ExcelAdapter
from auctions.services import BidService
from common.exceptions import BusinessException

class BidServiceTests(SimpleTestCase):
    def setUp(self):
        # We can't easily use setUp for temporary directories that need cleanup unless we use tearDown or context managers in tests.
        # But SimpleTestCase + tempfile context manager per test is fine.
        pass

    def setup_data(self, d, start_price=300, current_price=300, status='Active'):
        # setup employees
        df_emp = pd.DataFrame([{'id':1,'employeeId':'0001','name':'TestUser','department':'IT'}])
        df_emp.to_csv(os.path.join(d,'employees.csv'), index=False)
        # setup product
        df_prod = pd.DataFrame([{
            'id':1,'name':'測試品','start_price':start_price,'current_price':current_price,'status':status,
            'start_time':'2025-12-08T10:00:00Z','end_time':'2025-12-08T16:00:00Z','last_bid_time':'',
            'brand':'','description':'','image_url':'','bids_count':0,'highest_bidder_id':''
        }])
        df_prod.to_csv(os.path.join(d,'products.csv'), index=False)
        # empty bids
        pd.DataFrame(columns=['id','product_id','bidder_id','amount','bid_timestamp']).to_csv(os.path.join(d,'bids.csv'), index=False)

    def test_place_bid_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d)
            adapter = ExcelAdapter(d)
            service = BidService(adapter)
            
            # Action
            res = service.place_bid(1, '0001', 350)
            
            # Assert
            self.assertTrue(res['success'])
            self.assertEqual(res['newPrice'], 350)

    def test_place_bid_too_low(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d, start_price=300, current_price=300)
            adapter = ExcelAdapter(d)
            service = BidService(adapter)
            
            # Action & Assert
            with self.assertRaises(BusinessException) as cm:
                service.place_bid(1, '0001', 200)
            self.assertEqual(cm.exception.code, 'INVALID_BID_AMOUNT')

    def test_place_bid_inactive(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d, status='Closed')
            adapter = ExcelAdapter(d)
            service = BidService(adapter)
            
            # Action & Assert
            with self.assertRaises(BusinessException) as cm:
                service.place_bid(1, '0001', 400)
            self.assertEqual(cm.exception.code, 'AUCTION_NOT_ACTIVE')

class AuthServiceTests(SimpleTestCase):
    def setUp(self):
        pass

    def setup_data(self, d):
        # setup employees with email
        df_emp = pd.DataFrame([{
            'id':1,
            'employeeId':'0001',
            'name':'TestUser',
            'department':'IT',
            'email':'test@kingsteel.com',
            'pwd':'0315'
        }])
        df_emp.to_csv(os.path.join(d,'employees.csv'), index=False)
        # empty products and bids
        pd.DataFrame(columns=['id','name','start_price','current_price','status','start_time','end_time','last_bid_time','brand','description','bids_count','highest_bidder_id']).to_csv(os.path.join(d,'products.csv'), index=False)
        pd.DataFrame(columns=['id','product_id','bidder_id','amount','bid_timestamp']).to_csv(os.path.join(d,'bids.csv'), index=False)

    def test_login_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d)
            adapter = ExcelAdapter(d)
            from auctions.services import AuthService
            service = AuthService(adapter)
            
            # Action: login with email and employeeId as password
            emp = service.login('test@kingsteel.com', '0001')
            
            # Assert
            self.assertIsNotNone(emp)
            self.assertEqual(emp['employeeId'], '0001')

    def test_login_failed_wrong_password(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d)
            adapter = ExcelAdapter(d)
            from auctions.services import AuthService
            service = AuthService(adapter)
            
            # Action & Assert: wrong employeeId as password
            with self.assertRaises(BusinessException) as cm:
                service.login('test@kingsteel.com', '9999')
            self.assertEqual(cm.exception.code, 'INVALID_CREDENTIALS')

    def test_login_failed_wrong_email(self):
        with tempfile.TemporaryDirectory() as d:
            self.setup_data(d)
            adapter = ExcelAdapter(d)
            from auctions.services import AuthService
            service = AuthService(adapter)
            
            # Action & Assert: wrong email
            with self.assertRaises(BusinessException) as cm:
                service.login('wrong@kingsteel.com', '0001')
            self.assertEqual(cm.exception.code, 'INVALID_CREDENTIALS')
