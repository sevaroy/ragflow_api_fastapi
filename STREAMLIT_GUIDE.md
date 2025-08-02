# RAGFlow Streamlit 前端使用指南

## 🎯 概述

本 Streamlit 前端應用提供了一個美觀、易用的 Web 界面，與 FastAPI 後端進行交互，實現完整的 RAG 聊天機器人功能。

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝依賴
pip install -r requirements.txt

# 確認 Streamlit 安裝
streamlit --version
```

### 2. 啟動應用

**方法 1: 全棧啟動 (推薦)**
```bash
python3 run_full_stack.py
```

**方法 2: 分別啟動**
```bash
# 終端 1: 啟動 FastAPI 後端
python3 fastapi_server.py

# 終端 2: 啟動 Streamlit 前端
streamlit run streamlit_app.py
```

### 3. 訪問應用

- **Streamlit 前端**: http://localhost:8501
- **FastAPI 後端**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

## 🎨 界面功能詳解

### 主界面布局

```
┌─────────────────────────────────────────────────────────────┐
│                    🤖 RAGFlow 聊天機器人                      │
│                   基於 RAGFlow 的智能問答系統                  │
├─────────────────┬───────────────────────────────────────────┤
│   ⚙️ 配置        │              💬 聊天對話                   │
│                 │                                           │
│ 🔗 API 連接     │  ┌─────────────────────────────────────┐   │
│ ✅ 已連接       │  │ 👤 你: 什麼是憲法？                   │   │
│                 │  └─────────────────────────────────────┘   │
│ 📚 數據集選擇   │  ┌─────────────────────────────────────┐   │
│ 憲法與行政法    │  │ 🤖 RAGFlow: 憲法是國家的根本大法...   │   │
│                 │  │ 📖 參考來源 (3 個)                   │   │
│ 💬 會話管理     │  └─────────────────────────────────────┘   │
│ 當前會話: abc.. │                                           │
│ [🆕新會話]      │  ┌─────────────────────────────────────┐   │
│ [🗑️清除歷史]    │  │ 輸入您的問題: _________________ [發送] │   │
│                 │  └─────────────────────────────────────┘   │
│ 📊 活躍會話     │  💡 快速問題: [按鈕1] [按鈕2] [按鈕3]      │
└─────────────────┴───────────────────────────────────────────┘
```

### 側邊欄功能

#### 1. API 連接管理
- **連接狀態**: 實時顯示 API 連接狀態
- **地址配置**: 可修改 FastAPI 後端地址
- **連接測試**: 一鍵測試 API 連接

#### 2. 數據集選擇
- **動態載入**: 自動從 API 獲取可用數據集
- **詳細信息**: 顯示數據集名稱、文件數量、ID
- **即時切換**: 選擇不同數據集進行問答

#### 3. 會話管理
- **會話狀態**: 顯示當前會話 ID
- **新會話**: 開始全新的對話會話
- **清除歷史**: 清空當前聊天記錄
- **活躍會話**: 查看所有活躍的會話

### 主聊天區功能

#### 1. 消息顯示
- **用戶消息**: 藍色邊框，右對齊風格
- **機器人回答**: 紫色邊框，左對齊風格
- **時間戳**: 每條消息包含時間信息
- **滾動顯示**: 自動滾動到最新消息

#### 2. 來源引用
- **展開式顯示**: 點擊展開查看詳細來源
- **文檔信息**: 顯示來源文檔名稱
- **內容片段**: 顯示相關內容摘要
- **多來源支持**: 支持多個參考來源

#### 3. 輸入和交互
- **文本輸入**: 支持多行文本輸入
- **快速發送**: Enter 鍵或按鈕發送
- **快速問題**: 預設常用問題按鈕
- **實時反饋**: 發送時顯示處理狀態

## 🔧 高級功能

### 1. 會話持久化

```python
# 會話狀態管理
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
```

### 2. 錯誤處理

```python
# API 錯誤處理
try:
    response = client.send_chat_message(question, dataset_id)
    if response['success']:
        # 處理成功回應
    else:
        st.error(f"❌ 請求失敗: {response['error']}")
except Exception as e:
    st.error(f"❌ 連接錯誤: {str(e)}")
```

### 3. 狀態監控

```python
# API 健康檢查
def check_api_connection():
    health_result = client.check_api_health()
    if health_result['success']:
        st.success("✅ API 連接正常")
    else:
        st.error(f"❌ API 連接失敗: {health_result['error']}")
```

## 🎨 自定義樣式

### CSS 樣式定制

```python
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)
```

### 主題配置

**`.streamlit/config.toml`:**
```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "0.0.0.0"
```

## 📊 功能擴展

### 1. 添加新的快速問題

```python
quick_questions = [
    "這個數據集包含什麼內容？",
    "請簡單介紹主要概念",
    "有什麼重要信息？",
    "你的自定義問題",  # 添加新問題
]
```

### 2. 自定義 API 客戶端

```python
class CustomRAGClient(StreamlitRAGClient):
    def __init__(self, api_base_url: str):
        super().__init__(api_base_url)
        # 添加自定義配置
    
    def custom_chat_method(self, question: str):
        # 實現自定義聊天邏輯
        pass
```

### 3. 添加新的界面組件

```python
# 添加文件上傳功能
uploaded_file = st.file_uploader("上傳文檔", type=['pdf', 'txt'])

# 添加圖表顯示
import plotly.express as px
fig = px.bar(data, x='category', y='count')
st.plotly_chart(fig)

# 添加數據表格
st.dataframe(session_data)
```

## 🧪 測試和調試

### 1. 運行測試

```bash
# 基本功能測試
python3 test/test_streamlit.py

# 手動測試步驟
# 1. 啟動應用
# 2. 檢查 API 連接
# 3. 選擇數據集
# 4. 發送測試消息
# 5. 驗證回答和來源
```

### 2. 調試技巧

**查看 Streamlit 狀態:**
```python
# 在應用中添加調試信息
st.write("Debug Info:", st.session_state)
```

**API 請求調試:**
```python
# 在客戶端類中添加日誌
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_chat_message(self, question: str):
    logger.debug(f"發送問題: {question}")
    # ... 其他代碼
```

**性能監控:**
```python
import time

@st.cache_data
def cached_api_call(question: str):
    start_time = time.time()
    result = api_call(question)
    end_time = time.time()
    st.write(f"API 調用耗時: {end_time - start_time:.2f}s")
    return result
```

## 🚀 部署和優化

### 1. 生產環境部署

**使用 Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
```

**使用 Docker Compose:**
```yaml
version: '3.8'
services:
  streamlit-frontend:
    build: .
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://fastapi-backend:8000
    depends_on:
      - fastapi-backend
```

### 2. 性能優化

**緩存優化:**
```python
@st.cache_data(ttl=300)  # 5分鐘緩存
def get_datasets():
    return client.get_datasets()

@st.cache_resource
def init_client():
    return StreamlitRAGClient()
```

**會話狀態優化:**
```python
# 限制聊天歷史長度
MAX_HISTORY = 50
if len(st.session_state.chat_history) > MAX_HISTORY:
    st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY:]
```

### 3. 安全考慮

**輸入驗證:**
```python
def validate_input(question: str) -> bool:
    if not question or len(question.strip()) == 0:
        return False
    if len(question) > 1000:  # 限制長度
        return False
    return True
```

**API 密鑰保護:**
```python
# 使用環境變量
import os
API_KEY = os.getenv('RAGFLOW_API_KEY')
if not API_KEY:
    st.error("請設置 RAGFLOW_API_KEY 環境變量")
    st.stop()
```

## 📱 移動端適配

### 響應式設計

```python
# 檢測設備類型
def is_mobile():
    return st.session_state.get('mobile', False)

# 移動端布局調整
if is_mobile():
    # 使用單列布局
    st.write("移動端界面")
else:
    # 使用多列布局
    col1, col2 = st.columns([1, 3])
```

### 觸摸優化

```css
/* 在自定義 CSS 中添加 */
.stButton > button {
    min-height: 44px;  /* 觸摸友好的按鈕大小 */
    font-size: 16px;
}

.stTextInput > div > div > input {
    font-size: 16px;  /* 防止 iOS 縮放 */
}
```

## 🤝 貢獻指南

### 1. 開發環境設置

```bash
# 克隆項目
git clone <repository-url>
cd ragflow-chatbot

# 安裝開發依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果有開發依賴

# 啟動開發服務器
streamlit run streamlit_app.py --server.runOnSave true
```

### 2. 代碼規範

- 使用 Python 類型提示
- 遵循 PEP 8 代碼風格
- 添加適當的文檔字符串
- 編寫單元測試

### 3. 提交流程

1. Fork 項目
2. 創建功能分支
3. 實現功能並測試
4. 提交 Pull Request

## 📄 許可證

MIT License

---

**最後更新**: 2025年8月2日  
**版本**: 1.0.0  
**維護者**: RAGFlow Team