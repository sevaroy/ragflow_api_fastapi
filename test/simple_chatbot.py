#!/usr/bin/env python3
"""
簡單的 RAGFlow 聊天機器人範例
快速測試 RAG 問答功能
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

def ask_question(question: str, kb_id: str):
    """向知識庫提問"""
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    chat_data = {
        'name': f'RAG聊天機器人_{uuid.uuid4().hex[:8]}',
        'conversation_id': '',
        'question': question,
        'quote': True,
        'dataset_ids': [kb_id],
        'stream': False
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
            print(f"API 回應: {result}")  # 調試信息
            
            # 處理不同的回應格式
            if 'data' in result:
                data = result['data']
                return {
                    'success': True,
                    'answer': data.get('answer', '') if data else '',
                    'sources': data.get('reference', []) if data else []
                }
            else:
                return {
                    'success': True,
                    'answer': result.get('answer', ''),
                    'sources': result.get('reference', [])
                }
        
        else:
            return {
                'success': False,
                'error': f'HTTP {response.status_code}: {response.text}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("🤖 簡單 RAG 聊天機器人測試")
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
        "這個知識庫包含什麼內容？",
        "請簡單介紹一下主要內容",
        "有什麼重要的概念或規則？"
    ]
    
    print("🔍 自動測試問題:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. ❓ {question}")
        print("   🔍 搜索中...")
        
        result = ask_question(question, kb_id)
        
        if result['success']:
            answer = result['answer']
            sources = result['sources']
            
            print(f"   🤖 回答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"   📖 參考來源: {len(sources)} 個")
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
                print(f"\n🤖 回答:")
                print("-" * 30)
                print(result['answer'])
                
                sources = result['sources']
                if sources:
                    print(f"\n📖 參考來源 ({len(sources)} 個):")
                    for i, source in enumerate(sources[:3], 1):  # 只顯示前3個來源
                        doc_name = source.get('doc_name', 'Unknown')
                        print(f"  {i}. {doc_name}")
            else:
                print(f"❌ 錯誤: {result['error']}")
                
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break

if __name__ == "__main__":
    main()