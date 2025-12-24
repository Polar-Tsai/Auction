#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CSV 編碼轉換工具 - 將所有 CSV 轉換為 UTF-8-BOM 編碼
"""
import os
import codecs

def convert_csv_encoding(file_path):
    """
    嘗試多種編碼讀取 CSV，然後轉換為 UTF-8-BOM
    """
    encodings = ['utf-8', 'utf-8-sig', 'big5', 'gbk', 'cp950', 'latin1']
    
    content = None
    used_encoding = None
    
    # 嘗試讀取
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            print(f"  ✓ 使用 {encoding} 成功讀取")
            break
        except Exception as e:
            continue
    
    if content is None:
        print(f"  ✗ 無法讀取檔案 {file_path}")
        return False
    
    # 備份原始檔案
    backup_path = file_path + '.backup'
    try:
        with open(backup_path, 'wb') as f:
            with open(file_path, 'rb') as original:
                f.write(original.read())
        print(f"  ✓ 已備份至 {backup_path}")
    except Exception as e:
        print(f"  ✗ 備份失敗: {e}")
        return False
    
    # 寫入為 UTF-8-BOM
    try:
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(content)
        print(f"  ✓ 已轉換為 UTF-8-BOM 編碼")
        return True
    except Exception as e:
        print(f"  ✗ 轉換失敗: {e}")
        # 還原備份
        with open(backup_path, 'rb') as backup:
            with open(file_path, 'wb') as original:
                original.write(backup.read())
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("CSV 編碼轉換工具")
    print("=" * 60)
    print()
    
    data_dir = os.path.join(os.getcwd(), 'data')
    csv_files = ['employees.csv', 'products.csv', 'bids.csv']
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        print(f"處理 {csv_file}...")
        
        if not os.path.exists(file_path):
            print(f"  ⚠ 檔案不存在，跳過")
            print()
            continue
        
        if convert_csv_encoding(file_path):
            print(f"  ✅ {csv_file} 轉換成功")
        else:
            print(f"  ❌ {csv_file} 轉換失敗")
        print()
    
    print("=" * 60)
    print("轉換完成！請重新啟動伺服器")
    print("=" * 60)
