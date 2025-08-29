# 🤖 廣告偵測與替換系統

一個自動偵測網頁廣告並替換為自定義圖片的工具，適用於廣告效果測試、網站分析等用途。

## 🚀 快速開始（新用戶必看）

### 📥 下載與安裝
```bash
# 1. 下載專案
git clone https://github.com/mattyang-1019/ad-detection-replacement-system.git
cd ad-detection-replacement-system

# 2. 安裝 Python 依賴
pip install -r requirements.txt
pip install selenium beautifulsoup4 requests webdriver-manager

# 3. 確保已安裝 Chrome 瀏覽器
```

### ⚡ 30秒開始使用
```bash
# Windows 用戶（推薦）
雙擊執行 setup_and_run.bat

# 或手動執行
python config_manager.py
# 選擇 4️⃣ 修改設定並立即執行
# 輸入目標網址，其他設定可直接按 ENTER 使用預設值
```

### 📸 上傳替換圖片（可選）
```bash
python image_manager_app.py
# 瀏覽器開啟 http://localhost:5001
# 上傳你想要的廣告替換圖片
```

### 💻 系統需求
- **Python 3.8+** 
- **Chrome 瀏覽器**
- **Windows/Mac/Linux** 都支援

---

## 📖 詳細說明

簡潔的兩程式架構：圖片管理 + 廣告替換

## 🎯 核心程式

### 🅰️ 圖片管理系統
**執行檔案：** `image_manager_app.py`
- 📤 上傳廣告替換用的圖片
- 🏷️ 自動重新命名為 `img_寬度x高度.副檔名` 格式
- 🌐 Web 介面管理 (`http://localhost:5001`)

### 🅱️ 設定管理器 ⭐ 
**執行檔案：** `config_manager.py`
- 🔧 互動式設定系統參數
- 💾 自動儲存設定檔
- 🚀 一鍵執行廣告替換

#### 📋 選項說明
- **2️⃣ 修改設定** - 只進行設定，不執行程式，儲存到設定檔後回到主選單
- **3️⃣ 執行廣告替換** - 使用現有設定檔直接執行程式，不修改設定
- **4️⃣ 修改設定並立即執行** - 先設定參數，儲存後立即執行廣告替換
- **5️⃣ 離開** - 結束程式回到命令提示字元

#### 💡 設定技巧
- **快速設定**: 直接按 ENTER 跳過不需要修改的項目
- **保持原值**: 所有設定都會顯示目前值，按 ENTER 即可保持
- **必填項目**: 只有目標網址是必填的，其他都可以跳過

#### 🎯 使用情境
- **第一次使用** → 選 `4️⃣` 設定並執行
- **已設定過，想再執行** → 選 `3️⃣` 直接執行  
- **只想改設定** → 選 `2️⃣` 只修改設定
- **想改設定並測試** → 選 `4️⃣` 修改設定並執行

#### ⚙️ 進階設定說明
- **🎨 按鈕樣式**: 廣告上顯示的關閉/資訊按鈕樣式
  - `cross` - 驚嘆號+叉叉 (推薦)
  - `dots` - 驚嘆號+點點
  - `adchoices` - AdChoices+叉叉
  - `adchoices_dots` - AdChoices+點點
  - `none` - 無按鈕
- **🔄 最大嘗試次數**: 尋找廣告元素的最大嘗試次數 (預設: 50)
- **⏱️ 頁面載入超時**: 等待網頁完全載入的最長時間 (預設: 15秒)
- **⏳ 等待時間**: 操作間的暫停時間，包括截圖前、點擊後等 (預設: 3秒)
- **❌ 連續失敗限制**: 找不到對應尺寸廣告時的重試次數 (預設: 3次)

### 🅲️ 廣告替換執行器  
**執行檔案：** `ad_replacer_runner.py`
- 🔍 自動偵測網頁廣告位置
- 🔄 替換為自定義圖片
- 📸 自動截圖保存到 `screenshots/` 資料夾

## ⚡ 快速開始

### Windows 用戶（推薦）
1. 雙擊執行 `setup_and_run.bat`
2. 等待自動安裝完成
3. 瀏覽器會自動開啟 `http://localhost:5001`
4. 上傳你的廣告圖片

### 所有平台
1. 安裝 Python 3.8+
2. 安裝基礎套件：`pip install -r requirements.txt`
3. 安裝廣告替換套件：`pip install selenium beautifulsoup4 requests webdriver-manager`
4. 執行 `python config_manager.py` 進行設定
5. 開始使用！

## 🚀 使用方法

### 🎯 初次使用流程
```bash
# 步驟 1：上傳廣告替換圖片
python src/image_manager_app.py
# 然後訪問 http://localhost:5001 上傳圖片

# 步驟 2：設定參數並執行廣告替換
python src/config_manager.py
# 設定目標網址等參數，然後執行替換
```

### 🔄 後續使用
```bash
# 如果已有圖片和設定，直接執行
python src/config_manager.py
```

### 🔍 啟用調試模式（推薦）
```bash
python src/config_manager.py
# 選擇「修改設定」→ 在最後選擇「偵測調試模式」→ 輸入 y
```
**調試模式優點：**
- 📊 顯示每個選擇器找到多少個連結
- 🎯 分析頁面上所有廣告元素的詳細資訊  
- 📍 顯示廣告元素的精確位置和尺寸
- ⚠️ 提供詳細的錯誤診斷資訊

## 🎯 參數說明

### image_manager_app.py
```bash
python src/image_manager_app.py [選項]
  --port PORT     埠號 (預設: 5001)
  --host HOST     主機位址 (預設: 0.0.0.0)
  --debug         調試模式
```

### ad_replacer_runner.py  
```bash
python src/ad_replacer_runner.py --url URL [選項]
  --url URL           目標網址 (必填)
  --screenshots NUM   截圖數量 (預設: 10)
  --articles NUM      掃描文章數 (預設: 20)
  --screen NUM        螢幕編號 (預設: 1)
```

## 📁 檔案結構

```
📁 ad-detection-replacement-system/
├── 📄 README.md                    # 主要說明文件
├── 📄 LICENSE                      # 授權條款
├── 📄 requirements.txt             # Python 依賴
├── 📄 setup_and_run.bat           # 快速啟動腳本
│
├── 📁 src/                         # 核心程式碼
│   ├── 📄 config_manager.py       # 🅱️ 設定管理器 ⭐
│   ├── 📄 image_manager_app.py    # 🅰️ 圖片管理系統
│   ├── 📄 ad_replacer_runner.py   # 🅲️ 廣告替換執行器
│   └── 📄 website_template_complete.py  # 廣告替換核心邏輯
│
├── 📁 config/                      # 設定檔案
│   └── 📄 default_config.py       # 預設設定模板
│
├── 📁 templates/                   # 網頁模板
│   └── 📄 single_page_app.html    # 圖片管理介面
│
├── 📁 docs/                        # 文件資料夾
│   └── 📄 使用者自訂範例.md       # 自訂指南
│
└── 📁 data/                        # 資料資料夾
    ├── 📁 replace_image/           # 替換圖片儲存
    ├── 📁 screenshots/             # 截圖結果儲存
    └── 📁 logs/                    # 系統日誌

# 執行時自動生成的檔案（位於專案根目錄）：
# � ad_replacer_config.json      # 使用者設定檔
# 📄 config.py                    # 系統內部設定檔
```

## ⚙️ 設定檔說明

### 📋 **兩層設定架構**

#### **1. 使用者設定檔 (`ad_replacer_config.json`)**
- 🎯 **用途**: 使用者透過 `config_manager.py` 設定的啟動參數
- 🔧 **管理方式**: 互動式設定管理器
- 📝 **內容**: 
  - 🌐 目標網址
  - 📸 截圖數量
  - 📰 掃描文章數
  - � ️ 螢幕編號

#### **2. 系統內部設定檔 (`config.py`)**
- 🎯 **用途**: `website_template_complete.py` 使用的詳細系統設定
- 🔧 **管理方式**: 由 `ad_replacer_runner.py` 基於 `default_config.py` 自動生成
- 📝 **內容**:
  - 🎯 廣告尺寸定義
  - 🖼️ 圖片使用次數
  - ⏱️ 超時設定
  - 📁 資料夾路徑
  - 🔘 按鈕樣式設定

## 💡 進階使用範例

```bash
# 處理 20 張截圖，掃描 50 篇文章
python src/ad_replacer_runner.py --url https://example.com --screenshots 20 --articles 50

# 使用第 2 個螢幕
python src/ad_replacer_runner.py --url https://example.com --screen 2

# 圖片管理系統使用自訂埠號
python src/image_manager_app.py --port 8080

# 啟用調試模式
python src/image_manager_app.py --debug
```

## 🔧 系統需求

### 基本需求
- Python 3.8+
- Chrome 瀏覽器
- ChromeDriver (自動下載)

### Python 套件

#### 基礎套件 (requirements.txt)
```
Flask==2.3.3          # Web 框架
Werkzeug==2.3.7       # WSGI 工具包
Pillow==10.0.1        # 圖片處理
Jinja2==3.1.2         # 模板引擎
MarkupSafe==2.1.3     # 安全標記
itsdangerous==2.1.2   # 安全簽名
click==8.1.7          # 命令列工具
```

#### 廣告替換功能額外需要
```bash
# 安裝廣告替換所需套件
pip install selenium beautifulsoup4 requests webdriver-manager
```
- **Selenium** - 瀏覽器自動化
- **BeautifulSoup4** - HTML 解析
- **Requests** - HTTP 請求
- **webdriver-manager** - 自動管理 ChromeDriver

### 支援格式
- **圖片格式**：PNG, JPG, JPEG, GIF, BMP, WebP
- **檔案大小**：最大 10MB
- **廣告尺寸**：970x90, 728x90, 300x250, 336x280 等

## 🎯 使用場景

### 1. 廣告效果測試
- 測試不同廣告圖片的視覺效果
- 比較廣告在不同網站上的呈現
- 驗證廣告尺寸和位置的適配性

### 2. 網站廣告分析
- 分析競爭對手的廣告佈局
- 研究不同網站的廣告策略
- 收集廣告位置和尺寸資料

### 3. 設計驗證
- 驗證廣告設計在實際網站上的效果
- 測試廣告與網站內容的協調性
- 收集設計反饋和改進建議


## 🛠️ 故障排除

### 常見問題

#### 🔍 **程式找不到文章連結或廣告時**
**第一步：啟用調試模式**
```bash
python src/config_manager.py
# 選擇「修改設定」→「偵測調試模式」→ 輸入 y
```

**根據調試輸出診斷：**
- 如果看到 `使用選擇器 'xxx' 找到 0 個連結` → 需要修改文章連結選擇器
- 如果看到 `找到 0 個符合尺寸的廣告元素` → 需要調整廣告尺寸設定
- 如果看到大量錯誤訊息 → 檢查網站是否需要登入或有反爬蟲機制

#### 🛠️ **系統問題**
- **Chrome 無法啟動**：確保已安裝 Chrome 瀏覽器
- **權限問題**：確保對工作目錄有寫入權限
- **埠號被佔用**：使用 `--port` 參數指定其他埠號
- **圖片上傳失敗**：檢查圖片格式和大小限制
- **虛擬環境問題**：刪除 `image_upload_env` 資料夾後重新執行 `setup_and_run.bat`

### 檢查系統狀態
- 訪問 `http://localhost:5001/api/system-status` 查看系統狀態
- 查看 `data/logs/` 資料夾中的詳細日誌
- 檢查 `data/replace_image/` 和 `data/screenshots/` 資料夾權限

### 效能優化
- 關閉不必要的瀏覽器擴充功能可提高執行速度
- 減少 `--screenshots` 數量可縮短執行時間
- 關閉不必要的瀏覽器擴充功能
- 使用 `--articles` 參數限制掃描範圍

## 📝 更新日誌

- **v3.0** - 整合廣告偵測與替換系統
- **v2.0** - 單頁面圖片管理系統
- **v1.0** - 基礎圖片上傳功能

## 🔧 使用者自訂指南

### 📋 當程式無法偵測到您網站的廣告時

如果程式無法找到或替換您網站的廣告，請按照以下步驟進行自訂：

#### 1. 🔍 **分析您的網站廣告結構**

**步驟 A：使用瀏覽器開發者工具**
1. 在您的目標網站上按 `F12` 開啟開發者工具
2. 點擊左上角的「選擇元素」工具 (或按 `Ctrl+Shift+C`)
3. 點擊網頁上的廣告區域
4. 在開發者工具中查看廣告的 HTML 結構

**步驟 B：記錄廣告特徵**
- 📏 **廣告尺寸**：記錄 `width` 和 `height` 值
- 🏷️ **CSS 類別**：記錄 `class` 屬性值
- 🆔 **元素 ID**：記錄 `id` 屬性值
- 🏗️ **HTML 標籤**：確認是 `<div>`, `<iframe>`, `<ins>` 還是其他標籤

#### 2. 📝 **修改程式碼中的選擇器**

**檔案位置：** `src/website_template_complete.py`

**A. 修改廣告容器選擇器 (第 460 行附近)**
```javascript
// 🔧 找到這行並修改
var adsbygoogle = document.querySelectorAll('ins.adsbygoogle');

// 🔧 改為您網站的廣告選擇器，例如：
var adsbygoogle = document.querySelectorAll('.your-ad-class');
// 或
var adsbygoogle = document.querySelectorAll('#your-ad-id');
// 或
var adsbygoogle = document.querySelectorAll('div[data-ad="true"]');
```

**B. 修改廣告關鍵字 (第 490 行附近)**
```javascript
// 🔧 找到這行並添加您網站的廣告關鍵字
var hasAdKeyword = ['ad', 'advertisement', 'banner', 'google', 'ads'].some(function(keyword) {

// 🔧 改為包含您網站的廣告關鍵字，例如：
var hasAdKeyword = ['ad', 'advertisement', 'banner', 'google', 'ads', 'sponsor', 'promo', 'commercial'].some(function(keyword) {
```

**C. 修改文章連結選擇器 (第 590 行附近)**
```python
# 🔧 找到這個列表並修改
link_selectors = [
    "a[href*='/article/']",  # 一般文章連結
    "a[href*='/news/']",     # 新聞連結
    # ... 其他選擇器
]

# 🔧 添加您網站特有的連結模式，例如：
link_selectors = [
    "a[href*='/article/']",
    "a[href*='/news/']",
    "a.your-article-class",      # 您網站的文章連結類別
    ".post-title a",             # 文章標題內的連結
    "h2 a",                      # 標題標籤內的連結
    "a[href*='/your-path/']",    # 您網站特有的路徑
]
```

**D. 修改全螢幕廣告選擇器 (第 650 行附近)**
```javascript
// 🔧 找到這個陣列並添加您網站的彈出廣告選擇器
var fullscreenAdSelectors = [
    '.overlay',
    '.modal-overlay',
    // ... 其他選擇器
    
    // 🔧 添加您網站的彈出廣告選擇器
    '.your-popup-class',
    '#your-modal-id',
    '[data-popup="true"]',
];
```

#### 3. 🎯 **調整廣告尺寸設定**

**檔案位置：** `config/default_config.py` (第 23 行附近)

```python
# 🔧 修改這個列表以包含您網站的廣告尺寸
TARGET_AD_SIZES = [
    {"width": 970, "height": 90},   # 超級橫幅
    {"width": 986, "height": 106},  # 大型橫幅
    {"width": 728, "height": 90},   # 橫幅廣告
    {"width": 300, "height": 250},  # 中矩形廣告
    {"width": 336, "height": 280},  # 大矩形廣告
    {"width": 320, "height": 50},   # 手機橫幅
    {"width": 160, "height": 600},  # 寬摩天大樓
    {"width": 300, "height": 600},  # 半頁廣告
    
    # 🔧 添加您網站特有的廣告尺寸
    {"width": 您的寬度, "height": 您的高度},
]
```

#### 4. 🧪 **測試和調試**

**🔍 啟用偵測調試模式：**

1. **透過設定管理器啟用：**
   ```bash
   python src/config_manager.py
   # 選擇「修改設定」→ 在最後會看到「偵測調試模式」選項
   # 輸入 y 啟用調試模式
   ```

2. **調試模式功能：**
   - 📊 **選擇器效果分析** - 顯示每個 CSS 選擇器找到多少個連結
   - 🎯 **廣告元素偵測** - 自動分析頁面上所有可能的廣告元素
   - 📍 **精確位置資訊** - 顯示找到的廣告元素尺寸和位置
   - ⚠️ **錯誤診斷** - 顯示處理過程中的詳細錯誤訊息

3. **調試輸出範例：**
   ```
   使用選擇器 'a[href*="/news/"]' 找到 15 個連結
   開始掃描整個網頁尋找 300x250 的廣告...
   找到符合尺寸的廣告元素: 300x250 at 150,200
   === 調試：頁面廣告元素分析 ===
   找到 23 個可能的廣告元素：
   1. 尺寸: 728x90, 位置: (100, 50), 類別: banner-ad
   2. 尺寸: 300x250, 位置: (800, 200), 類別: sidebar-ad
   ```

4. **使用建議：**
   - ✅ **第一次測試新網站時** - 了解網站結構
   - ✅ **程式找不到文章連結時** - 診斷選擇器問題
   - ✅ **程式找不到廣告時** - 分析廣告元素
   - ✅ **想要優化偵測準確度時** - 精細調整參數

#### 5. 📋 **常見網站類型的選擇器範例**

**新聞網站：**
```python
link_selectors = [
    "a[href*='/news/']",
    "a[href*='/article/']", 
    ".headline a",
    ".news-item a",
    "h2 a", "h3 a"
]
```

**部落格網站：**
```python
link_selectors = [
    "a[href*='/blog/']",
    "a[href*='/post/']",
    ".post-title a",
    ".entry-title a",
    "article a"
]
```

**電商網站：**
```python
link_selectors = [
    "a[href*='/product/']",
    "a[href*='/item/']",
    ".product-link",
    ".item-title a"
]
```

**論壇網站：**
```python
link_selectors = [
    "a[href*='/thread/']",
    "a[href*='/topic/']",
    ".thread-title a",
    ".topic-link"
]
```

#### 6. 💡 **進階技巧**

**A. 使用更精確的選擇器：**
```javascript
// 使用屬性選擇器
document.querySelectorAll('[data-ad-client]')
document.querySelectorAll('[data-ad-slot]')

// 使用複合選擇器
document.querySelectorAll('div.ad-container iframe')
document.querySelectorAll('.sidebar .advertisement')
```

**B. 處理動態載入的廣告：**
如果廣告是動態載入的，可能需要增加等待時間：
```python
# 在 src/website_template_complete.py 中找到並修改等待時間
time.sleep(5)  # 增加等待時間
```

**C. 處理多種廣告格式：**
```javascript
// 同時檢查多種廣告容器
var ads = [];
ads = ads.concat(Array.from(document.querySelectorAll('ins.adsbygoogle')));
ads = ads.concat(Array.from(document.querySelectorAll('.your-ad-class')));
ads = ads.concat(Array.from(document.querySelectorAll('iframe[src*="ads"]')));
```

### 🆘 **需要協助？**

如果您在自訂過程中遇到困難：

1. **啟用調試模式** 查看程式偵測到的元素
2. **檢查瀏覽器控制台** 是否有 JavaScript 錯誤
3. **逐步測試** 先測試簡單的選擇器，再逐漸複雜化
4. **備份原始檔案** 在修改前先備份 `src/website_template_complete.py`

## 🔒 注意事項

- 請遵守目標網站的使用條款
- 僅用於合法的測試和研究目的
- 注意保護個人隱私和資料安全
- 建議在測試環境中使用

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 如何貢獻
1. Fork 這個專案
2. 創建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 📄 授權

本專案採用 MIT 授權條款 - 查看 [LICENSE](LICENSE) 檔案了解詳情

## ⭐ 支持專案

如果這個專案對你有幫助，請給它一個 ⭐！

---

💡 **提示**：首次使用建議先上傳一些測試圖片，然後選擇一個簡單的網站進行測試！