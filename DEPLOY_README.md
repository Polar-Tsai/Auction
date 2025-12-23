# 🚀 虛擬機快速部署指南

## 一鍵部署步驟

### 1️⃣ 開啟 PowerShell
在專案目錄點擊右鍵 → 選擇「在終端機中開啟」或「Open PowerShell window here」

### 2️⃣ 執行部署腳本
```powershell
.\deploy_setup.ps1
```

如果遇到「無法執行指令碼」的錯誤，請先執行：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\deploy_setup.ps1
```

---

## 📋 腳本會自動完成的工作

✅ **步驟 1**: 檢查 Python 安裝  
✅ **步驟 2**: 升級 pip 到最新版本  
✅ **步驟 3**: 安裝 requirements.txt 中的所有套件  
✅ **步驟 4**: 建立 .env 環境變數檔案（如果不存在）  
✅ **步驟 5**: 執行資料庫遷移 (migrate)  
✅ **步驟 6**: 編譯翻譯檔案 (compile translations)  
✅ **步驟 7**: 建立必要的目錄 (data, data_photo, static)  

---

## ⚙️ 部署後必做事項

### 1. 編輯 `.env` 檔案
```env
DJANGO_SECRET_KEY=<隨機產生一個長密鑰>
DEBUG=False
ALLOWED_HOSTS=test-auction.kingsteel.com,<您的VM IP位址>
ADMIN_PASSWORD=<設定您的管理員密碼>
```

**產生隨機密鑰方法**：
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. 複製資料檔案
- 將 Excel 資料檔案複製到 `data/` 目錄
- 將產品圖片複製到 `data_photo/` 目錄

### 3. 啟動伺服器
```powershell
python run_server.py
```

**使用 Port 80** (需要系統管理員權限):
```powershell
# 以系統管理員身份開啟 PowerShell，然後執行：
cd <專案路徑>
python run_server.py
```

---

## 🔥 設定防火牆（重要！）

以系統管理員身份執行 PowerShell：
```powershell
# 允許 Port 80
New-NetFirewallRule -DisplayName "拍賣網站 Port 80" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow

# 允許 Port 8080（備用）
New-NetFirewallRule -DisplayName "拍賣網站 Port 8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

---

## 🔄 設定開機自動啟動

### 方法一：Windows 工作排程器
1. 開啟「工作排程器」
2. 建立基本工作：
   - 名稱：`啟動拍賣網站`
   - 觸發程序：**電腦啟動時**
   - 動作：**啟動程式**
     - 程式：`python`
     - 引數：`run_server.py`
     - 起始於：`<專案完整路徑>`
   - 勾選「以最高權限執行」

### 方法二：使用 NSSM（推薦）
1. 下載 NSSM: https://nssm.cc/download
2. 解壓縮並以系統管理員執行：
```powershell
.\nssm.exe install AuctionWebsite
```
3. 設定視窗：
   - Path: `C:\Python311\python.exe`（您的 Python 安裝路徑）
   - Startup directory: `<專案完整路徑>`
   - Arguments: `run_server.py`
4. 啟動服務：
```powershell
.\nssm.exe start AuctionWebsite
```

---

## ✅ 驗證部署成功

1. 在瀏覽器開啟：`http://localhost` 或 `http://test-auction.kingsteel.com`
2. 檢查登入頁面是否正常顯示
3. 測試語言切換功能（中文/印尼文）
4. 登入後台管理介面

---

## 🆘 常見問題

**Q: 執行腳本時出現「禁止執行」錯誤？**  
A: 執行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 後再試一次

**Q: 套件安裝失敗？**  
A: 確認網路連線正常，或手動執行 `pip install -r requirements.txt`

**Q: 無法綁定 Port 80？**  
A: 需要以系統管理員身份執行，或使用 Port 8080

**Q: 翻譯檔案編譯失敗？**  
A: 不影響主要功能，可手動執行 `python compile_with_msgfmt.py` 或忽略

---

## 📞 需要協助？

如有問題請檢查：
1. `error_log.txt` - 錯誤記錄檔
2. PowerShell 終端機輸出訊息
3. 確認所有檔案路徑正確
