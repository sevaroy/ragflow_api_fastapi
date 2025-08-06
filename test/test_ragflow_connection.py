#!/usr/bin/env python3
"""
RAGFlow API 連線測試腳本
"""

import os
import requests
from dotenv import load_dotenv

def test_ragflow_connection():
    """測試 RAGFlow API 連線"""
    
    # 載入環境變數
    load_dotenv()
    
    api_url = os.getenv('RAGFLOW_API_URL', 'http://192.168.50.123:8080')
    api_key = os.getenv('RAGFLOW_API_KEY', '')
    
    print("🔍 RAGFlow API 連線測試")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"API Key: {'*' * min(8, len(api_key)) if api_key else '未設置'}")
    print()
    
    if not api_key:
        print("❌ 錯誤: 請在 .env 文件中設置 RAGFLOW_API_KEY")
        return False
    
    try:
        # 測試基本連線
        print("📡 測試服務器連線...")
        response = requests.get(f"{api_url}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ 服務器連線成功")
        else:
            print(f"⚠️ 服務器回應狀態碼: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 連線失敗: 無法連接到服務器")
        print("請檢查:")
        print("1. RAGFlow 服務是否正在運行")
        print("2. 網址是否正確")
        print("3. 網路連線是否正常")
        return False
    
    except requests.exceptions.Timeout:
        print("❌ 連線超時")
        return False
    
    except Exception as e:
        print(f"❌ 連線錯誤: {e}")
        return False
    
    try:
        # 測試 API 認證
        print("\n🔐 測試 API 認證...")
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # 嘗試獲取數據集列表
        response = requests.get(f"{api_url}/api/v1/datasets", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 認證成功")
            
            if 'data' in data and isinstance(data['data'], list):
                dataset_count = len(data['data'])
                print(f"📚 找到 {dataset_count} 個數據集")
                
                # 顯示前幾個數據集
                if dataset_count > 0:
                    print("\n📋 可用數據集:")
                    for i, dataset in enumerate(data['data'][:3]):
                        name = dataset.get('name', 'Unknown')
                        dataset_id = dataset.get('id', 'Unknown')
                        print(f"  {i+1}. {name} (ID: {dataset_id})")
                    
                    if dataset_count > 3:
                        print(f"  ... 還有 {dataset_count - 3} 個數據集")
            
            return True
            
        elif response.status_code == 401:
            print("❌ API Key 無效或已過期")
            return False
        
        else:
            print(f"⚠️ API 請求失敗: {response.status_code}")
            try:
                error_data = response.json()
                print(f"錯誤信息: {error_data}")
            except:
                print(f"錯誤內容: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ API 測試錯誤: {e}")
        return False

if __name__ == "__main__":
    success = test_ragflow_connection()
    
    if success:
        print("\n🎉 RAGFlow API 連線測試成功!")
        print("您可以開始使用整合平台的所有功能。")
    else:
        print("\n💡 解決建議:")
        print("1. 確認 RAGFlow 服務正在運行")
        print("2. 檢查 .env 文件中的 API URL 和 Key")
        print("3. 確認網路連線正常")
        print("4. 查看 RAGFlow 服務日誌")