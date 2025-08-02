#!/usr/bin/env python3
"""
FastAPI 服務測試腳本
測試所有 API 端點的功能
"""

import requests
import time
import json
from typing import Dict, Any

class FastAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def test_health_check(self) -> Dict[str, Any]:
        """測試健康檢查端點"""
        try:
            response = self.session.get(f"{self.base_url}/")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_get_datasets(self) -> Dict[str, Any]:
        """測試獲取數據集端點"""
        try:
            response = self.session.get(f"{self.base_url}/datasets")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_chat(self, question: str, dataset_id: str, session_id: str = None) -> Dict[str, Any]:
        """測試聊天端點"""
        try:
            payload = {
                'question': question,
                'dataset_id': dataset_id,
                'quote': True
            }
            
            if session_id:
                payload['session_id'] = session_id
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_get_sessions(self) -> Dict[str, Any]:
        """測試獲取會話端點"""
        try:
            response = self.session.get(f"{self.base_url}/sessions")
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def run_comprehensive_test():
    """運行全面的 API 測試"""
    print("🧪 FastAPI 服務全面測試")
    print("=" * 50)
    
    tester = FastAPITester()
    
    # 1. 測試健康檢查
    print("1. 🔍 測試健康檢查端點...")
    health_result = tester.test_health_check()
    
    if health_result['success']:
        print("   ✅ 健康檢查通過")
        print(f"   📊 服務狀態: {health_result['data']['status']}")
    else:
        print(f"   ❌ 健康檢查失敗: {health_result.get('error', '未知錯誤')}")
        return
    
    # 2. 測試獲取數據集
    print("\n2. 📚 測試獲取數據集端點...")
    datasets_result = tester.test_get_datasets()
    
    if datasets_result['success']:
        datasets = datasets_result['data']
        print(f"   ✅ 成功獲取 {len(datasets)} 個數據集")
        
        if datasets:
            first_dataset = datasets[0]
            dataset_id = first_dataset['id']
            dataset_name = first_dataset['name']
            print(f"   📖 將使用數據集: {dataset_name}")
        else:
            print("   ❌ 沒有可用的數據集")
            return
    else:
        print(f"   ❌ 獲取數據集失敗: {datasets_result.get('error', '未知錯誤')}")
        return
    
    # 3. 測試聊天功能
    print("\n3. 💬 測試聊天端點...")
    test_questions = [
        "這個數據集包含什麼內容？",
        "請簡單介紹主要概念"
    ]
    
    session_id = None
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n   3.{i} 測試問題: {question}")
        
        chat_result = tester.test_chat(
            question=question,
            dataset_id=dataset_id,
            session_id=session_id
        )
        
        if chat_result['success']:
            data = chat_result['data']
            session_id = data['session_id']  # 保存會話 ID
            
            print(f"      ✅ 聊天成功")
            print(f"      🤖 回答長度: {len(data['answer'])} 字符")
            print(f"      📖 參考來源: {len(data['sources'])} 個")
            print(f"      🔗 會話 ID: {session_id}")
            
            # 顯示回答預覽
            answer_preview = data['answer'][:100] + '...' if len(data['answer']) > 100 else data['answer']
            print(f"      📝 回答預覽: {answer_preview}")
        else:
            print(f"      ❌ 聊天失敗: {chat_result.get('error', '未知錯誤')}")
    
    # 4. 測試會話管理
    print("\n4. 📊 測試會話管理端點...")
    sessions_result = tester.test_get_sessions()
    
    if sessions_result['success']:
        sessions = sessions_result['data']
        print(f"   ✅ 成功獲取 {len(sessions)} 個活躍會話")
        
        for session in sessions:
            print(f"   🔗 會話: {session['session_id'][:16]}...")
            print(f"      數據集: {session['dataset_name']}")
            print(f"      創建時間: {session['created_at']}")
    else:
        print(f"   ❌ 獲取會話失敗: {sessions_result.get('error', '未知錯誤')}")
    
    print("\n" + "=" * 50)
    print("✨ 測試完成！")
    
    # 測試總結
    print("\n📋 測試總結:")
    print(f"   ✅ 健康檢查: {'通過' if health_result['success'] else '失敗'}")
    print(f"   ✅ 數據集獲取: {'通過' if datasets_result['success'] else '失敗'}")
    print(f"   ✅ 聊天功能: 測試了 {len(test_questions)} 個問題")
    print(f"   ✅ 會話管理: {'通過' if sessions_result['success'] else '失敗'}")

def wait_for_server(max_wait_time: int = 30):
    """等待服務器啟動"""
    print("⏳ 等待 FastAPI 服務器啟動...")
    
    tester = FastAPITester()
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            result = tester.test_health_check()
            if result['success']:
                print("✅ 服務器已啟動")
                return True
        except:
            pass
        
        time.sleep(1)
        print(".", end="", flush=True)
    
    print(f"\n❌ 服務器在 {max_wait_time} 秒內未啟動")
    return False

if __name__ == "__main__":
    print("🚀 FastAPI 服務測試工具")
    print("請確保 FastAPI 服務器正在運行")
    print("啟動命令: python3 fastapi_server.py")
    print()
    
    # 等待服務器啟動
    if wait_for_server():
        # 運行測試
        run_comprehensive_test()
        
        print("\n💡 提示:")
        print("- API 文檔: http://localhost:8000/docs")
        print("- ReDoc 文檔: http://localhost:8000/redoc")
        print("- 健康檢查: http://localhost:8000/")
    else:
        print("❌ 無法連接到 FastAPI 服務器")
        print("請檢查服務器是否正在運行")