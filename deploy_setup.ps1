# ========================================
# 拍賣網站一鍵部署腳本
# Auction Website Auto Deployment Script
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "拍賣網站部署開始 | Starting Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查是否在正確的目錄
$currentPath = Get-Location
Write-Host "[1/8] 檢查當前目錄..." -ForegroundColor Yellow
Write-Host "當前路徑: $currentPath" -ForegroundColor Gray

if (-not (Test-Path "requirements.txt")) {
    Write-Host "[錯誤] 找不到 requirements.txt，請確認您在專案根目錄執行此腳本！" -ForegroundColor Red
    Read-Host "按 Enter 鍵退出"
    exit 1
}
Write-Host "✓ 目錄確認完成" -ForegroundColor Green
Write-Host ""

# Step 1: 檢查 Python 安裝
Write-Host "[2/8] 檢查 Python 安裝..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 已安裝: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[錯誤] 找不到 Python，請先安裝 Python 3.11+" -ForegroundColor Red
    Read-Host "按 Enter 鍵退出"
    exit 1
}
Write-Host ""

# Step 2: 升級 pip
Write-Host "[3/8] 升級 pip 到最新版本..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] pip 升級失敗，繼續安裝..." -ForegroundColor Yellow
}
Write-Host "✓ pip 升級完成" -ForegroundColor Green
Write-Host ""

# Step 3: 安裝依賴套件
Write-Host "[4/8] 安裝 Python 套件依賴..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[錯誤] 套件安裝失敗！" -ForegroundColor Red
    Read-Host "按 Enter 鍵退出"
    exit 1
}
Write-Host "✓ 套件安裝完成" -ForegroundColor Green
Write-Host ""

# Step 4: 檢查 .env 檔案
Write-Host "[5/8] 檢查環境變數設定..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[提示] 找不到 .env 檔案，正在複製 .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✓ .env 檔案已建立" -ForegroundColor Green
        Write-Host "" 
        Write-Host "================================================" -ForegroundColor Magenta
        Write-Host "重要提醒：請編輯 .env 檔案並設定以下內容：" -ForegroundColor Magenta
        Write-Host "  1. DJANGO_SECRET_KEY （設定隨機密鑰）" -ForegroundColor White
        Write-Host "  2. DEBUG=False （生產環境建議設為 False）" -ForegroundColor White
        Write-Host "  3. ALLOWED_HOSTS （設定您的域名或 IP）" -ForegroundColor White
        Write-Host "  4. ADMIN_PASSWORD （設定管理員密碼）" -ForegroundColor White
        Write-Host "================================================" -ForegroundColor Magenta
        Write-Host ""
    } else {
        Write-Host "[警告] 找不到 .env.example，請手動建立 .env 檔案" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ .env 檔案已存在" -ForegroundColor Green
}
Write-Host ""

# Step 5: 執行資料庫遷移
Write-Host "[6/8] 執行資料庫遷移..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "[錯誤] 資料庫遷移失敗！" -ForegroundColor Red
    Read-Host "按 Enter 鍵退出"
    exit 1
}
Write-Host "✓ 資料庫遷移完成" -ForegroundColor Green
Write-Host ""

# Step 6: 編譯翻譯檔案
Write-Host "[7/8] 編譯翻譯檔案..." -ForegroundColor Yellow
if (Test-Path "compile_with_msgfmt.py") {
    python compile_with_msgfmt.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 翻譯檔案編譯完成" -ForegroundColor Green
    } else {
        Write-Host "[警告] 翻譯檔案編譯失敗，但不影響主要功能" -ForegroundColor Yellow
    }
} else {
    Write-Host "[跳過] 找不到 compile_with_msgfmt.py" -ForegroundColor Gray
}
Write-Host ""

# Step 7: 檢查必要目錄
Write-Host "[8/8] 檢查必要目錄..." -ForegroundColor Yellow
$directories = @("data", "data_photo", "static")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✓ 建立目錄: $dir" -ForegroundColor Green
    } else {
        Write-Host "✓ 目錄已存在: $dir" -ForegroundColor Gray
    }
}
Write-Host ""

# 完成
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 確認 .env 檔案已正確設定" -ForegroundColor White
Write-Host "2. 複製 Excel 資料檔案到 data/ 目錄" -ForegroundColor White
Write-Host "3. 複製產品圖片到 data_photo/ 目錄" -ForegroundColor White
Write-Host "4. 執行 'python run_server.py' 啟動伺服器" -ForegroundColor White
Write-Host ""
Write-Host "如需以系統管理員身份執行（使用 Port 80）：" -ForegroundColor Yellow
Write-Host "  以系統管理員身份開啟 PowerShell，然後執行：" -ForegroundColor White
Write-Host "  cd $currentPath" -ForegroundColor Cyan
Write-Host "  python run_server.py" -ForegroundColor Cyan
Write-Host ""

Read-Host "按 Enter 鍵退出"
