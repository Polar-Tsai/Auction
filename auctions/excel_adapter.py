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
            (self.employees_path, ['id','employeeId','name','department','admin','pwd']),
            (self.products_path, ['id','name','start_price','current_price','status','start_time','end_time','last_bid_time','brand','description','bids_count','highest_bidder_id']),
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

    def _derive_status(self, product):
        """
        Derive status based on time, unless explicitly Unsold.
        Expects product['start_time'] and product['end_time'] to be datetime objects 
        (if already converted by _convert_product_times).
        """
        if product.get('status') == 'Unsold':
            return 'Unsold'
            
        start = product.get('start_time')
        end = product.get('end_time')
        
        if not start or not end:
            return product.get('status', 'Upcoming')

        import pytz
        tz = pytz.timezone('Asia/Taipei')
        now = datetime.now(tz)
        
        # Ensure we are comparing aware to aware
        def ensure_aware(dt):
            if isinstance(dt, str):
                # Fallback parsing if not yet converted
                try:
                    if 'T' in dt:
                        res = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                    else:
                        res = datetime.strptime(dt.strip(), "%Y-%m-%d %H:%M")
                    if res.tzinfo is None:
                        res = tz.localize(res)
                    return res
                except:
                    return None
            if isinstance(dt, datetime):
                if dt.tzinfo is None:
                    return tz.localize(dt)
                return dt
            return None

        start_dt = ensure_aware(start)
        end_dt = ensure_aware(end)

        if not start_dt or not end_dt:
            return product.get('status', 'Upcoming')

        if now < start_dt:
            return 'Upcoming'
        elif now > end_dt:
            return 'Closed'
        else:
            return 'Open'

    def get_all_products(self):
        df = pd.read_csv(self.products_path, encoding='utf-8-sig')
        df = df.fillna('')
        products = df.to_dict(orient='records')
        valid_products = []
        for p in products:
            if 'id' in p and p['id'] != '' and str(p['id']).strip():
                try:
                    p['id'] = int(float(p['id']))
                except:
                    continue
                
                # Convert times FIRST, then derive status
                p = self._convert_product_times(p)
                p['status'] = self._derive_status(p)
                
                imgs = self.get_product_images(p['id'])
                if imgs:
                    p['main_image'] = f"/data_photo/{p['id']}/{imgs[0]}"
                else:
                    p['main_image'] = None
                valid_products.append(p)
        return valid_products

    def get_product_by_id(self, product_id):
        df = pd.read_csv(self.products_path, encoding='utf-8-sig')
        df = df.fillna('')
        res = df[df['id'] == int(product_id)]
        if res.empty:
            return None
        product = res.iloc[0].to_dict()
        
        # Convert times FIRST, then derive status
        product = self._convert_product_times(product)
        product['status'] = self._derive_status(product)
        
        return product

    def _convert_product_times(self, product):
        """Helper to convert various time formats to timezone-aware datetime objects."""
        import pytz
        tz = pytz.timezone('Asia/Taipei')
        
        for field in ['start_time', 'end_time']:
            val = product.get(field)
            if not val:
                continue
            
            dt = None
            try:
                if isinstance(val, (datetime, pd.Timestamp)):
                    dt = val
                elif isinstance(val, str) and val.strip():
                    val = val.strip()
                    # Try ISO format
                    if 'T' in val:
                        try:
                            dt = datetime.fromisoformat(val.replace('Z', '+00:00'))
                        except: pass
                    
                    if not dt:
                        # Try common formats
                        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"]:
                            try:
                                dt = datetime.strptime(val, fmt)
                                break
                            except: continue
                
                if dt:
                    # Ensure it's a datetime object (not Timestamp) and aware
                    if isinstance(dt, pd.Timestamp):
                        dt = dt.to_pydatetime()
                    
                    if dt.tzinfo is None:
                        dt = tz.localize(dt)
                    product[field] = dt
            except Exception as e:
                logger.warning(f"Failed to convert {field} '{val}': {e}")
                
        return product

    def get_product_images(self, product_id):
        """
        Scan data_photo/{product_id} directory for images.
        Returns list of Media URL paths.
        """
        try:
            photo_dir = os.path.join(self.data_dir, '..', 'data_photo', str(product_id))
            if not os.path.exists(photo_dir):
                return []
            
            files = sorted(os.listdir(photo_dir))
            # Filter partial extension check or just simple one
            images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            
            # Use settings.MEDIA_URL but we are in adapter, maybe strict dep on settings is fine or pass it in.
            # Using relative path assuming usage with {{ MEDIA_URL }} or similar in template
            # For simplicity, returning full relative URL path if we assume '/media/' prefix.
            # But adapter shouldn't know URL config ideally.
            # Let's return filenames, view can construct URL.
            return images
        except Exception:
            return []

    def get_employee_by_employeeId(self, employeeId):
        try:
            df = pd.read_csv(self.employees_path, dtype=str, encoding='utf-8-sig')
            res = df[df['employeeId'] == str(employeeId)]
            if res.empty:
                return None
            return res.iloc[0].to_dict()
        except Exception:
            return None

    def get_employee_by_email(self, email):
        try:
            # Try utf-8-sig first, fallback to cp950 (Traditional Chinese)
            try:
                df = pd.read_csv(self.employees_path, dtype=str, encoding='utf-8-sig')
            except UnicodeDecodeError:
                df = pd.read_csv(self.employees_path, dtype=str, encoding='cp950')
            
            # Robustness: strip whitespaces from column names
            df.columns = [c.strip() for c in df.columns]
            
            if 'email' not in df.columns:
                logger.error(f"Column 'email' not found in {self.employees_path}. Available: {df.columns.tolist()}")
                return None
                
            # Robustness: strip whitespaces from data and case-insensitive comparison
            target_email = str(email).strip().lower()
            df['email_clean'] = df['email'].str.strip().str.lower()
            
            res = df[df['email_clean'] == target_email]
            if res.empty:
                return None
            
            # Return original data (as dict) without the 'email_clean' temp column
            result = res.iloc[0].to_dict()
            result.pop('email_clean', None)
            return result
        except FileNotFoundError:
            logger.error(f"Employees file not found at {self.employees_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading employees CSV: {str(e)}")
            return None

    def get_bids_for_product(self, product_id, limit=10):
        df = pd.read_csv(self.bids_path, encoding='utf-8-sig')
        res = df[df['product_id'] == int(product_id)].sort_values('bid_timestamp', ascending=False)
        return res.head(limit).to_dict(orient='records')

    def get_bids_for_employee(self, employee_id):
        # Specify dtypes to ensure product_id is integer, not float
        df_bids = pd.read_csv(self.bids_path, encoding='utf-8-sig', 
                             dtype={'product_id': 'Int64'})  # Use Int64 to handle NaN
        # Filter by bidder_id (employee_id should be string usually, but let's ensure type safety)
        # In save_bid we saved it as is. In login we stored it as string/from csv.
        # Let's ensure comparison works.
        res = df_bids[df_bids['bidder_id'].astype(str) == str(employee_id)].sort_values('bid_timestamp', ascending=False)
        
        bids = res.to_dict(orient='records')
        
        # Enrich with product name, highest_bidder_id, and status
        if not bids:
            return []
            
        df_prod = pd.read_csv(self.products_path, encoding='utf-8-sig',
                             dtype={'id': 'Int64'})  # Ensure product id is integer
        df_prod = df_prod.fillna('')
        
        # Create maps for product information
        prod_map = df_prod.set_index('id')['name'].to_dict()
        highest_bidder_map = df_prod.set_index('id')['highest_bidder_id'].to_dict()
        status_map = df_prod.set_index('id')['status'].to_dict()
        
        # Track the highest bid per product for this employee
        product_highest_bids = {}
        for b in bids:
            pid = b.get('product_id')
            amount = b.get('amount', 0)
            if pid not in product_highest_bids or amount > product_highest_bids[pid]:
                product_highest_bids[pid] = amount
        
        # Group bids by product
        from collections import defaultdict
        grouped_bids = defaultdict(lambda: {'bids': []})
        
        for b in bids:
            pid = b.get('product_id')
            product_name = prod_map.get(pid, f'Unknown Product ({pid})')
            
            # Determine if this bid is a winning bid
            highest_bidder = str(highest_bidder_map.get(pid, ''))
            product_status = str(status_map.get(pid, ''))
            is_highest_for_employee = (b.get('amount', 0) == product_highest_bids.get(pid, -1))
            
            # Winning conditions:
            # 1. This employee is the highest bidder for the product
            # 2. This is the employee's highest bid on this product
            # 3. Product is not marked as "Unsold" (流標)
            is_winning = (
                str(employee_id) == highest_bidder and 
                is_highest_for_employee and
                product_status != 'Unsold'
            )
            
            # Add to grouped structure
            if 'product_name' not in grouped_bids[pid]:
                grouped_bids[pid]['product_id'] = int(pid)  # Convert to int for URL reverse
                grouped_bids[pid]['product_name'] = product_name
                grouped_bids[pid]['is_winning'] = is_winning
            
            grouped_bids[pid]['bids'].append({
                'amount': b.get('amount'),
                'bid_timestamp': b.get('bid_timestamp')
            })
        
        # Convert to list and add bid counts
        result = []
        for pid, data in grouped_bids.items():
            data['bid_count'] = len(data['bids'])
            result.append(data)
        
        # Sort by latest bid timestamp (first bid in each group)
        result.sort(key=lambda x: x['bids'][0]['bid_timestamp'] if x['bids'] else '', reverse=True)
        
        return result

    def user_has_any_bids(self, bidder_id):
        """
        Check if a user has made any bids.
        Used for first-time bid confirmation feature.
        
        Args:
            bidder_id: Employee ID to check
            
        Returns:
            bool: True if user has any bid records, False if this would be their first bid
        """
        try:
            df_bids = pd.read_csv(self.bids_path, encoding='utf-8-sig')
            if df_bids.empty:
                return False
            
            # Check if this bidder has any records
            user_bids = df_bids[df_bids['bidder_id'].astype(str) == str(bidder_id)]
            return not user_bids.empty
        except Exception:
            # If there's an error reading, assume user has no bids (safer)
            return False

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
            bids_count = int(product.get('bids_count', 0)) if not pd.isna(product.get('bids_count')) else 0
            
            # For first bid: allow amount == start_price  
            # For subsequent bids: amount must be > current_price
            if bids_count == 0:
                # First bid: must be >= start_price (usually should equal start_price)
                start_price = float(product.get('start_price', 0))
                if amount < start_price:
                    raise ValueError("First bid must be at least the starting price")
            else:
                # Subsequent bids: must be > current_price
                if amount <= current_price:
                     # Race condition detected
                     raise ValueError("Race condition: Price already updated")

            # Append bid
            new_id = 1 if df_bids.empty else int(df_bids['id'].max()) + 1
            ts = datetime.now().isoformat()
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
            # Generate ID - handle case where 'id' column might not exist
            if df.empty or 'id' not in df.columns:
                new_id = 1
            else:
                new_id = int(df['id'].max()) + 1
            product_dict['id'] = new_id
            
            # Default fields
            defaults = {
                'status': 'Upcoming',
                'current_price': product_dict.get('start_price'),
                'bids_count': 0,
                'highest_bidder_id': '',
                'last_bid_time': '',
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat() # Should be set by admin
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
