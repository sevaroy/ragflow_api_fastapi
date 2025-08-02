#!/usr/bin/env python3
"""
RAGFlow 聊天機器人 - 簡化版本
基於官方 API 文檔的最簡實現
"""

import requests
import uuid
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

class SimpleRAGFlowBot:
    def __init__(self):
        self.api_url = RAGFLOW_API_URL.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {RAGFLOW_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.chat_id = None
        self.session_id = None
    
    def get_first_dataset(self):
        """獲取第一個可用的數據集"""
        response = requests.get(f'{self.api_url}/api/v1/datasets', headers=self.headers)
        
        if response.status_code == 200:
            datasets = response.json().get('data', [])
            return datasets[0] if datasets else None
        return None
    
    def setup_chat(self, dataset_id: str):
        """設置聊天環境"""
        # 1. 創建聊天助手
        chat_data = {
            'name': f'簡單聊天機器人_{uuid.uuid4().hex[:8]}',
            'dataset_ids': [dataset_id]
        }
        
        response = requests.post(f'{self.api_url}/api/v1/chats', 
                               headers=self.headers, json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                self.chat_id = result['data']['id']
            else:
                return False
        else:
            return False
        
        # 2. 創建會話
        response = requests.post(f'{self.api_url}/api/v1/chats/{self.chat_id}/sessions',
                               headers=self.headers, json={})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                self.session_id = result['data']['id']
                return True
        
        return False
    
    def ask(self, question: str):
        """提問"""
        if not self.chat_id or not self.session_id:
            return None
        
        completion_data = {
            'question': question,
            'quote': True,
            'stream': False,
            'session_id': self.session_id
        }
        
        response = requests.post(f'{self.api_url}/api/v1/chats/{self.chat_id}/completions',
                               headers=self.headers, json=completion_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                data = result['data']
                return {
                    'answer': data.get('answer', ''),
                    'sources': data.get('reference', [])
                }
        
        return None

def main():
    print("🤖 RAGFlow 聊天機器人 - 簡化版本")
    print("=" * 40)
    
    # 初始化機器人
    bot = SimpleRAGFlowBot()
    
    # 獲取數據集
    print("📚 正在獲取數據集...")
    dataset = bot.get_first_dataset()
    
    if not dataset:
        print("❌ 無法獲取數據集")
        return
    
    dataset_name = dataset.get('name', 'Unknown')
    dataset_id = dataset.get('id')
    
    print(f"✅ 使用數據集: {dataset_name}")
    print(f"   文件數量: {dataset.get('document_count', 'N/A')}")
    
    # 設置聊天環境
    print("🔧 正在設置聊天環境...")
    if not bot.setup_chat(dataset_id):
        print("❌ 聊天環境設置失敗")
        return
    
    print("✅ 聊天環境設置成功")
    print("-" * 40)
    
    # 自動測試
    test_questions = [
        "這個數據集包含什麼內容？",
        "請簡單介紹主要概念",
        "有什麼重要信息？"
    ]
    
    print("🧪 自動測試問題:")
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. ❓ {question}")
        print("   🔍 搜索中...")
        
        result = bot.ask(question)
        
        if result:
            answer = result['answer']
            sources = result['sources']
            
            if answer:
                print(f"   🤖 回答: {answer[:150]}{'...' if len(answer) > 150 else ''}")
                print(f"   📖 參考來源: {len(sources)} 個")
            else:
                print("   🤖 沒有找到相關內容")
        else:
            print("   ❌ 請求失敗")
    
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
            result = bot.ask(question)
            
            if result:
                if result['answer']:
                    print(f"\n🤖 回答:")
                    print("-" * 30)
                    print(result['answer'])
                    
                    sources = result['sources']
                    if sources:
                        print(f"\n📖 參考來源 ({len(sources)} 個):")
                        for i, source in enumerate(sources[:3], 1):
                            if isinstance(source, dict):
                                doc_name = source.get('doc_name', 'Unknown')
                                print(f"  {i}. {doc_name}")
                else:
                    print("🤖 沒有找到相關答案")
            else:
                print("❌ 請求失敗")
        
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break

if __name__ == "__main__":
    main()