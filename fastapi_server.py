#!/usr/bin/env python3
"""
RAGFlow FastAPI 後端服務
為聊天代理機器人提供 RAG 聊天 API 接口
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import time
import asyncio
from datetime import datetime
import logging

# 導入 RAGFlow 客戶端
from ragflow_chatbot import RAGFlowOfficialClient

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title="RAGFlow Chat API",
    description="基於 RAGFlow 的智能問答 API 服務",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境中應該限制具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局變量
ragflow_client = RAGFlowOfficialClient()
active_sessions = {}  # 存儲活躍的聊天會話

# Pydantic 模型
class DatasetInfo(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    document_count: int = 0
    create_time: Optional[int] = None

class ChatRequest(BaseModel):
    question: str = Field(..., description="用戶問題")
    dataset_id: str = Field(..., description="數據集 ID")
    session_id: Optional[str] = Field(None, description="會話 ID，如果不提供則創建新會話")
    user_id: Optional[str] = Field(None, description="用戶 ID")
    quote: bool = Field(True, description="是否顯示引用來源")
    stream: bool = Field(False, description="是否流式回應")

class ChatResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Dict[str, Any]] = []
    session_id: str
    chat_id: str
    message: str
    timestamp: datetime

class SessionInfo(BaseModel):
    session_id: str
    chat_id: str
    dataset_id: str
    dataset_name: str
    user_id: Optional[str]
    created_at: datetime
    last_used: datetime

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    timestamp: datetime

# 會話管理類
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, dataset_id: str, dataset_name: str, user_id: str = None) -> Dict[str, Any]:
        """創建新的聊天會話"""
        try:
            # 創建聊天助手
            chat_name = f"API聊天機器人_{uuid.uuid4().hex[:8]}"
            chat_result = ragflow_client.create_chat(
                name=chat_name,
                dataset_ids=[dataset_id]
            )
            
            if not chat_result['success']:
                raise Exception(f"創建聊天助手失敗: {chat_result['message']}")
            
            chat_id = chat_result['data']['id']
            
            # 創建會話
            session_result = ragflow_client.create_session(chat_id, user_id)
            
            if not session_result['success']:
                raise Exception(f"創建會話失敗: {session_result['message']}")
            
            session_id = session_result['data']['id']
            
            # 存儲會話信息
            session_info = {
                'session_id': session_id,
                'chat_id': chat_id,
                'dataset_id': dataset_id,
                'dataset_name': dataset_name,
                'user_id': user_id,
                'created_at': datetime.now(),
                'last_used': datetime.now()
            }
            
            self.sessions[session_id] = session_info
            
            logger.info(f"創建會話成功: {session_id}, 聊天助手: {chat_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'chat_id': chat_id,
                'message': '會話創建成功'
            }
            
        except Exception as e:
            logger.error(f"創建會話失敗: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """獲取會話信息"""
        return self.sessions.get(session_id)
    
    def update_session_usage(self, session_id: str):
        """更新會話使用時間"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_used'] = datetime.now()
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理舊會話"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_info in self.sessions.items():
            age = (current_time - session_info['last_used']).total_seconds() / 3600
            if age > max_age_hours:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"清理過期會話: {session_id}")
        
        return len(expired_sessions)

# 創建會話管理器
session_manager = SessionManager()

# API 端點
@app.get("/", summary="健康檢查")
async def root():
    """API 健康檢查"""
    return {
        "service": "RAGFlow Chat API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now()
    }

@app.get("/datasets", response_model=List[DatasetInfo], summary="獲取數據集列表")
async def get_datasets():
    """獲取所有可用的數據集"""
    try:
        result = ragflow_client.list_datasets()
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result['message'])
        
        datasets = []
        for dataset in result['data']:
            datasets.append(DatasetInfo(
                id=dataset.get('id', ''),
                name=dataset.get('name', 'Unknown'),
                description=dataset.get('description'),
                document_count=dataset.get('document_count', 0),
                create_time=dataset.get('create_time')
            ))
        
        return datasets
        
    except Exception as e:
        logger.error(f"獲取數據集失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse, summary="發送聊天消息")
async def chat(request: ChatRequest):
    """發送聊天消息並獲取回答"""
    try:
        session_id = request.session_id
        
        # 如果沒有提供 session_id，創建新會話
        if not session_id:
            # 首先獲取數據集信息
            datasets_result = ragflow_client.list_datasets()
            if not datasets_result['success']:
                raise HTTPException(status_code=500, detail="無法獲取數據集信息")
            
            dataset_name = "Unknown"
            for dataset in datasets_result['data']:
                if dataset.get('id') == request.dataset_id:
                    dataset_name = dataset.get('name', 'Unknown')
                    break
            
            # 創建新會話
            session_result = session_manager.create_session(
                dataset_id=request.dataset_id,
                dataset_name=dataset_name,
                user_id=request.user_id
            )
            
            if not session_result['success']:
                raise HTTPException(status_code=500, detail=session_result['message'])
            
            session_id = session_result['session_id']
        
        # 獲取會話信息
        session_info = session_manager.get_session(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="會話不存在")
        
        # 更新會話使用時間
        session_manager.update_session_usage(session_id)
        
        # 發送聊天請求
        chat_result = ragflow_client.chat_completion(
            chat_id=session_info['chat_id'],
            session_id=session_id,
            question=request.question,
            quote=request.quote,
            stream=request.stream
        )
        
        if not chat_result['success']:
            raise HTTPException(status_code=500, detail=chat_result['message'])
        
        data = chat_result['data']
        
        # 處理 sources 格式
        sources = data.get('reference', [])
        if isinstance(sources, dict) and 'chunks' in sources:
            sources = sources['chunks']
        elif not isinstance(sources, list):
            sources = []
        
        return ChatResponse(
            success=True,
            answer=data.get('answer', ''),
            sources=sources,
            session_id=session_id,
            chat_id=session_info['chat_id'],
            message='回答成功',
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"聊天請求失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions", response_model=List[SessionInfo], summary="獲取活躍會話列表")
async def get_sessions():
    """獲取所有活躍的會話"""
    sessions = []
    for session_id, session_info in session_manager.sessions.items():
        sessions.append(SessionInfo(
            session_id=session_info['session_id'],
            chat_id=session_info['chat_id'],
            dataset_id=session_info['dataset_id'],
            dataset_name=session_info['dataset_name'],
            user_id=session_info['user_id'],
            created_at=session_info['created_at'],
            last_used=session_info['last_used']
        ))
    
    return sessions

@app.delete("/sessions/{session_id}", summary="刪除會話")
async def delete_session(session_id: str):
    """刪除指定的會話"""
    if session_id in session_manager.sessions:
        del session_manager.sessions[session_id]
        return {"success": True, "message": "會話已刪除"}
    else:
        raise HTTPException(status_code=404, detail="會話不存在")

@app.post("/sessions/cleanup", summary="清理過期會話")
async def cleanup_sessions(max_age_hours: int = 24):
    """清理過期的會話"""
    cleaned_count = session_manager.cleanup_old_sessions(max_age_hours)
    return {
        "success": True,
        "message": f"清理了 {cleaned_count} 個過期會話",
        "cleaned_count": cleaned_count
    }

# 後台任務：定期清理過期會話
@app.on_event("startup")
async def startup_event():
    """應用啟動時的初始化"""
    logger.info("RAGFlow Chat API 服務啟動")
    
    # 測試 RAGFlow 連接
    try:
        datasets_result = ragflow_client.list_datasets()
        if datasets_result['success']:
            logger.info(f"RAGFlow 連接成功，找到 {len(datasets_result['data'])} 個數據集")
        else:
            logger.warning(f"RAGFlow 連接測試失敗: {datasets_result['message']}")
    except Exception as e:
        logger.error(f"RAGFlow 連接測試異常: {str(e)}")

async def periodic_cleanup():
    """定期清理過期會話"""
    while True:
        try:
            await asyncio.sleep(3600)  # 每小時執行一次
            cleaned_count = session_manager.cleanup_old_sessions(24)
            if cleaned_count > 0:
                logger.info(f"定期清理了 {cleaned_count} 個過期會話")
        except Exception as e:
            logger.error(f"定期清理任務異常: {str(e)}")

@app.on_event("startup")
async def start_background_tasks():
    """啟動後台任務"""
    asyncio.create_task(periodic_cleanup())

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 啟動 RAGFlow FastAPI 後端服務")
    print("📡 API 文檔: http://localhost:8000/docs")
    print("🔗 ReDoc 文檔: http://localhost:8000/redoc")
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )