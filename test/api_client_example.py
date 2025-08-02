#!/usr/bin/env python3
"""
RAGFlow FastAPI 客戶端示例
展示如何調用 FastAPI 後端進行 RAG 聊天
"""

import requests
import json
from typing import Dict, List, Optional

class RAGFlowAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_datasets(self) -> Dict:
        """獲取數據集列表"""
        try:
            response = self.session.get(f"{self.base_url}/datasets")
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat(self, question: str, dataset_id: str, session_id: Optional[str] = None, 
             user_id: Optional[str] = None, quote: bool = True) -> Dict:
        """發送聊天消息"""
        try:
            payload = {
                'question': question,
                'dataset_id': dataset_id,
                'quote': quote
            }
            
            if session_id:
                payload['session_id'] = session_id
            if user_id:
                payload['user_id'] = user_id
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sessions(self) -> Dict:
        """獲取活躍會話列表"""
        try:
            response = self.session.get(f"{self.base_url}/sessions")
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_session(self, session_id: str) -> Dict:
        """刪除會話"""
        try:
            response = self.session.delete(f"{self.base_url}/sessions/{session_id}")
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def demo_chat_agent():
    """演示聊天代理機器人如何使用 API"""
    print("🤖 RAGFlow API 客戶端演示")
    print("=" * 50)
    
    # 創建 API 客戶端
    client = RAGFlowAPIClient()
    
    # 1. 獲取數據集列表
    print("📚 正在獲取數據集列表...")
    datasets_result = client.get_datasets()
    
    if not datasets_result['success']:
        print(f"❌ 獲取數據集失敗: {datasets_result['error']}")
        return
    
    datasets = datasets_result['data']
    if not datasets:
        print("❌ 沒有可用的數據集")
        return
    
    print(f"✅ 找到 {len(datasets)} 個數據集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset['name']} (ID: {dataset['id']})")
        print(f"     文件數量: {dataset['document_count']}")
    
    # 選擇第一個數據集
    selected_dataset = datasets[0]
    dataset_id = selected_dataset['id']
    dataset_name = selected_dataset['name']
    
    print(f"\n📖 使用數據集: {dataset_name}")
    print("-" * 50)
    
    # 2. 模擬聊天代理機器人的對話
    user_id = "demo_user_001"
    session_id = None
    
    # 測試問題列表
    test_questions = [
        "這個數據集包含什麼內容？",
        "請簡單介紹主要概念",
        "有什麼重要信息？",
        "能否提供更多細節？"
    ]
    
    print("💬 開始模擬聊天對話...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. 👤 用戶問題: {question}")
        print("   🔍 正在處理...")
        
        # 發送聊天請求
        chat_result = client.chat(
            question=question,
            dataset_id=dataset_id,
            session_id=session_id,
            user_id=user_id,
            quote=True
        )
        
        if chat_result['success']:
            data = chat_result['data']
            answer = data['answer']
            sources = data['sources']
            session_id = data['session_id']  # 保存會話 ID 用於後續對話
            
            print(f"   🤖 回答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"   📖 參考來源: {len(sources)} 個")
            print(f"   🔗 會話 ID: {session_id}")
            
            # 顯示來源詳情
            if sources:
                print("   📋 來源詳情:")
                for j, source in enumerate(sources[:2], 1):  # 只顯示前2個來源
                    if isinstance(source, dict):
                        doc_name = source.get('doc_name', 'Unknown')
                        print(f"      {j}. {doc_name}")
        else:
            print(f"   ❌ 請求失敗: {chat_result['error']}")
    
    # 3. 查看活躍會話
    print(f"\n📊 查看活躍會話...")
    sessions_result = client.get_sessions()
    
    if sessions_result['success']:
        sessions = sessions_result['data']
        print(f"✅ 找到 {len(sessions)} 個活躍會話:")
        for session in sessions:
            print(f"  - 會話 ID: {session['session_id']}")
            print(f"    數據集: {session['dataset_name']}")
            print(f"    用戶 ID: {session['user_id']}")
            print(f"    創建時間: {session['created_at']}")
    else:
        print(f"❌ 獲取會話失敗: {sessions_result['error']}")
    
    print("\n" + "=" * 50)
    print("✨ 演示完成！")
    print("\n💡 聊天代理機器人可以通過以下方式使用 API:")
    print("1. 調用 /datasets 獲取可用的知識庫")
    print("2. 調用 /chat 發送問題並獲取回答")
    print("3. 使用 session_id 維持對話上下文")
    print("4. 調用 /sessions 管理會話狀態")

def interactive_chat():
    """交互式聊天演示"""
    print("\n🎯 交互式聊天演示")
    print("=" * 30)
    
    client = RAGFlowAPIClient()
    
    # 獲取數據集
    datasets_result = client.get_datasets()
    if not datasets_result['success']:
        print(f"❌ 無法獲取數據集: {datasets_result['error']}")
        return
    
    datasets = datasets_result['data']
    if not datasets:
        print("❌ 沒有可用的數據集")
        return
    
    # 選擇數據集
    print("📚 可用數據集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset['name']}")
    
    try:
        choice = int(input(f"\n請選擇數據集 [1-{len(datasets)}]: ")) - 1
        if 0 <= choice < len(datasets):
            selected_dataset = datasets[choice]
        else:
            selected_dataset = datasets[0]
    except:
        selected_dataset = datasets[0]
    
    dataset_id = selected_dataset['id']
    dataset_name = selected_dataset['name']
    
    print(f"✅ 選擇數據集: {dataset_name}")
    print("\n💬 開始聊天 (輸入 'quit' 退出):")
    
    session_id = None
    user_id = "interactive_user"
    
    while True:
        try:
            question = input("\n❓ 你的問題: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再見！")
                break
            
            print("🔍 搜索中...")
            
            chat_result = client.chat(
                question=question,
                dataset_id=dataset_id,
                session_id=session_id,
                user_id=user_id
            )
            
            if chat_result['success']:
                data = chat_result['data']
                session_id = data['session_id']
                
                print(f"\n🤖 回答:")
                print("-" * 30)
                print(data['answer'])
                
                sources = data['sources']
                if sources:
                    print(f"\n📖 參考來源 ({len(sources)} 個):")
                    for i, source in enumerate(sources[:3], 1):
                        if isinstance(source, dict):
                            doc_name = source.get('doc_name', 'Unknown')
                            print(f"  {i}. {doc_name}")
            else:
                print(f"❌ 錯誤: {chat_result['error']}")
        
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break

if __name__ == "__main__":
    print("🚀 RAGFlow FastAPI 客戶端測試")
    print("請確保 FastAPI 服務器正在運行 (python3 fastapi_server.py)")
    print()
    
    try:
        # 運行演示
        demo_chat_agent()
        
        # 詢問是否進行交互式聊天
        choice = input("\n是否進行交互式聊天測試? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_chat()
    
    except KeyboardInterrupt:
        print("\n👋 程序被中斷，再見！")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")