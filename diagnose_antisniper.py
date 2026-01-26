"""
Anti-Sniper 機制診斷工具

此腳本用於分析 anti-sniper 觸發的時間差異問題。
可以從日誌中提取關鍵資訊或進行時間測試。
"""

import os
import sys
import django
from datetime import datetime
import pytz

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auction_site.settings")
django.setup()

from auctions.excel_adapter import ExcelAdapter
from auctions.services import BidService

TAIPEI_TZ = pytz.timezone('Asia/Taipei')

def analyze_bid_timing():
    """
    分析出價時間與 anti-sniper 觸發的關係
    """
    print("=" * 60)
    print("Anti-Sniper 機制診斷分析")
    print("=" * 60)
    
    # 模擬不同的網路延遲情況
    delays = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    print("\n假設用戶在看到剩餘時間為 10 秒時出價：")
    print("-" * 60)
    print(f"{'網路延遲(秒)':<15} {'伺服器收到時剩餘':<20} {'是否觸發加時':<15}")
    print("-" * 60)
    
    for delay in delays:
        server_remaining = 10 - delay
        triggered = 0 < server_remaining < 10
        status = "✅ 觸發" if triggered else "❌ 不觸發"
        print(f"{delay:<15} {server_remaining:<20} {status:<15}")
    
    print("\n" + "=" * 60)
    print("假設用戶在看到剩餘時間為 5 秒時出價：")
    print("-" * 60)
    print(f"{'網路延遲(秒)':<15} {'伺服器收到時剩餘':<20} {'是否觸發加時':<15}")
    print("-" * 60)
    
    for delay in delays:
        server_remaining = 5 - delay
        triggered = 0 < server_remaining < 10
        status = "✅ 觸發" if triggered and server_remaining > 0 else "❌ 不觸發"
        if server_remaining <= 0:
            status = "⏱️ 已結束"
        print(f"{delay:<15} {server_remaining:<20} {status:<15}")
    
    print("\n" + "=" * 60)

def check_current_products():
    """
    檢查當前產品的狀態和結束時間
    """
    print("\n當前產品狀態檢查")
    print("=" * 60)
    
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    adapter = ExcelAdapter(DATA_DIR)
    
    products = adapter.get_all_products()
    current_time = datetime.now(TAIPEI_TZ)
    
    print(f"\n伺服器當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("-" * 60)
    
    open_products = [p for p in products if p.get('status') == 'Open']
    
    if not open_products:
        print("目前沒有進行中的拍賣")
        return
    
    print(f"\n進行中的拍賣 ({len(open_products)} 個):")
    print("-" * 60)
    
    for product in open_products:
        end_time = product.get('end_time')
        if isinstance(end_time, datetime):
            if end_time.tzinfo is None:
                end_time = TAIPEI_TZ.localize(end_time)
            
            time_remaining = (end_time - current_time).total_seconds()
            
            print(f"\n產品 ID: {product['id']}")
            print(f"產品名稱: {product.get('name', 'N/A')}")
            print(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"剩餘時間: {time_remaining:.1f} 秒")
            
            if 0 < time_remaining < 10:
                print("⚠️  目前處於 anti-sniper 觸發區間！")
            elif time_remaining < 0:
                print("⏱️  拍賣已結束（狀態可能尚未更新）")
            else:
                print(f"✅ 距離 anti-sniper 觸發還有 {time_remaining - 10:.1f} 秒")

def recommendations():
    """
    提供建議和解決方案
    """
    print("\n" + "=" * 60)
    print("診斷結論與建議")
    print("=" * 60)
    
    print("""
📊 問題分析：
-----------
您遇到的問題是由「網路延遲」造成的，不是裝置時間誤差。

原因：
1. Anti-sniper 的判斷是在伺服器端進行
2. 伺服器使用「接收到請求的時間」來計算剩餘時間
3. 從用戶點擊到伺服器接收，有網路傳輸時間（RTT）

範例情境（假設網路延遲 5 秒）：
- 用戶看到「剩餘 10 秒」→ 點擊出價
- 伺服器收到時「剩餘 5 秒」→ 觸發 anti-sniper ✅
- 
- 用戶看到「剩餘 6 秒」→ 點擊出價  
- 伺服器收到時「剩餘 1 秒」→ 觸發 anti-sniper ✅

但如果網路很順暢（延遲 1 秒）：
- 用戶看到「剩餘 10 秒」→ 點擊出價
- 伺服器收到時「剩餘 9 秒」→ 觸發 anti-sniper ✅


💡 解決方案建議：
---------------
1. 【增加日誌記錄】在 services.py 中記錄更詳細的時間資訊：
   - 記錄收到請求時的剩餘時間
   - 記錄是否觸發 anti-sniper 的判斷過程
   
2. 【調整門檻值】考慮將 ANTI_SNIPER_THRESHOLD_SECONDS 增加：
   - 目前：10 秒
   - 建議：15-20 秒（考慮網路延遲）
   
3. 【前端提示】在前端加上延遲估計提示：
   - 顯示「建議提前 X 秒出價以確保觸發加時」
   
4. 【監控延遲】定期監控用戶的平均 RTT：
   - 在 polling.js 中記錄時間同步的 offset
   - 分析用戶端與伺服器的時間差異

5. 【測試環境 vs 正式環境】
   - 測試環境：通常延遲較低（< 100ms）
   - 正式環境：可能有更高延遲（尤其遠端用戶）
   - VPN、防火牆等都可能增加延遲


🔍 如何測量實際延遲：
------------------
在瀏覽器開發者工具中：
1. 打開 Network 標籤
2. 觀察 API 請求（/api/bids/）
3. 查看 "Time" 欄位，這就是 RTT
4. 典型值：
   - 本地網路：< 50ms
   - 同城：50-100ms
   - 跨城：100-300ms
   - 國際：300ms-2s+


⚠️ 關於裝置時間誤差：
------------------
裝置時間誤差「不會」影響 anti-sniper 判斷，因為：
1. 判斷完全在伺服器端進行
2. ServerTime.sync() 只影響前端顯示，不影響後端邏輯
3. 即使用戶裝置時間差 10 分鐘，也不會影響伺服器判斷

但裝置時間誤差「會」影響：
- 前端倒數計時的準確性（已透過 ServerTime.sync 修正）
- 用戶對剩餘時間的判斷
""")

if __name__ == "__main__":
    analyze_bid_timing()
    check_current_products()
    recommendations()
