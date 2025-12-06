# CWA Weather Data Crawler with SQLite Database

## 專案說明
這個專案從中央氣象局（CWA）Open Data API 抓取天氣預報資料，並將資料儲存到 SQLite 資料庫中。

## 檔案說明

### 1. `crawler.py`
主程式，負責：
- 從 CWA API 抓取天氣預報資料
- 解析 JSON 資料
- 將資料儲存到 SQLite 資料庫
- 顯示資料統計

### 2. `query_db.py`
資料庫查詢工具，提供多種查詢功能

### 3. `sqlitedata.db`
SQLite 資料庫檔案（執行 crawler.py 後自動建立）

### 4. `streamlit_app.py` ✨ NEW
Streamlit 網頁應用程式，提供互動式視覺化介面：
- 🗺️ **台灣溫度地圖**：視覺化顯示各地區溫度分布（置於頂部）
- 🎯 地區下拉選單篩選
- 📊 統計資訊展示（5個關鍵指標）
- 📈 溫度趨勢圖表（互動式折線圖）
- 📋 資料表格顯示與下載
- 📅 日期選擇器（地圖用）

## 資料庫結構

### 資料表 1: `weather_forecast`
儲存天氣預報資料

| 欄位名稱 | 資料型態 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵（自動遞增）|
| location | TEXT | 地區名稱（如：北部地區、中部地區等）|
| forecast_date | DATE | 預報日期 |
| max_temp | INTEGER | 最高溫度（°C）|
| min_temp | INTEGER | 最低溫度（°C）|
| fetched_at | TIMESTAMP | 資料抓取時間 |

**唯一性限制**: (location, forecast_date, fetched_at) 的組合必須唯一

### 資料表 2: `fetch_log`
記錄資料抓取歷史

| 欄位名稱 | 資料型態 | 說明 |
|---------|---------|------|
| id | INTEGER | 主鍵（自動遞增）|
| fetch_time | TIMESTAMP | 抓取時間 |
| records_inserted | INTEGER | 成功插入的記錄數 |
| status | TEXT | 狀態（SUCCESS/FAILED/ERROR）|

## 使用方式

### 執行爬蟲程式
```bash
python crawler.py
```

這個指令會：
1. 初始化資料庫（如果不存在）
2. 從 CWA API 抓取資料
3. 顯示資料表格
4. 將資料儲存到資料庫
5. 顯示資料庫統計資訊

### 查詢資料庫

#### 顯示統計資訊（預設）
```bash
python query_db.py
# 或
python query_db.py stats
```

#### 顯示所有記錄
```bash
python query_db.py all
```

#### 顯示抓取歷史
```bash
python query_db.py log
```

#### 查詢特定地區
```bash
python query_db.py location 北部地區
python query_db.py location 中部地區
python query_db.py location 南部地區
```

## 支援的地區
- 北部地區
- 中部地區
- 南部地區
- 東北部地區
- 東部地區
- 東南部地區

## 資料來源
中央氣象局開放資料平臺
- API: F-A0010-001 (農業氣象預報-農業氣象預報資料)
- URL: https://opendata.cwa.gov.tw/

### 啟動網頁介面（Streamlit） ✨ NEW

#### 安裝依賴
```bash
pip install -r requirements.txt
```

或手動安裝：
```bash
pip install streamlit pandas plotly requests
```

#### 執行網頁應用程式
```bash
streamlit run streamlit_app.py
```

這個指令會：
1. 啟動 Streamlit 網頁伺服器（預設 port 8501）
2. 自動在瀏覽器開啟應用程式
3. 提供互動式視覺化介面

**網頁功能：**
- 🗺️ **台灣溫度地圖**：互動式地圖顯示各地區溫度分布（NEW! 置於頂部）
  - 標記大小：反映平均溫度（越大越熱）
  - 顏色梯度：紅色（熱）→ 黃色（溫和）→ 藍色（冷）
  - Hover 資訊：顯示最高/最低/平均溫度
  - 日期選擇：查看不同日期的預報
- 🎯 **地區選擇器**：下拉選單選擇特定地區或查看全部
- 📊 **統計摘要**：顯示平均溫度、最高/最低溫等指標
- 📈 **溫度趨勢圖**：互動式折線圖顯示最高/最低溫變化
- 📋 **資料表格**：可排序的詳細預報資料
- 📥 **資料下載**：匯出 CSV 格式
- 🕐 **更新時間**：顯示資料最後更新時間

#### 更改 Port（選用）
```bash
streamlit run streamlit_app.py --server.port 8502
```

#### 疑難排解
**問題：Database file not found**
```bash
# 解決方案：先執行爬蟲程式建立資料庫
python crawler.py
```

**問題：Port 8501 already in use**
```bash
# 解決方案：使用不同的 port
streamlit run streamlit_app.py --server.port 8502
```

## 依賴套件

### 核心套件
```
requests          # HTTP 請求
sqlite3           # Python 內建
json              # Python 內建
datetime          # Python 內建
```

### 網頁介面套件（Streamlit）
```
streamlit>=1.29.0 # 網頁框架
pandas>=2.0.0     # 資料處理
plotly>=5.18.0    # 互動式圖表
```

## 安裝依賴

### 快速安裝（推薦）
```bash
pip install -r requirements.txt
```

### 最小安裝（僅爬蟲功能）
```bash
pip install requests
```

## 範例輸出

### crawler.py 執行結果
```
✓ Database 'sqlitedata.db' initialized successfully

🌐 Fetching data from CWA API...
✓ Extracted 42 records

📊 Temperature Forecast:
Location   Date         MaxT   MinT  
----------------------------------------
北部地區       2025-12-06   24     15    
中部地區       2025-12-06   26     16    
...

💾 Saving to database...
✓ Successfully saved 42 records to database

📊 Database Statistics:
   Total records: 42
   Latest fetch: 2025-12-06 15:57:01
   Locations: 北部地區, 中部地區, 南部地區, 東北部地區, 東部地區, 東南部地區

✅ Process completed!
```

### query_db.py 統計資訊
```
📊 DATABASE STATISTICS
Total Records: 84
Locations: 6
Forecast Date Range: 2025-12-06 to 2025-12-12
Total Fetches: 2

📈 Average Temperatures by Location:
Location     Avg MaxT   Avg MinT  
----------------------------------------
南部地區         27.9       18.4      
中部地區         27.3       16.6      
```

## 注意事項
1. 每次執行 `crawler.py` 都會插入新的資料記錄
2. 相同的 (location, forecast_date, fetched_at) 組合會被視為重複
3. 資料庫會自動記錄每次抓取的時間和狀態
4. 可以透過 `fetched_at` 欄位追蹤資料的歷史版本

## 授權資訊
本程式使用中央氣象局開放資料，請遵守其使用條款。
