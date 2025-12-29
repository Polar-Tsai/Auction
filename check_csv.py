#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os

data_dir = r'c:\Users\polar.KINGSTEEL\OneDrive - 鉅鋼機械股份有限公司 King Steel Machinery Co., Ltd\001-鉅鋼工作\2025\SDD\AuctionWebsite\ActionWebsite\data'
products_csv = os.path.join(data_dir, 'products.csv')

print(f"Checking file: {products_csv}")
print(f"File exists: {os.path.exists(products_csv)}")
print(f"File size: {os.path.getsize(products_csv)} bytes")
print("\n" + "="*60)

try:
    # Try reading with utf-8-sig encoding
    df = pd.read_csv(products_csv, encoding='utf-8-sig')
    print("\nSuccessfully read with utf-8-sig encoding")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nNumber of rows: {len(df)}")
    print(f"\nDataFrame info:")
    print(df.info())
    print(f"\nFirst 2 rows:")
    print(df.head(2))
    
    # Check if 'id' column exists
    if 'id' in df.columns:
        print("\n✓ 'id' column exists")
        print(f"ID values: {df['id'].tolist()}")
    else:
        print("\n✗ 'id' column NOT FOUND!")
        print("This is likely the source of the error!")
        
except Exception as e:
    print(f"\n✗ Error reading CSV: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
