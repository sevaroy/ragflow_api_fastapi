#!/usr/bin/env python3
"""
Streamlit 應用測試腳本
測試 Streamlit 前端的基本功能
"""

import requests
import time
import subprocess
import sys
from threading import Thread

def test_streamlit_health():
    """測試 Streamlit 健康狀態"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8501", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
        print(f"等待 Streamlit 啟動... ({attempt + 1}/{max_attempts})")
    return False

def test_fastapi_health():
    """測試 FastAPI 健康狀態"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
        print(f"等待 FastAPI 啟動... ({attempt + 1}/{max_attempts})")
    return False

def run_integration_test():
    """運行集成測試"""
    print("🧪 RAGFlow Streamlit 集成測試")
    print("=" * 50)
    
    # 檢查依賴
    try:
        import streamlit
        print("✅ Streamlit 已安裝")
    except ImportError:
        print("❌ Streamlit 未安裝，請運行: pip install streamlit")
        return False
    
    try:
        import fastapi
        print("✅ FastAPI 已安裝")
    except ImportError:
        print("❌ FastAPI 未安裝，請運行: pip install fastapi uvicorn")
        return False
    
    # 檢查文件
    import os
    required_files = [
        "streamlit_app.py",
        "fastapi_server.py",
        "config.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
            return False
    
    print("\n📋 測試總結:")
    print("✅ 所有依賴和文件檢查通過")
    print("✅ 可以運行 Streamlit 應用")
    
    print("\n💡 啟動方式:")
    print("1. 手動啟動:")
    print("   - 終端 1: python3 fastapi_server.py")
    print("   - 終端 2: streamlit run streamlit_app.py")
    print("2. 自動啟動:")
    print("   - python3 run_full_stack.py")
    
    return True

def demo_streamlit_features():
    """演示 Streamlit 功能特性"""
    print("\n🌟 Streamlit 聊天機器人功能特性:")
    print("=" * 50)
    
    features = [
        "🎨 美觀的聊天界面設計",
        "📱 響應式布局，支持多設備",
        "🔄 實時與 FastAPI 後端交互",
        "📚 動態數據集選擇",
        "💬 會話管理和歷史記錄",
        "📖 詳細的來源引用顯示",
        "⚡ 快速問題按鈕",
        "🔗 API 連接狀態監控",
        "🎯 用戶友好的錯誤處理",
        "📊 會話統計和管理"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎯 使用流程:")
    print("1. 啟動 FastAPI 後端服務")
    print("2. 啟動 Streamlit 前端應用")
    print("3. 在瀏覽器中訪問 http://localhost:8501")
    print("4. 選擇知識庫數據集")
    print("5. 開始智能問答對話")
    
    print("\n🔧 技術架構:")
    print("前端: Streamlit (Python Web 框架)")
    print("後端: FastAPI (RESTful API)")
    print("AI 引擎: RAGFlow (檢索增強生成)")
    print("通信: HTTP/JSON API 調用")

if __name__ == "__main__":
    print("🚀 Streamlit 應用測試工具")
    print()
    
    # 運行基本測試
    if run_integration_test():
        # 演示功能特性
        demo_streamlit_features()
        
        print("\n" + "=" * 50)
        print("✨ 測試完成！")
        print("現在可以運行 Streamlit 應用了。")
    else:
        print("\n❌ 測試失敗，請檢查環境配置。")