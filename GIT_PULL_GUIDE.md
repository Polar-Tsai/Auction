# 🔄 虛擬機 Git Pull 教學

## 📥 如何在虛擬機上拉取最新代碼

您已經從 GitHub clone 專案到虛擬機了，現在只需要定期 pull 最新更新即可。

---

## 🚀 快速指令（只需這一行）

打開 PowerShell 或 Git Bash，進入專案目錄後執行：

```bash
git pull
```

就這麼簡單！✅

---

## 📋 完整步驟

### 1️⃣ 開啟終端機
- **方法 A**: 在專案資料夾按住 **Shift + 右鍵** → 選擇「在終端機中開啟」
- **方法 B**: 開啟 PowerShell，然後 `cd` 到專案目錄：
  ```powershell
  cd C:\AuctionWebsite\ActionWebsite
  ```

### 2️⃣ 拉取最新代碼
```bash
git pull
```

### 3️⃣ 檢查更新內容
```bash
git log -3
```
這會顯示最近 3 次的提交記錄。

---

## 🔄 完整的更新流程（建議）

每次要更新虛擬機上的代碼時，按照以下步驟：

```powershell
# 1. 進入專案目錄
cd C:\AuctionWebsite\ActionWebsite

# 2. 停止伺服器（如果正在運行）
# 按 Ctrl + C 停止，或關閉運行中的 PowerShell 視窗

# 3. 拉取最新代碼
git pull

# 4. 安裝新增的套件依賴（如果 requirements.txt 有更新）
pip install -r requirements.txt

# 5. 執行資料庫遷移（如果有新的資料庫變更）
python manage.py migrate

# 6. 編譯翻譯檔案（如果有翻譯更新）
python compile_with_msgfmt.py

# 7. 重新啟動伺服器
python run_server.py
```

---

## ⚡ 一鍵更新腳本（推薦使用）

為了方便，您可以建立一個更新腳本：

### 建立 `update.ps1`：
```powershell
Write-Host "開始更新拍賣網站..." -ForegroundColor Cyan

# 拉取最新代碼
Write-Host "[1/4] 拉取最新代碼..." -ForegroundColor Yellow
git pull

# 更新套件
Write-Host "[2/4] 更新 Python 套件..." -ForegroundColor Yellow
pip install -r requirements.txt

# 資料庫遷移
Write-Host "[3/4] 執行資料庫遷移..." -ForegroundColor Yellow
python manage.py migrate

# 編譯翻譯
Write-Host "[4/4] 編譯翻譯檔案..." -ForegroundColor Yellow
python compile_with_msgfmt.py

Write-Host "✅ 更新完成！" -ForegroundColor Green
Write-Host "請重新啟動伺服器：python run_server.py" -ForegroundColor Cyan

Read-Host "按 Enter 鍵退出"
```

### 使用方式：
```powershell
.\update.ps1
```

---

## ❓ 常見問題

### Q1: 出現「Your local changes would be overwritten」錯誤？
**原因**：虛擬機上有本地修改的檔案與遠端衝突。

**解決方法**：
```bash
# 方法 A: 保留遠端版本（放棄本地修改）
git reset --hard HEAD
git pull

# 方法 B: 暫存本地修改
git stash
git pull
git stash pop  # 如果需要恢復本地修改
```

### Q2: Pull 後發現有問題，想要回到之前的版本？
```bash
# 查看提交歷史
git log --oneline

# 回到指定版本（複製 commit hash）
git reset --hard <commit-hash>
```

### Q3: 如何查看本地與遠端的差異？
```bash
# 查看遠端有哪些新更新
git fetch
git log HEAD..origin/main

# 查看具體差異
git diff HEAD origin/main
```

---

## 📌 重要提醒

### ⚠️ 不要修改虛擬機上的代碼
- 所有代碼修改應該在**開發機**上完成
- 虛擬機只負責**拉取和運行**
- 這樣可以避免版本衝突問題

### 🔄 更新頻率建議
- **有新功能時**：立即 pull
- **修復 bug**：立即 pull
- **定期檢查**：每週至少 pull 一次

### 📝 建議工作流程
1. 在開發機上修改代碼
2. `git commit` 提交變更
3. `git push` 推送到 GitHub
4. 在虛擬機上 `git pull` 拉取更新
5. 重新啟動伺服器

---

## ✅ 檢查清單

部署後第一次 pull 更新時：
- [ ] 確認已經 clone 專案到虛擬機
- [ ] 執行 `git pull` 拉取最新代碼
- [ ] 確認拉取成功（顯示「Already up to date」或更新訊息）
- [ ] 執行 `pip install -r requirements.txt`
- [ ] 執行 `python manage.py migrate`
- [ ] 執行 `python compile_with_msgfmt.py`
- [ ] 重新啟動伺服器

---

## 🆘 需要協助？

如果遇到問題：
1. 檢查錯誤訊息
2. 確認網路連線正常
3. 確認 Git 已正確安裝
4. 參考上方的常見問題解答
