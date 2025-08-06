"""
API 客戶端服務 (非同步版本)
"""
import httpx
from typing import Optional, Dict, Any, Union

from config import settings

class RAGFlowApiClient:
    """RAGFlow API 非同步客戶端 (單例模式)"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RAGFlowApiClient, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, 'initialized'):  # 避免重複初始化
            self.api_url: str = settings.RAGFLOW_API_BASE_URL
            self.client: httpx.AsyncClient = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=30.0
            )
            self.initialized = True

    async def close(self):
        """優雅地關閉 httpx 客戶端"""
        await self.client.aclose()

    async def check_api_health(self) -> Dict[str, Any]:
        """檢查 API 健康狀態"""
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {"success": False, "error": str(e)}

    async def get_datasets(self) -> Dict[str, Any]:
        """獲取數據集列表"""
        try:
            response = await self.client.get("/datasets")
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {"success": False, "error": str(e)}

    async def send_chat_message(
        self, 
        question: str, 
        dataset_id: str, 
        session_id: Optional[str] = None, 
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """發送聊天消息"""
        try:
            payload: Dict[str, Any] = {
                "question": question,
                "dataset_id": dataset_id,
                "quote": True
            }
            if session_id:
                payload["session_id"] = session_id
            if user_id:
                payload["user_id"] = user_id

            response = await self.client.post("/chat", json=payload)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {"success": False, "error": str(e)}

    async def get_sessions(self) -> Dict[str, Any]:
        """獲取活躍會話列表"""
        try:
            response = await self.client.get("/sessions")
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {"success": False, "error": str(e)}

    async def delete_session(self, session_id: str) -> Dict[str, Any]:
        """刪除會話"""
        try:
            response = await self.client.delete(f"/sessions/{session_id}")
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            return {"success": False, "error": str(e)}


# 提供一個全局的客戶端實例
api_client = RAGFlowApiClient()
