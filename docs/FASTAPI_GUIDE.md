# RAGFlow FastAPI 後端使用指南

## 🎯 概述

本 FastAPI 後端服務為聊天代理機器人提供了完整的 RAG (Retrieval-Augmented Generation) 聊天 API 接口，基於 RAGFlow 官方 Python API 實現。

## 🚀 快速開始

### 1. 環境準備

```bash
# 安裝依賴
pip install -r requirements.txt

# 配置 RAGFlow API
# 編輯 config.py 或設置環境變量
export RAGFLOW_API_URL="http://your-ragflow-server"
export RAGFLOW_API_KEY="your-api-key"
```

### 2. 啟動服務

```bash
python3 fastapi_server.py
```

服務啟動後可訪問：
- API 文檔: http://localhost:8000/docs
- ReDoc 文檔: http://localhost:8000/redoc
- 健康檢查: http://localhost:8000/

## 📚 API 接口詳解

### 1. 健康檢查

```http
GET /
```

**回應:**
```json
{
  "service": "RAGFlow Chat API",
  "status": "running",
  "version": "1.0.0",
  "timestamp": "2025-08-02T17:38:36.203421"
}
```

### 2. 獲取數據集列表

```http
GET /datasets
```

**回應:**
```json
[
  {
    "id": "826403366ee311f0bca2c60b36fb4045",
    "name": "憲法與行政法",
    "description": null,
    "document_count": 2,
    "create_time": 1754058387272
  }
]
```

### 3. 發送聊天消息

```http
POST /chat
```

**請求體:**
```json
{
  "question": "什麼是憲法？",
  "dataset_id": "826403366ee311f0bca2c60b36fb4045",
  "session_id": "optional-session-id",
  "user_id": "optional-user-id",
  "quote": true,
  "stream": false
}
```

**回應:**
```json
{
  "success": true,
  "answer": "憲法是國家的根本大法...",
  "sources": [
    {
      "doc_name": "憲法條文.pdf",
      "content": "相關內容片段..."
    }
  ],
  "session_id": "76be56a26f8411f08686c60b36fb4045",
  "chat_id": "76bb1e7e6f8411f0b1e1c60b36fb4045",
  "message": "回答成功",
  "timestamp": "2025-08-02T17:38:36.203421"
}
```

### 4. 獲取活躍會話

```http
GET /sessions
```

**回應:**
```json
[
  {
    "session_id": "76be56a26f8411f08686c60b36fb4045",
    "chat_id": "76bb1e7e6f8411f0b1e1c60b36fb4045",
    "dataset_id": "826403366ee311f0bca2c60b36fb4045",
    "dataset_name": "憲法與行政法",
    "user_id": "demo_user_001",
    "created_at": "2025-08-02T17:38:36.203421",
    "last_used": "2025-08-02T17:40:15.123456"
  }
]
```

### 5. 刪除會話

```http
DELETE /sessions/{session_id}
```

**回應:**
```json
{
  "success": true,
  "message": "會話已刪除"
}
```

## 🤖 聊天代理機器人集成

### Python 客戶端示例

```python
import requests

class ChatAgent:
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_url = api_base_url
        self.session_id = None
        self.dataset_id = None
    
    def initialize(self):
        """初始化：選擇數據集"""
        response = requests.get(f"{self.api_url}/datasets")
        datasets = response.json()
        
        if datasets:
            self.dataset_id = datasets[0]['id']
            print(f"使用數據集: {datasets[0]['name']}")
            return True
        return False
    
    def chat(self, question: str, user_id: str = None):
        """發送聊天消息"""
        payload = {
            "question": question,
            "dataset_id": self.dataset_id,
            "quote": True
        }
        
        if self.session_id:
            payload["session_id"] = self.session_id
        if user_id:
            payload["user_id"] = user_id
        
        response = requests.post(f"{self.api_url}/chat", json=payload)
        result = response.json()
        
        if result.get("success"):
            self.session_id = result["session_id"]  # 保存會話 ID
            return {
                "answer": result["answer"],
                "sources": result["sources"]
            }
        else:
            return {"error": result.get("message", "未知錯誤")}

# 使用示例
agent = ChatAgent()
if agent.initialize():
    result = agent.chat("什麼是憲法？", user_id="user123")
    print(result["answer"])
```

### JavaScript/Node.js 客戶端示例

```javascript
class ChatAgent {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiUrl = apiBaseUrl;
        this.sessionId = null;
        this.datasetId = null;
    }
    
    async initialize() {
        try {
            const response = await fetch(`${this.apiUrl}/datasets`);
            const datasets = await response.json();
            
            if (datasets.length > 0) {
                this.datasetId = datasets[0].id;
                console.log(`使用數據集: ${datasets[0].name}`);
                return true;
            }
            return false;
        } catch (error) {
            console.error('初始化失敗:', error);
            return false;
        }
    }
    
    async chat(question, userId = null) {
        const payload = {
            question: question,
            dataset_id: this.datasetId,
            quote: true
        };
        
        if (this.sessionId) {
            payload.session_id = this.sessionId;
        }
        if (userId) {
            payload.user_id = userId;
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.sessionId = result.session_id;
                return {
                    answer: result.answer,
                    sources: result.sources
                };
            } else {
                return { error: result.message || '未知錯誤' };
            }
        } catch (error) {
            return { error: error.message };
        }
    }
}

// 使用示例
const agent = new ChatAgent();
agent.initialize().then(success => {
    if (success) {
        agent.chat('什麼是憲法？', 'user123').then(result => {
            console.log(result.answer);
        });
    }
});
```

## 🔧 配置選項

### 環境變量

| 變量名 | 描述 | 默認值 |
|--------|------|--------|
| `RAGFLOW_API_URL` | RAGFlow 服務器地址 | `http://192.168.50.123` |
| `RAGFLOW_API_KEY` | RAGFlow API 密鑰 | 配置文件中的值 |

### 服務配置

```python
# fastapi_server.py 中的配置選項
app = FastAPI(
    title="RAGFlow Chat API",
    description="基於 RAGFlow 的智能問答 API 服務",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境中應限制具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐳 Docker 部署

### 使用 Docker Compose (推薦)

```bash
# 啟動服務
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

### 手動 Docker 部署

```bash
# 構建鏡像
docker build -t ragflow-api .

# 運行容器
docker run -d \
  --name ragflow-api \
  -p 8000:8000 \
  -e RAGFLOW_API_URL=http://your-ragflow-server \
  -e RAGFLOW_API_KEY=your-api-key \
  ragflow-api

# 查看日誌
docker logs -f ragflow-api
```

## 🧪 測試和調試

### 運行測試套件

```bash
# 完整 API 測試
python3 test/test_fastapi.py

# 客戶端示例測試
python3 test/api_client_example.py
```

### 調試技巧

1. **查看服務日誌:**
   ```bash
   # 直接運行時的日誌
   python3 fastapi_server.py
   
   # Docker 容器日誌
   docker logs -f ragflow-api
   ```

2. **測試 API 端點:**
   ```bash
   # 健康檢查
   curl http://localhost:8000/
   
   # 獲取數據集
   curl http://localhost:8000/datasets
   
   # 發送聊天消息
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"question":"測試問題","dataset_id":"your-dataset-id"}'
   ```

3. **使用 API 文檔:**
   - 訪問 http://localhost:8000/docs 進行交互式測試
   - 使用 Swagger UI 直接測試所有端點

## 🔒 安全考慮

### 生產環境配置

1. **限制 CORS 來源:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],  # 限制具體域名
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

2. **添加認證中間件:**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   async def verify_token(token: str = Depends(security)):
       # 實現 token 驗證邏輯
       if not verify_jwt_token(token.credentials):
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid token"
           )
   ```

3. **限制請求頻率:**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/chat")
   @limiter.limit("10/minute")  # 每分鐘最多 10 次請求
   async def chat(request: Request, chat_request: ChatRequest):
       # 聊天邏輯
   ```

## 📊 監控和日誌

### 日誌配置

```python
import logging

# 配置日誌格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ragflow_api.log'),
        logging.StreamHandler()
    ]
)
```

### 性能監控

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🤝 貢獻和支持

如有問題或建議，請：
1. 查看 API 文檔: http://localhost:8000/docs
2. 運行測試腳本確認環境配置
3. 檢查 RAGFlow 服務器連接狀態
4. 提交 Issue 或 Pull Request

## 📄 許可證

MIT License