#!/usr/bin/env python3
"""
RAGFlow API 端點測試工具
測試不同的 API 端點來找到正確的聊天接口
"""

import requests
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

def test_endpoint(endpoint, method='GET', data=None):
    """測試 API 端點"""
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = f'{RAGFLOW_API_URL}{endpoint}'
    print(f"\n🔍 測試: {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   回應: {str(result)[:200]}...")
                return True
            except:
                print(f"   回應: {response.text[:200]}...")
                return True
        else:
            print(f"   錯誤: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   異常: {e}")
        return False

def main():
    print("🔍 RAGFlow API 端點測試")
    print("=" * 50)
    
    # 獲取第一個知識庫 ID
    kb_response = requests.get(
        f'{RAGFLOW_API_URL}/api/v1/datasets',
        headers={'Authorization': f'Bearer {RAGFLOW_API_KEY}'},
        timeout=10
    )
    
    if kb_response.status_code == 200:
        kbs = kb_response.json().get('data', [])
        if kbs:
            kb_id = kbs[0]['id']
            kb_name = kbs[0]['name']
            print(f"✅ 使用知識庫: {kb_name} ({kb_id})")
        else:
            print("❌ 沒有可用的知識庫")
            return
    else:
        print("❌ 無法獲取知識庫")
        return
    
    # 測試不同的聊天端點
    chat_endpoints = [
        '/api/v1/chats',
        '/api/v1/chat',
        '/api/v1/conversation',
        '/api/v1/conversations',
        '/api/v1/completions',
        '/api/v1/completion'
    ]
    
    test_question = "什麼是憲法？"
    
    # 測試不同的請求格式
    request_formats = [
        {
            'conversation_id': '',
            'question': test_question,
            'quote': True,
            'doc_ids': [kb_id],
            'stream': False
        },
        {
            'conversation_id': '',
            'messages': [{'role': 'user', 'content': test_question}],
            'quote': True,
            'doc_ids': [kb_id],
            'stream': False
        },
        {
            'question': test_question,
            'dataset_id': kb_id,
            'quote': True,
            'stream': False
        },
        {
            'query': test_question,
            'dataset_id': kb_id,
            'quote': True
        }
    ]
    
    print(f"\n📝 測試問題: {test_question}")
    print("-" * 50)
    
    success_found = False
    
    for endpoint in chat_endpoints:
        for i, data in enumerate(request_formats):
            print(f"\n🧪 測試端點: {endpoint} (格式 {i+1})")
            if test_endpoint(endpoint, 'POST', data):
                success_found = True
                print(f"✅ 可能的成功端點: {endpoint}")
                print(f"   使用格式: {data}")
    
    if not success_found:
        print("\n❌ 沒有找到有效的聊天端點")
        print("建議檢查 RAGFlow API 文檔或版本")

if __name__ == "__main__":
    main()