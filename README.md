Kingsteel Auction - Django scaffold

快速啟動：

1. 建立虛擬環境並安裝依賴：

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. 設定環境變數：複製 `.env.example` 並修改

3. 執行開發伺服器：

```bash
python manage.py migrate
python manage.py runserver
```

備註：目前資料以 Excel/CSV 為來源，位於 `data/` 資料夾。