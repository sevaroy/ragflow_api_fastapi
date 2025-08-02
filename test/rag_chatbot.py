#!/usr/bin/env python3
"""
RAGFlow RAG 聊天機器人
使用 RAGFlow API 實現的智能問答系統
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY, REQUEST_TIMEOUT

class RAGChatbot:
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = (api_url or RAGFLOW_API_URL).rstrip('/')
        self.api_key = api_key or RAGFLOW_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'RAGFlow-Chatbot/1.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.conversation_history = []
        self.current_kb_id = None
        self.current_kb_name = None
    
    def get_knowledge_bases(self) -> List[Dict]:
        """獲取可用的知識庫列表"""
        try:
            response = self.session.get(
                f'{self.api_url}/api/v1/datasets',
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                print(f"❌ 獲取知識庫失敗: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 請求錯誤: {e}")
            return []
    
    def select_knowledge_base(self, kb_id: str = None) -> bool:
        """選擇知識庫"""
        knowledge_bases = self.get_knowledge_bases()
        
        if not knowledge_bases:
            print("❌ 沒有可用的知識庫")
            return False
        
        if kb_id:
            # 直接指定知識庫 ID
            for kb in knowledge_bases:
                if kb.get('id') == kb_id:
                    self.current_kb_id = kb_id
                    self.current_kb_name = kb.get('name', 'Unknown')
                    print(f"✅ 已選擇知識庫: {self.current_kb_name}")
                    return True
            print(f"❌ 找不到知識庫 ID: {kb_id}")
            return False
        
        # 顯示知識庫列表供用戶選擇
        print("\n📚 可用的知識庫:")
        print("-" * 50)
        for i, kb in enumerate(knowledge_bases, 1):
            print(f"{i}. {kb.get('name', 'N/A')} (ID: {kb.get('id', 'N/A')})")
            print(f"   文件數量: {kb.get('document_count', 'N/A')}")
        
        try:
            choice = input("\n請選擇知識庫編號: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(knowledge_bases):
                selected_kb = knowledge_bases[index]
                self.current_kb_id = selected_kb.get('id')
                self.current_kb_name = selected_kb.get('name', 'Unknown')
                print(f"✅ 已選擇知識庫: {self.current_kb_name}")
                return True
            else:
                print("❌ 無效的選擇")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 無效的輸入")
            return False
    
    def chat(self, question: str, stream: bool = False) -> Dict[str, Any]:
        """發送聊天請求"""
        if not self.current_kb_id:
            return {
                'success': False,
                'message': '請先選擇知識庫',
                'answer': ''
            }
        
        # 構建請求數據
        chat_data = {
            'conversation_id': '',  # 新對話
            'messages': [
                {
                    'role': 'user',
                    'content': question
                }
            ],
            'quote': True,  # 顯示引用來源
            'doc_ids': [self.current_kb_id],  # 指定知識庫
            'stream': stream
        }
        
        try:
            response = self.session.post(
                f'{self.api_url}/api/v1/chats',
                json=chat_data,
                timeout=REQUEST_TIMEOUT * 2  # 聊天請求可能需要更長時間
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 保存對話歷史
                self.conversation_history.append({
                    'question': question,
                    'answer': result.get('data', {}).get('answer', ''),
                    'timestamp': time.time(),
                    'sources': result.get('data', {}).get('reference', [])
                })
                
                return {
                    'success': True,
                    'message': '回答成功',
                    'answer': result.get('data', {}).get('answer', ''),
                    'sources': result.get('data', {}).get('reference', []),
                    'conversation_id': result.get('data', {}).get('id', '')
                }
            else:
                return {
                    'success': False,
                    'message': f'請求失敗: HTTP {response.status_code}',
                    'answer': '',
                    'error': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'請求錯誤: {e}',
                'answer': ''
            }
    
    def print_chat_response(self, response: Dict[str, Any]):
        """格式化顯示聊天回應"""
        if response['success']:
            print(f"\n🤖 {self.current_kb_name} 回答:")
            print("-" * 60)
            print(response['answer'])
            
            # 顯示引用來源
            sources = response.get('sources', [])
            if sources:
                print(f"\n📖 參考來源 ({len(sources)} 個):")
                for i, source in enumerate(sources, 1):
                    doc_name = source.get('doc_name', 'Unknown')
                    content = source.get('content', '')[:100] + '...' if len(source.get('content', '')) > 100 else source.get('content', '')
                    print(f"{i}. {doc_name}")
                    print(f"   內容片段: {content}")
        else:
            print(f"\n❌ {response['message']}")
            if 'error' in response:
                print(f"錯誤詳情: {response['error']}")
    
    def show_conversation_history(self):
        """顯示對話歷史"""
        if not self.conversation_history:
            print("📝 暫無對話歷史")
            return
        
        print(f"\n📜 對話歷史 ({len(self.conversation_history)} 條):")
        print("=" * 60)
        
        for i, conv in enumerate(self.conversation_history, 1):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(conv['timestamp']))
            print(f"\n{i}. [{timestamp}]")
            print(f"❓ 問題: {conv['question']}")
            print(f"🤖 回答: {conv['answer'][:200]}{'...' if len(conv['answer']) > 200 else ''}")
            if conv.get('sources'):
                print(f"📖 來源數量: {len(conv['sources'])}")
    
    def clear_history(self):
        """清除對話歷史"""
        self.conversation_history = []
        print("✅ 對話歷史已清除")

def main():
    """主程序"""
    print("🤖 RAGFlow RAG 聊天機器人")
    print("=" * 50)
    
    # 創建聊天機器人實例
    chatbot = RAGChatbot()
    
    # 選擇知識庫
    if not chatbot.select_knowledge_base():
        print("❌ 無法選擇知識庫，程序退出")
        return
    
    print(f"\n💬 開始與 '{chatbot.current_kb_name}' 對話")
    print("輸入 'quit' 或 'exit' 退出")
    print("輸入 'history' 查看對話歷史")
    print("輸入 'clear' 清除對話歷史")
    print("輸入 'switch' 切換知識庫")
    print("-" * 50)
    
    while True:
        try:
            # 獲取用戶輸入
            question = input(f"\n❓ 你的問題: ").strip()
            
            if not question:
                continue
            
            # 處理特殊命令
            if question.lower() in ['quit', 'exit', '退出']:
                print("👋 再見！")
                break
            elif question.lower() in ['history', '歷史']:
                chatbot.show_conversation_history()
                continue
            elif question.lower() in ['clear', '清除']:
                chatbot.clear_history()
                continue
            elif question.lower() in ['switch', '切換']:
                if chatbot.select_knowledge_base():
                    print(f"✅ 已切換到知識庫: {chatbot.current_kb_name}")
                continue
            
            # 發送聊天請求
            print("🔍 正在搜索相關信息...")
            response = chatbot.chat(question)
            
            # 顯示回應
            chatbot.print_chat_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 程序被中斷，再見！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()