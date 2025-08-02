#!/usr/bin/env python3
"""
RAGFlow API 客戶端
提供完整的 RAGFlow API 操作功能
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY, ENDPOINTS, REQUEST_TIMEOUT, MAX_RETRIES

class RAGFlowAPIError(Exception):
    """RAGFlow API 錯誤"""
    pass

class RAGFlowClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = (api_url or RAGFLOW_API_URL).rstrip('/')
        self.api_key = api_key or RAGFLOW_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'RAGFlow-Python-Client/1.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """發送 HTTP 請求，包含重試機制"""
        url = f'{self.api_url}{endpoint}'
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=REQUEST_TIMEOUT,
                    **kwargs
                )
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == MAX_RETRIES - 1:
                    raise RAGFlowAPIError(f"請求失敗 (嘗試 {MAX_RETRIES} 次): {e}")
                
                print(f"⚠️  請求失敗，正在重試 ({attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(2 ** attempt)  # 指數退避
    
    def test_connection(self) -> Dict[str, Any]:
        """測試 API 連線"""
        try:
            response = self._make_request('GET', ENDPOINTS['health'])
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'message': ''
            }
            
            if result['success']:
                result['message'] = '連線成功'
                try:
                    result['data'] = response.json()
                except json.JSONDecodeError:
                    result['data'] = response.text
            else:
                result['message'] = f'連線失敗: HTTP {response.status_code}'
                result['error'] = response.text
            
            return result
            
        except RAGFlowAPIError as e:
            return {
                'success': False,
                'message': str(e),
                'status_code': None,
                'response_time': None
            }
    
    def list_knowledge_bases(self) -> Dict[str, Any]:
        """列出所有知識庫"""
        try:
            response = self._make_request('GET', ENDPOINTS['datasets'])
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': [],
                'message': ''
            }
            
            if result['success']:
                try:
                    json_data = response.json()
                    result['data'] = json_data.get('data', [])
                    result['message'] = f'成功獲取 {len(result["data"])} 個知識庫'
                except json.JSONDecodeError:
                    result['success'] = False
                    result['message'] = 'JSON 解析錯誤'
                    result['error'] = response.text
            else:
                result['message'] = f'獲取知識庫失敗: HTTP {response.status_code}'
                result['error'] = response.text
            
            return result
            
        except RAGFlowAPIError as e:
            return {
                'success': False,
                'message': str(e),
                'data': [],
                'status_code': None
            }
    
    def get_knowledge_base_details(self, kb_id: str) -> Dict[str, Any]:
        """獲取知識庫詳細信息"""
        try:
            response = self._make_request('GET', f'{ENDPOINTS["datasets"]}/{kb_id}')
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': None,
                'message': ''
            }
            
            if result['success']:
                try:
                    result['data'] = response.json()
                    result['message'] = '成功獲取知識庫詳情'
                except json.JSONDecodeError:
                    result['success'] = False
                    result['message'] = 'JSON 解析錯誤'
            else:
                result['message'] = f'獲取知識庫詳情失敗: HTTP {response.status_code}'
                result['error'] = response.text
            
            return result
            
        except RAGFlowAPIError as e:
            return {
                'success': False,
                'message': str(e),
                'data': None,
                'status_code': None
            }

def main():
    """主測試函數"""
    print("🚀 RAGFlow API 測試開始")
    print(f"API URL: {RAGFLOW_API_URL}")
    print("=" * 60)
    
    # 創建客戶端
    client = RAGFlowClient()
    
    # 測試連線
    print("🔗 測試 API 連線...")
    connection_result = client.test_connection()
    
    if connection_result['success']:
        print(f"✅ {connection_result['message']}")
        print(f"   回應時間: {connection_result['response_time']:.2f}s")
    else:
        print(f"❌ {connection_result['message']}")
        return
    
    print("-" * 60)
    
    # 列出知識庫
    print("📚 獲取知識庫列表...")
    kb_result = client.list_knowledge_bases()
    
    if kb_result['success']:
        print(f"✅ {kb_result['message']}")
        
        if len(kb_result['data']) == 0:
            print("📝 目前沒有知識庫")
        else:
            print("\n📋 知識庫列表:")
            print("-" * 60)
            
            for i, kb in enumerate(kb_result['data'], 1):
                print(f"{i:2d}. 📖 {kb.get('name', 'N/A')}")
                print(f"     ID: {kb.get('id', 'N/A')}")
                print(f"     描述: {kb.get('description', 'N/A')}")
                print(f"     創建時間: {kb.get('create_time', 'N/A')}")
                print(f"     文件數量: {kb.get('document_count', 'N/A')}")
                print(f"     狀態: {kb.get('status', 'N/A')}")
                print("-" * 40)
    else:
        print(f"❌ {kb_result['message']}")
    
    print("✨ 測試完成")

if __name__ == "__main__":
    main()