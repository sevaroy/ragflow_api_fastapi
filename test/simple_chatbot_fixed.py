#!/usr/bin/env python3
"""
修復版 RAGFlow 聊天機器人範例
使用正確的 API 端點進行問答
"""

import requests
import json
import uuid
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

def get_first_knowledge_base():
    """獲取第一個可用的知識庫"""
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'{RAGFLOW_API_URL}/api/v1/datasets',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            knowledge_bases = data.get('data', [])
            if knowledge_bases:
                return knowledge_bases[0]
        
        return None
    except Exception as e:
        print(f"❌ 獲取知識庫失敗: {e}")
        return None

def create_chat_session(kb_id: str):
    """創建聊天會話"""
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    chat_data = {
        'name': f'RAG聊天機器人_{uuid.uuid4().hex[:8]}',
        'dataset_ids': [kb_id]
    }
    
    try:
        response = requests.post(
            f'{RAGFLOW_API_URL}/api/v1/chats',
            headers=headers,
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return result['data']['id']
        return None
    except:
        return None

def ask_question(question: str, kb_id: str):
    """向知識庫提問"""
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # 先創建聊天會話
    chat_id = create_chat_session(kb_id)
    if not chat_id:
        return {
            'success': False,
            'error': '無法創建聊天會話',
            'answer': ''
        }
    
    # 發送消息
    message_data = {
        'question': question,
        'quote': True,
        'stream': False
    }
    
    try:
        response = requests.post(
            f'{RAGFLOW_API_URL}/api/v1/chats/{chat_id}/completions',
            headers=headers,
            json=message_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('code') == 0 and result.get('data'):
                data = result['data']
                return {
                    'success': True,
                    'answer': data.get('answer', ''),
                    'sources': data.get('reference', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '未知錯誤'),
                    'answer': ''
                }
        else:
            return {
                'success': False,
                'error': f'API 錯誤: {response.status_code}',
                'answer': ''
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'請求失敗: {str(e)}',
            'answer': ''
        }

def main():
    print("🤖 修復版 RAG 聊天機器人測試")
    print("=" * 40)
    
    # 獲取知識庫
    print("📚 正在獲取知識庫...")
    kb = get_first_knowledge_base()
    
    if not kb:
        print("❌ 無法獲取知識庫")
        return
    
    kb_name = kb.get('name', 'Unknown')
    kb_id = kb.get('id')
    
    print(f"✅ 使用知識庫: {kb_name}")
    print(f"   ID: {kb_id}")
    print(f"   文件數量: {kb.get('document_count', 'N/A')}")
    print("-" * 40)
    
    # 預設測試問題
    test_questions = [
        "什麼是憲法？",
        "憲法有什麼重要性？",
        "行政法的基本原則是什麼？"
    ]
    
    print("🔍 自動測試問題:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. ❓ {question}")
        print("   🔍 搜索中...")
        
        result = ask_question(question, kb_id)
        
        if result['success']:
            answer = result['answer']
            sources = result['sources']
            
            if answer:
                print(f"   🤖 回答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                print(f"   📖 參考來源: {len(sources)} 個")
            else:
                print("   🤖 回答為空")
        else:
            print(f"   ❌ 錯誤: {result['error']}")
    
    print("\n" + "=" * 40)
    print("💬 現在你可以自由提問 (輸入 'quit' 退出):")
    
    # 互動問答
    while True:
        try:
            question = input("\n❓ 你的問題: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再見！")
                break
            
            print("🔍 搜索中...")
            result = ask_question(question, kb_id)
            
            if result['success']:
                if result['answer']:
                    print(f"\n🤖 回答:")
                    print("-" * 30)
                    print(result['answer'])
                    
                    sources = result['sources']
                    if sources and isinstance(sources, list):
                        print(f"\n📖 參考來源 ({len(sources)} 個):")
                        for i, source in enumerate(sources[:3], 1):  # 只顯示前3個來源
                            if isinstance(source, dict):
                                doc_name = source.get('doc_name', 'Unknown')
                                print(f"  {i}. {doc_name}")
                            else:
                                print(f"  {i}. {source}")
                else:
                    print("🤖 沒有找到相關答案")
            else:
                print(f"❌ 錯誤: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break

if __name__ == "__main__":
    main()