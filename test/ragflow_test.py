#!/usr/bin/env python3
"""
RAGFlow API 測試腳本
測試連線並列出所有知識庫
"""

import requests
import json
import sys
from typing import Dict, List, Optional

class RAGFlowClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> bool:
        """測試 API 連線"""
        try:
            response = requests.get(
                f'{self.api_url}/api/v1/health',
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                print("✅ API 連線成功")
                return True
            else:
                print(f"❌ API 連線失敗: HTTP {response.status_code}")
                print(f"回應內容: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ 連線錯誤: {e}")
            return False
    
    def list_knowledge_bases(self) -> Optional[List[Dict]]:
        """列出所有知識庫"""
        try:
            response = requests.get(
                f'{self.api_url}/api/v1/datasets',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"❌ 獲取知識庫失敗: HTTP {response.status_code}")
                print(f"回應內容: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 請求錯誤: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析錯誤: {e}")
            return None

def main():
    # RAGFlow API 配置
    RAGFLOW_API_URL = "http://192.168.50.123"
    RAGFLOW_API_KEY = "ragflow-Y2YWUxOTY4MDIwNzExZjBhMTgzMDI0Mm"
    
    print("🚀 RAGFlow API 測試開始")
    print(f"API URL: {RAGFLOW_API_URL}")
    print("-" * 50)
    
    # 創建客戶端
    client = RAGFlowClient(RAGFLOW_API_URL, RAGFLOW_API_KEY)
    
    # 測試連線
    if not client.test_connection():
        sys.exit(1)
    
    print("-" * 50)
    
    # 列出知識庫
    print("📚 正在獲取知識庫列表...")
    knowledge_bases = client.list_knowledge_bases()
    
    if knowledge_bases is not None:
        if len(knowledge_bases) == 0:
            print("📝 目前沒有知識庫")
        else:
            print(f"📋 找到 {len(knowledge_bases)} 個知識庫:")
            print("-" * 50)
            
            for i, kb in enumerate(knowledge_bases, 1):
                print(f"{i}. 名稱: {kb.get('name', 'N/A')}")
                print(f"   ID: {kb.get('id', 'N/A')}")
                print(f"   描述: {kb.get('description', 'N/A')}")
                print(f"   創建時間: {kb.get('create_time', 'N/A')}")
                print(f"   文件數量: {kb.get('document_count', 'N/A')}")
                print("-" * 30)
    
    print("✨ 測試完成")

if __name__ == "__main__":
    main()