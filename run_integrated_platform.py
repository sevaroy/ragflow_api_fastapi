#!/usr/bin/env python3
"""
RAGFlow 整合平台啟動腳本
一鍵啟動完整的聊天和評估系統
"""

import os
import sys
import subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv

def check_dependencies():
    """檢查必要的依賴包"""
    required_packages = [
        'streamlit',
        'streamlit-chat',
        'plotly',
        'pandas',
        'numpy',
        'requests',
        'python-dotenv'
    ]
    
    optional_packages = [
        'ragas',
        'datasets'
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            elif package == 'streamlit-chat':
                __import__('streamlit_chat')
            else:
                __import__(package)
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print("❌ 缺少必要依賴包:")
        for package in missing_required:
            print(f"  - {package}")
        print("\n請安裝缺少的包:")
        print(f"pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print("⚠️ 缺少可選依賴包 (RAGAS 功能將受限):")
        for package in missing_optional:
            print(f"  - {package}")
        print("\n如需完整功能，請安裝:")
        print(f"pip install {' '.join(missing_optional)}")
    
    return True

def test_ragflow_connection():
    """測試 RAGFlow API 連線"""
    api_url = os.getenv('RAGFLOW_API_URL')
    api_key = os.getenv('RAGFLOW_API_KEY')
    
    if not api_url or not api_key:
        return False, "API URL 或 API Key 未設置"
    
    try:
        # 測試基本連線
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code != 200:
            return False, f"服務器回應狀態碼: {response.status_code}"
        
        # 測試 API 認證
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f"{api_url}/api/v1/datasets", headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            dataset_count = len(data.get('data', []))
            return True, f"連線成功，找到 {dataset_count} 個數據集"
        elif response.status_code == 401:
            return False, "API Key 無效或已過期"
        else:
            return False, f"API 請求失敗: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        return False, "無法連接到 RAGFlow 服務器"
    except requests.exceptions.Timeout:
        return False, "連線超時"
    except Exception as e:
        return False, f"連線錯誤: {str(e)}"

def setup_environment():
    """設置運行環境"""
    # 載入 .env 文件
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ 已載入 .env 配置文件")
    else:
        print("ℹ️ 未找到 .env 文件，使用系統環境變數")
    
    # 創建必要的目錄
    os.makedirs('data/evaluations', exist_ok=True)
    os.makedirs('data/conversations', exist_ok=True)
    
    # 檢查環境變數
    env_vars = ['RAGFLOW_API_URL', 'RAGFLOW_API_KEY', 'OPENAI_API_KEY']
    
    print("\n🔧 環境變數檢查:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(8, len(str(value)))}{'...' if len(str(value)) > 8 else ''}")
        else:
            print(f"  ⚠️ {var}: 未設置")
    
    # 測試 RAGFlow 連線
    print("\n🔍 測試 RAGFlow 連線...")
    success, message = test_ragflow_connection()
    if success:
        print(f"  ✅ {message}")
    else:
        print(f"  ❌ {message}")
        print("  💡 請在 .env 文件中正確配置 RAGFLOW_API_URL 和 RAGFLOW_API_KEY")
    
    print()

def main():
    """主函數"""
    print("🚀 RAGFlow 整合智能平台")
    print("=" * 50)
    
    # 檢查依賴
    print("📦 檢查依賴包...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ 依賴檢查完成\n")
    
    # 設置環境
    print("🔧 設置運行環境...")
    setup_environment()
    
    # 啟動應用
    print("🌟 啟動 RAGFlow 整合平台...")
    print("📍 訪問地址: http://localhost:8501")
    print("🔧 配置頁面: http://localhost:8501 -> 系統設置")
    print("\n💡 使用提示:")
    ragflow_connected = os.getenv('RAGFLOW_API_KEY') and os.getenv('RAGFLOW_API_URL')
    if ragflow_connected:
        print("1. ✅ RAGFlow API 已配置，可直接使用所有功能")
        print("2. 在 '💬 智能聊天' 中選擇知識庫並進行對話")
        print("3. 在 '📏 RAGAS 評估' 中執行評估分析")
        print("4. 在 '📊 數據儀表板' 中查看評估結果")
        print("5. 在 '⚙️ 系統設置' 中調整配置參數")
    else:
        print("1. ⚠️ 請先在 '⚙️ 系統設置' 中配置 RAGFlow API")
        print("2. 或編輯 .env 文件設置 RAGFLOW_API_URL 和 RAGFLOW_API_KEY")
        print("3. 配置完成後即可使用完整功能")
    print("\n" + "=" * 50)
    
    try:
        # 啟動 Streamlit 應用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "integrated_ragflow_platform.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 感謝使用 RAGFlow 整合平台！")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()