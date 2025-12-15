import os
import time
import pandas as pd
import portalocker
from datetime import datetime

class ExcelAdapter:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.employees_path = os.path.join(self.data_dir, 'employees.csv')
        self.products_path = os.path.join(self.data_dir, 'products.csv')
        self.bids_path = os.path.join(self.data_dir, 'bids.csv')
        # ensure files exist
        for p, cols in [
            (self.employees_path, ['id','employeeId','name','department']),
            (self.products_path, ['id','name','start_price','current_price','status','start_time','end_time','last_bid_time','brand','description','image_url','bids_count','highest_bidder_id']),
            (self.bids_path, ['id','product_id','bidder_id','amount','bid_timestamp'])
        ]:
            if not os.path.exists(p):
                df = pd.DataFrame(columns=cols)
                df.to_csv(p, index=False)

    def _lock_and_read(self, path):
        f = open(path, 'r+', encoding='utf-8')
        portalocker.lock(f, portalocker.LOCK_EX)
        try:
            df = pd.read_csv(f)
        except Exception:
            df = pd.DataFrame()
        return f, df

    def _write_and_unlock(self, f, df):
        f.seek(0)
        f.truncate()
        df.to_csv(f, index=False)
        f.flush()
        portalocker.unlock(f)
        f.close()

    def get_all_products(self):
        df = pd.read_csv(self.products_path)
        return df.to_dict(orient='records')

    def get_product_by_id(self, product_id):
        df = pd.read_csv(self.products_path)
        res = df[df['id'] == int(product_id)]
        if res.empty:
            return None
        return res.iloc[0].to_dict()

    def get_employee_by_employeeId(self, employeeId):
        try:
            df = pd.read_csv(self.employees_path, dtype=str)
            res = df[df['employeeId'] == str(employeeId)]
            if res.empty:
                return None
            return res.iloc[0].to_dict()
        except Exception:
            return None

    def get_bids_for_product(self, product_id, limit=10):
        df = pd.read_csv(self.bids_path)
        res = df[df['product_id'] == int(product_id)].sort_values('bid_timestamp', ascending=False)
        return res.head(limit).to_dict(orient='records')

    def save_bid(self, product_id, employee_id, amount):
        """
        Transactional save of a bid.
        Updates 'bids.csv' and 'products.csv' safely.
        """
        f_prod, df_prod = self._lock_and_read(self.products_path)
        f_bids, df_bids = self._lock_and_read(self.bids_path)
        try:
            prod_idx = df_prod.index[df_prod['id'] == int(product_id)].tolist()
            if not prod_idx:
                raise Exception("Product not found during save") # Should have been caught in service
            
            i = prod_idx[0]
            product = df_prod.loc[i]
            
            # Re-read basics for race condition check (though files are locked now)
            # Logic is moved to Service, but we are inside lock now.
            # Ideally Service does checks, but for file-based DB, we might need to re-verify inside lock?
            # For this simple app, we trust Service checks OR we repeat minimal checks if strictly needed.
            # Let's assumes Service checks were for UX, but here we just write.
            # But wait, if two requests come in, Service check passes for both, then they race for lock.
            # So we SHOULD strictly check invariants here: e.g. amount > current_price.
            
            current_price = float(product.get('current_price') if not pd.isna(product.get('current_price')) else product.get('start_price',0))
            if amount <= current_price:
                 # Race condition detected
                 raise ValueError("Race condition: Price already updated")

            # Append bid
            new_id = 1 if df_bids.empty else int(df_bids['id'].max()) + 1
            ts = datetime.utcnow().isoformat()
            new_bid = {'id': new_id, 'product_id': int(product_id), 'bidder_id': employee_id, 'amount': amount, 'bid_timestamp': ts}
            
            # concat is preferred over append (deprecated) in newer pandas, but sticking to style if older.
            # Using basic list append logic if dataframe is too heavy? No, stick to DF.
            df_bids = pd.concat([df_bids, pd.DataFrame([new_bid])], ignore_index=True)
            
            # Update product
            df_prod.at[i, 'current_price'] = amount
            df_prod.at[i, 'highest_bidder_id'] = employee_id
            df_prod.at[i, 'last_bid_time'] = ts
            bids_count = int(product.get('bids_count', 0)) if not pd.isna(product.get('bids_count')) else 0
            df_prod.at[i, 'bids_count'] = bids_count + 1
            
            self._write_and_unlock(f_bids, df_bids)
            self._write_and_unlock(f_prod, df_prod)
            
            return {'success': True, 'bidId': new_id, 'newPrice': amount, 'timestamp': ts}
            

        except Exception as e:
            # Unlock on error
            try:
                portalocker.unlock(f_bids)
                f_bids.close()
            except: pass
            try:
                portalocker.unlock(f_prod)
                f_prod.close()
            except: pass
            raise e

    def save_product(self, product_dict):
        f, df = self._lock_and_read(self.products_path)
        try:
            # Generate ID
            new_id = 1 if df.empty else int(df['id'].max()) + 1
            product_dict['id'] = new_id
            
            # Default fields
            defaults = {
                'status': 'Upcoming',
                'current_price': product_dict.get('start_price'),
                'bids_count': 0,
                'highest_bidder_id': '',
                'last_bid_time': '',
                'start_time': datetime.utcnow().isoformat(),
                'end_time': datetime.utcnow().isoformat() # Should be set by admin
            }
            for k,v in defaults.items():
                if k not in product_dict:
                    product_dict[k] = v
                    
            df = pd.concat([df, pd.DataFrame([product_dict])], ignore_index=True)
            self._write_and_unlock(f, df)
            return new_id
        except Exception as e:
            try:
                portalocker.unlock(f)
                f.close()
            except: pass
            raise e

    def update_product(self, product_id, updates):
        f, df = self._lock_and_read(self.products_path)
        try:
            idx_list = df.index[df['id'] == int(product_id)].tolist()
            if not idx_list:
                raise ValueError("Product not found")
            
            i = idx_list[0]
            for k, v in updates.items():
                df.at[i, k] = v
                
            self._write_and_unlock(f, df)
            return True
        except Exception as e:
            try:
                portalocker.unlock(f)
                f.close()
            except: pass
            raise e

    def delete_product(self, product_id):
        f, df = self._lock_and_read(self.products_path)
        try:
            idx_list = df.index[df['id'] == int(product_id)].tolist()
            if not idx_list:
                 # Already gone is fine
                 self._write_and_unlock(f, df)
                 return True
            
            # Hard delete
            df = df.drop(idx_list[0])
            self._write_and_unlock(f, df)
            return True
        except Exception as e:
            try:
                portalocker.unlock(f)
                f.close()
            except: pass
            raise e
