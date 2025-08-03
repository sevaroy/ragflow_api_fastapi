#!/usr/bin/env python3
"""
配置檢查腳本
檢查 RAGFlow 和 OpenAI API 的配置狀態
"""

import os
import sys
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY, OPENAI_API_KEY, OPENAI_MODEL

def check_ragflow_config():
    """檢查 RAGFlow 配置"""
    print("🔍 檢查 RAGFlow 配置...")
    
    if RAGFLOW_API_URL:
        print(f"✅ RAGFlow API URL: {RAGFLOW_API_URL}")
    else:
        print("❌ RAGFlow API URL 未設置")
        return False
    
    if RAGFLOW_API_KEY:
        # 隱藏大部分 key 內容
        masked_key = f"{RAGFLOW_API_KEY[:10]}...{RAGFLOW_API_KEY[-6:]}"
        print(f"✅ RAGFlow API Key: {masked_key}")
    else:
        print("❌ RAGFlow API Key 未設置")
        return False
    
    # 測試 RAGFlow 連接
    try:
        from ragflow_chatbot import RAGFlowOfficialClient
        client = RAGFlowOfficialClient()
        result = client.list_datasets()
        
        if result['success']:
            datasets = result['data']
            print(f"✅ RAGFlow 連接成功，找到 {len(datasets)} 個數據集")
            return True
        else:
            print(f"❌ RAGFlow 連接失敗: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ RAGFlow 連接測試失敗: {e}")
        return False

def check_openai_config():
    """檢查 OpenAI 配置"""
    print("\n🔍 檢查 OpenAI 配置...")
    
    if OPENAI_API_KEY:
        # 隱藏大部分 key 內容
        masked_key = f"{OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}"
        print(f"✅ OpenAI API Key: {masked_key}")
        print(f"✅ OpenAI Model: {OPENAI_MODEL}")
        
        # 測試 OpenAI API 連接
        try:
            import openai
            
            # 設置 API Key
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # 簡單的 API 測試
            models = client.models.list()
            print("✅ OpenAI API 連接成功")
            
            # 檢查指定模型是否可用
            available_models = [model.id for model in models.data]
            if OPENAI_MODEL in available_models:
                print(f"✅ 模型 {OPENAI_MODEL} 可用")
            else:
                print(f"⚠️  模型 {OPENAI_MODEL} 可能不可用")
                print("   可用模型示例:", available_models[:5])
            
            return True
            
        except Exception as e:
            print(f"❌ OpenAI API 連接失敗: {e}")
            return False
    else:
        print("⚠️  OpenAI API Key 未設置")
        print("   DeepEval 高級功能將無法使用")
        print("   基本評估功能仍可正常運行")
        return None  # 不是錯誤，只是功能受限

def check_dependencies():
    """檢查依賴包"""
    print("\n🔍 檢查依賴包...")
    
    required_packages = [
        'requests',
        'deepeval',
        'openai',
        'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依賴包: {', '.join(missing_packages)}")
        print("請運行: pip install -r requirements.txt")
        return False
    
    return True

def print_config_summary():
    """打印配置摘要"""
    print("\n📋 配置摘要")
    print("=" * 40)
    print(f"RAGFlow API URL: {RAGFLOW_API_URL}")
    print(f"RAGFlow API Key: {'已設置' if RAGFLOW_API_KEY else '未設置'}")
    print(f"OpenAI API Key: {'已設置' if OPENAI_API_KEY else '未設置'}")
    print(f"OpenAI Model: {OPENAI_MODEL}")
    
    print(f"\n🎯 功能狀態:")
    print(f"RAGFlow 聊天機器人: {'✅ 可用' if RAGFLOW_API_KEY else '❌ 不可用'}")
    print(f"DeepEval 基礎評估: {'✅ 可用' if RAGFLOW_API_KEY else '❌ 不可用'}")
    print(f"DeepEval 高級評估: {'✅ 可用' if OPENAI_API_KEY else '⚠️  受限'}")

def provide_setup_guidance():
    """提供設置指導"""
    print("\n🔧 設置指導")
    print("=" * 40)
    
    if not RAGFLOW_API_KEY:
        print("❗ RAGFlow API Key 未設置:")
        print("   export RAGFLOW_API_KEY='your-ragflow-api-key'")
    
    if not OPENAI_API_KEY:
        print("💡 OpenAI API Key 未設置 (可選):")
        print("   export OPENAI_API_KEY='your-openai-api-key'")
        print("   這將啟用 DeepEval 的高級評估功能")
    
    print(f"\n📚 相關文檔:")
    print("   - OpenAI 配置指南: OPENAI_CONFIG_GUIDE.md")
    print("   - DeepEval 使用指南: DEEPEVAL_GUIDE.md")
    print("   - 完整更新報告: deepeval_note.md")

def main():
    """主函數"""
    print("🔧 RAGFlow + DeepEval 配置檢查")
    print("=" * 50)
    
    # 檢查依賴
    deps_ok = check_dependencies()
    
    # 檢查 RAGFlow 配置
    ragflow_ok = check_ragflow_config()
    
    # 檢查 OpenAI 配置
    openai_ok = check_openai_config()
    
    # 打印摘要
    print_config_summary()
    
    # 提供指導
    if not ragflow_ok or not deps_ok:
        provide_setup_guidance()
        sys.exit(1)
    
    if openai_ok is None:  # OpenAI 未配置但不是錯誤
        print("\n💡 提示: 配置 OpenAI API Key 可啟用更多評估功能")
    
    print("\n🎉 配置檢查完成！")
    
    if ragflow_ok:
        print("\n🚀 你現在可以:")
        print("   1. 運行基本聊天機器人: python3 ragflow_chatbot.py")
        print("   2. 運行 DeepEval 演示: python3 test/deepeval_demo.py")
        print("   3. 運行完整評估: python3 test/run_deepeval_test.py")

if __name__ == "__main__":
    main()