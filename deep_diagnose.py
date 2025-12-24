#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
深度診斷工具 - 測試資料讀取和環境設定
"""
import os
import sys

print("=" * 60)
print("拍賣網站深度診斷工具")
print("=" * 60)
print()

# 1. 檢查當前目錄
print("[1] 當前工作目錄:")
print(f"    {os.getcwd()}")
print()

# 2. 檢查 .env 檔案
print("[2] 檢查 .env 檔案:")
env_path = ".env"
if os.path.exists(env_path):
    print(f"    ✓ .env 存在")
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"    共 {len(lines)} 行")
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            key = line.split('=')[0]
            print(f"    - {key}: {'已設定' if '=' in line and len(line.split('=', 1)[1].strip()) > 0 else '未設定'}")
else:
    print(f"    ✗ .env 不存在！")
print()

# 3. 測試環境變數讀取
print("[3] 測試環境變數讀取:")
from dotenv import load_dotenv
load_dotenv()

admin_pwd = os.getenv('ADMIN_PASSWORD')
secret_key = os.getenv('DJANGO_SECRET_KEY')
debug = os.getenv('DEBUG')

print(f"    ADMIN_PASSWORD: {'已設定 (長度: ' + str(len(admin_pwd)) + ')' if admin_pwd else '未設定'}")
print(f"    DJANGO_SECRET_KEY: {'已設定 (長度: ' + str(len(secret_key)) + ')' if secret_key else '未設定'}")
print(f"    DEBUG: {debug}")
print()

# 4. 測試 CSV 檔案讀取
print("[4] 測試 CSV 資料讀取:")
data_dir = os.path.join(os.getcwd(), 'data')
print(f"    資料目錄: {data_dir}")

try:
    import pandas as pd
    
    # 測試 employees.csv
    emp_path = os.path.join(data_dir, 'employees.csv')
    print(f"\n    [4.1] 讀取 employees.csv:")
    print(f"          檔案路徑: {emp_path}")
    print(f"          檔案存在: {os.path.exists(emp_path)}")
    
    if os.path.exists(emp_path):
        # 測試不同編碼
        for encoding in ['utf-8', 'utf-8-sig', 'big5', 'gbk']:
            try:
                df = pd.read_csv(emp_path, dtype=str, encoding=encoding)
                print(f"          ✓ 使用 {encoding} 編碼成功讀取")
                print(f"          - 總筆數: {len(df)}")
                print(f"          - 欄位: {list(df.columns)}")
                
                # 檢查特定工號
                if 'employeeId' in df.columns:
                    target_id = '1244'
                    result = df[df['employeeId'] == target_id]
                    print(f"          - 工號 '{target_id}' 查詢結果: {'找到' if not result.empty else '未找到'}")
                    
                    if result.empty:
                        print(f"          - 現有工號列表:")
                        for emp_id in df['employeeId'].head(10):
                            print(f"            * '{emp_id}' (長度: {len(str(emp_id))}, 類型: {type(emp_id).__name__})")
                    else:
                        print(f"          - 資料: {result.iloc[0].to_dict()}")
                break
            except Exception as e:
                print(f"          ✗ 使用 {encoding} 編碼失敗: {str(e)}")
except ImportError:
    print("    ✗ pandas 未安裝")
except Exception as e:
    print(f"    ✗ 錯誤: {str(e)}")

print()

# 5. 測試 ExcelAdapter
print("[5] 測試 ExcelAdapter:")
try:
    sys.path.insert(0, os.getcwd())
    from auctions.excel_adapter import ExcelAdapter
    
    adapter = ExcelAdapter(data_dir)
    
    # 測試讀取員工
    print(f"    [5.1] 測試 get_employee_by_employeeId('1244'):")
    emp = adapter.get_employee_by_employeeId('1244')
    if emp:
        print(f"          ✓ 找到員工: {emp}")
    else:
        print(f"          ✗ 未找到員工")
        
        # 嘗試列出所有員工
        print(f"    [5.2] 列出前 5 位員工:")
        try:
            df = pd.read_csv(adapter.employees_path, dtype=str)
            for idx, row in df.head(5).iterrows():
                print(f"          - {row.to_dict()}")
        except Exception as e:
            print(f"          ✗ 無法列出: {str(e)}")
            
except Exception as e:
    print(f"    ✗ ExcelAdapter 測試失敗: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("診斷完成")
print("=" * 60)
