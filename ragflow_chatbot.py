#!/usr/bin/env python3
"""
RAGFlow 聊天機器人 - 完整功能版本
基於官方 RAGFlow Python API 文檔實現
參考: https://ragflow.io/docs/dev/python_api_reference#create-session-with-chat-assistant
"""

import requests
import json
import uuid
import time
from typing import Dict, List, Optional, Any
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

class RAGFlowOfficialClient:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = (api_url or RAGFLOW_API_URL).rstrip('/')
        self.api_key = api_key or RAGFLOW_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def list_datasets(self) -> Dict[str, Any]:
        """列出所有數據集/知識庫"""
        try:
            response = self.session.get(f'{self.api_url}/api/v1/datasets')
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'data': result.get('data', []),
                    'message': '成功獲取數據集列表'
                }
            else:
                return {
                    'success': False,
                    'data': [],
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'message': f'請求失敗: {str(e)}'
            }
    
    def create_chat(self, name: str, dataset_ids: List[str], **kwargs) -> Dict[str, Any]:
        """創建聊天助手會話
        
        Args:
            name: 聊天助手名稱
            dataset_ids: 數據集 ID 列表
            **kwargs: 其他可選參數 (llm, prompt, etc.)
        """
        chat_data = {
            'name': name,
            'dataset_ids': dataset_ids,
            **kwargs
        }
        
        try:
            response = self.session.post(
                f'{self.api_url}/api/v1/chats',
                json=chat_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return {
                        'success': True,
                        'data': result.get('data'),
                        'message': '成功創建聊天會話'
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'message': result.get('message', '創建聊天會話失敗')
                    }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'請求失敗: {str(e)}'
            }
    
    def list_chats(self) -> Dict[str, Any]:
        """列出所有聊天會話"""
        try:
            response = self.session.get(f'{self.api_url}/api/v1/chats')
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'data': result.get('data', []),
                    'message': '成功獲取聊天會話列表'
                }
            else:
                return {
                    'success': False,
                    'data': [],
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'data': [],
                'message': f'請求失敗: {str(e)}'
            }
    
    def create_session(self, chat_id: str, user_id: str = None) -> Dict[str, Any]:
        """創建會話
        
        Args:
            chat_id: 聊天助手 ID
            user_id: 用戶 ID (可選)
        """
        session_data = {}
        if user_id:
            session_data['user_id'] = user_id
        
        try:
            response = self.session.post(
                f'{self.api_url}/api/v1/chats/{chat_id}/sessions',
                json=session_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return {
                        'success': True,
                        'data': result.get('data'),
                        'message': '成功創建會話'
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'message': result.get('message', '創建會話失敗')
                    }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'請求失敗: {str(e)}'
            }
    
    def chat_completion(self, chat_id: str, session_id: str, question: str, 
                       quote: bool = True, stream: bool = False) -> Dict[str, Any]:
        """發送聊天完成請求
        
        Args:
            chat_id: 聊天助手 ID
            session_id: 會話 ID
            question: 問題
            quote: 是否顯示引用
            stream: 是否流式回應
        """
        completion_data = {
            'question': question,
            'quote': quote,
            'stream': stream,
            'session_id': session_id
        }
        
        try:
            response = self.session.post(
                f'{self.api_url}/api/v1/chats/{chat_id}/completions',
                json=completion_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return {
                        'success': True,
                        'data': result.get('data'),
                        'message': '成功獲取回答'
                    }
                else:
                    return {
                        'success': False,
                        'data': None,
                        'message': result.get('message', '獲取回答失敗')
                    }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': f'HTTP {response.status_code}: {response.text}'
                }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'請求失敗: {str(e)}'
            }

class RAGFlowChatbot:
    def __init__(self):
        self.client = RAGFlowOfficialClient()
        self.chat_id = None
        self.session_id = None
        self.chat_name = None
        self.dataset_name = None
    
    def setup_chat(self, dataset_id: str, dataset_name: str = "Unknown") -> bool:
        """設置聊天環境"""
        self.dataset_name = dataset_name
        
        # 創建聊天助手
        chat_name = f"RAG聊天機器人_{uuid.uuid4().hex[:8]}"
        chat_result = self.client.create_chat(
            name=chat_name,
            dataset_ids=[dataset_id]
        )
        
        if not chat_result['success']:
            print(f"❌ 創建聊天助手失敗: {chat_result['message']}")
            return False
        
        self.chat_id = chat_result['data']['id']
        self.chat_name = chat_name
        print(f"✅ 創建聊天助手成功: {chat_name}")
        
        # 創建會話
        session_result = self.client.create_session(self.chat_id)
        
        if not session_result['success']:
            print(f"❌ 創建會話失敗: {session_result['message']}")
            return False
        
        self.session_id = session_result['data']['id']
        print(f"✅ 創建會話成功: {self.session_id}")
        
        return True
    
    def ask(self, question: str) -> Dict[str, Any]:
        """提問"""
        if not self.chat_id or not self.session_id:
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'message': '聊天環境未設置'
            }
        
        result = self.client.chat_completion(
            chat_id=self.chat_id,
            session_id=self.session_id,
            question=question,
            quote=True,
            stream=False
        )
        
        if result['success']:
            data = result['data']
            return {
                'success': True,
                'answer': data.get('answer', ''),
                'sources': data.get('reference', []),
                'message': '回答成功'
            }
        else:
            return {
                'success': False,
                'answer': '',
                'sources': [],
                'message': result['message']
            }

def main():
    print("🤖 RAGFlow 聊天機器人 - 完整功能版本")
    print("=" * 50)
    
    # 創建客戶端
    client = RAGFlowOfficialClient()
    
    # 獲取數據集列表
    print("📚 正在獲取數據集列表...")
    datasets_result = client.list_datasets()
    
    if not datasets_result['success']:
        print(f"❌ 獲取數據集失敗: {datasets_result['message']}")
        return
    
    datasets = datasets_result['data']
    if not datasets:
        print("❌ 沒有可用的數據集")
        return
    
    print(f"✅ 找到 {len(datasets)} 個數據集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset.get('name', 'N/A')} (ID: {dataset.get('id', 'N/A')})")
        print(f"     文件數量: {dataset.get('document_count', 'N/A')}")
    
    # 選擇數據集
    try:
        choice = input(f"\n請選擇數據集 [1-{len(datasets)}]: ").strip()
        index = int(choice) - 1
        
        if 0 <= index < len(datasets):
            selected_dataset = datasets[index]
            dataset_id = selected_dataset['id']
            dataset_name = selected_dataset['name']
        else:
            print("❌ 無效選擇，使用第一個數據集")
            selected_dataset = datasets[0]
            dataset_id = selected_dataset['id']
            dataset_name = selected_dataset['name']
    except (ValueError, KeyboardInterrupt):
        print("❌ 無效輸入，使用第一個數據集")
        selected_dataset = datasets[0]
        dataset_id = selected_dataset['id']
        dataset_name = selected_dataset['name']
    
    print(f"📖 選擇數據集: {dataset_name}")
    print("-" * 50)
    
    # 設置聊天機器人
    chatbot = RAGFlowChatbot()
    if not chatbot.setup_chat(dataset_id, dataset_name):
        print("❌ 聊天環境設置失敗")
        return
    
    print("-" * 50)
    print("💬 聊天機器人已準備就緒！")
    print("輸入 'quit' 或 'exit' 退出")
    print("輸入 'test' 運行自動測試")
    print("-" * 50)
    
    # 自動測試
    test_questions = [
        "這個數據集包含什麼內容？",
        "請簡單介紹主要概念",
        "有什麼重要信息？"
    ]
    
    while True:
        try:
            question = input(f"\n❓ 你的問題: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再見！")
                break
            
            if question.lower() == 'test':
                print("\n🧪 運行自動測試...")
                for i, test_q in enumerate(test_questions, 1):
                    print(f"\n{i}. ❓ {test_q}")
                    print("   🔍 搜索中...")
                    
                    result = chatbot.ask(test_q)
                    
                    if result['success']:
                        answer = result['answer']
                        sources = result['sources']
                        
                        if answer:
                            print(f"   🤖 回答: {answer[:200]}{'...' if len(answer) > 200 else ''}")
                            print(f"   📖 參考來源: {len(sources)} 個")
                        else:
                            print("   🤖 沒有找到相關內容")
                    else:
                        print(f"   ❌ 錯誤: {result['message']}")
                continue
            
            print("🔍 搜索中...")
            result = chatbot.ask(question)
            
            if result['success']:
                if result['answer']:
                    print(f"\n🤖 回答:")
                    print("-" * 30)
                    print(result['answer'])
                    
                    sources = result['sources']
                    if sources and isinstance(sources, list):
                        print(f"\n📖 參考來源 ({len(sources)} 個):")
                        for i, source in enumerate(sources[:3], 1):
                            if isinstance(source, dict):
                                doc_name = source.get('doc_name', 'Unknown')
                                content = source.get('content', '')[:100]
                                print(f"  {i}. {doc_name}")
                                if content:
                                    print(f"     內容片段: {content}...")
                            else:
                                print(f"  {i}. {source}")
                else:
                    print("🤖 沒有找到相關答案")
            else:
                print(f"❌ 錯誤: {result['message']}")
        
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()