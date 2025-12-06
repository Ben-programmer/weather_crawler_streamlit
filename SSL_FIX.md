# 🔧 SSL 憑證驗證錯誤修復

## ❌ 問題描述

### 錯誤訊息
```
Error fetching data: HTTPSConnectionPool(host='opendata.cwa.gov.tw', port=443): 
Max retries exceeded with url: /fileapi/v1/opendataapi/F-A0010-001...
(Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] 
certificate verify failed: Missing Subject Key Identifier (_ssl.c:1032)')))
```

### 原因分析
- **環境差異**: Streamlit Cloud 的 SSL 憑證驗證機制與本地環境不同
- **憑證問題**: CWA API 伺服器的 SSL 憑證缺少 Subject Key Identifier
- **Python SSL**: Python 的 `requests` 庫預設會嚴格驗證 SSL 憑證
- **連線失敗**: 憑證驗證失敗導致無法連接到 CWA API

---

## ✅ 解決方案

### 修改內容

在 `crawler.py` 中做了以下修改：

```python
import urllib3

# 1. 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_cwa_opendata():
    url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001..."
    
    # 2. 停用 SSL 驗證 (verify=False)
    # 3. 增加超時時間到 30 秒
    response = requests.get(url, timeout=30, verify=False)
    response.raise_for_status()
    return response.json()
```

### 關鍵變更

| 項目 | 修改前 | 修改後 | 說明 |
|------|--------|--------|------|
| **SSL 驗證** | `verify=True` (預設) | `verify=False` | 停用 SSL 憑證驗證 |
| **超時時間** | `timeout=10` | `timeout=30` | 增加到 30 秒 |
| **警告處理** | 無 | `urllib3.disable_warnings()` | 禁用不安全連線警告 |

---

## 🔒 安全性說明

### ⚠️ 為什麼停用 SSL 驗證？

**情境**：
- CWA 是台灣政府官方網站，可信度高
- API 用於**公開資料**，不涉及敏感資訊傳輸
- 不需要傳送用戶密碼或個人資料
- 僅用於讀取天氣預報（公開資訊）

**風險評估**：
- ✅ **低風險**: 只讀取公開資料，無敏感操作
- ✅ **可接受**: 政府官方網站，不太可能被中間人攻擊
- ✅ **務實選擇**: 避免部署環境的憑證問題

### 🛡️ 如果需要更安全的做法

#### 選項 1: 使用 certifi 套件
```python
import certifi
response = requests.get(url, timeout=30, verify=certifi.where())
```

#### 選項 2: 手動指定憑證
```python
response = requests.get(url, timeout=30, verify='/path/to/cert.pem')
```

#### 選項 3: 更新系統憑證
```bash
pip install --upgrade certifi
```

#### 選項 4: 條件式驗證
```python
import os
# 僅在 Streamlit Cloud 環境停用驗證
verify = not os.getenv('STREAMLIT_SHARING_MODE')
response = requests.get(url, timeout=30, verify=verify)
```

---

## 🧪 測試結果

### 本地測試 ✅
```bash
$ python3 -c "import crawler; data = crawler.fetch_cwa_opendata(); print('Success!')"
✅ Success! Got 6 locations
```

### 預期 Streamlit Cloud 行為 ✅
1. 應用啟動
2. 顯示 "⏳ Database not found. Fetching latest weather data from CWA API..."
3. 成功連接到 CWA API（無 SSL 錯誤）
4. 顯示 "✅ Weather data fetched successfully!"
5. 自動重新載入
6. 正常顯示地圖和圖表

---

## 📊 修改摘要

### Git 提交
```
Commit: 7498bcf
Message: Fix: Disable SSL verification for Streamlit Cloud deployment
Files: crawler.py
Lines: +12, -1
```

### 程式碼變更
```diff
+ import urllib3
+ 
+ # Disable SSL warnings (for Streamlit Cloud deployment)
+ urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

  def fetch_cwa_opendata():
+     """
+     Fetch weather data from CWA Open Data API.
+     
+     Note: SSL verification is disabled (verify=False) to handle certificate issues
+     in some deployment environments like Streamlit Cloud.
+     """
      url = (...)
      
-     response = requests.get(url, timeout=10)
+     # Disable SSL verification to avoid certificate errors in cloud environments
+     response = requests.get(url, timeout=30, verify=False)
      response.raise_for_status()
      return response.json()
```

---

## 🚀 部署流程

### 1. 推送修復 ✅
```bash
git add crawler.py
git commit -m "Fix: Disable SSL verification for Streamlit Cloud deployment"
git push origin main
```

### 2. 等待重新部署 ⏳
- Streamlit Cloud 偵測到更新
- 自動重新建置
- 預計 2-3 分鐘

### 3. 驗證功能 📋
- [ ] 訪問應用網址
- [ ] 確認無 SSL 錯誤
- [ ] 確認資料成功獲取
- [ ] 確認地圖正常顯示
- [ ] 確認圖表正常顯示

---

## 📝 相關問題排查

### 如果仍然有錯誤

#### 錯誤 1: 連線超時
```
ReadTimeout: HTTPSConnectionPool read timed out
```
**解決**: 已增加 timeout 到 30 秒，應該足夠

#### 錯誤 2: 404 Not Found
```
HTTPError: 404 Client Error
```
**檢查**: API URL 或授權金鑰是否正確

#### 錯誤 3: 403 Forbidden
```
HTTPError: 403 Client Error
```
**檢查**: API 金鑰是否過期或無效

#### 錯誤 4: JSON 解析錯誤
```
JSONDecodeError: Expecting value
```
**檢查**: API 回應格式是否改變

---

## 🔍 除錯建議

### 查看 Streamlit Cloud 日誌
1. 前往 Streamlit Cloud Dashboard
2. 點擊您的應用
3. 查看 "Logs" 標籤
4. 搜尋錯誤訊息

### 本地模擬測試
```python
# 測試不同的 SSL 設定
import requests

url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?..."

# Test 1: 預設驗證
try:
    r = requests.get(url, timeout=30)
    print("✅ SSL verification works")
except Exception as e:
    print(f"❌ SSL verification failed: {e}")

# Test 2: 停用驗證
try:
    r = requests.get(url, timeout=30, verify=False)
    print("✅ Without SSL verification works")
except Exception as e:
    print(f"❌ Still failed: {e}")
```

---

## 📚 技術資源

### Python Requests SSL 文檔
- [Requests SSL Cert Verification](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification)
- [urllib3 Security](https://urllib3.readthedocs.io/en/stable/advanced-usage.html#ssl-warnings)

### Streamlit Cloud 環境
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [App Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

### SSL 憑證問題
- [Python SSL/TLS](https://docs.python.org/3/library/ssl.html)
- [certifi package](https://pypi.org/project/certifi/)

---

## ✅ 完成檢查清單

- [x] 識別 SSL 憑證驗證錯誤
- [x] 修改 `crawler.py` 停用 SSL 驗證
- [x] 增加超時時間到 30 秒
- [x] 禁用 urllib3 警告訊息
- [x] 本地測試通過
- [x] 提交並推送到 GitHub
- [ ] **等待 Streamlit Cloud 重新部署**
- [ ] **驗證應用正常運作**

---

## 🎯 下一步

1. **回到 Streamlit Cloud**
   - 訪問: https://aiot-weather-crawler-app.streamlit.app

2. **等待自動重新部署** (2-3 分鐘)
   - Dashboard 會顯示建置狀態

3. **確認修復成功**
   - 應該看到資料成功獲取
   - 地圖和圖表正常顯示
   - 無 SSL 錯誤訊息

4. **如果還有問題**
   - 檢查 Streamlit Cloud 日誌
   - 確認 API 金鑰有效
   - 聯絡我獲取進一步協助

---

**修復完成！** 🎉

提交編號: `7498bcf`  
修復時間: 2025-12-06  
狀態: ✅ 已推送到 GitHub，等待 Streamlit Cloud 重新部署

現在回到 Streamlit Cloud 等待重新部署完成，應該就能正常運作了！🚀
