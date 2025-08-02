#!/usr/bin/env python3
"""
RAGFlow API 和聊天機器人完整演示
展示所有功能的使用方法
"""

import subprocess
import sys
import time

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_section(title):
    """打印章節"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_demo():
    """運行完整演示"""
    print_header("RAGFlow API 和聊天機器人完整演示")
    
    print("這個演示將展示以下功能:")
    print("1. ✅ API 連線測試")
    print("2. 📚 知識庫列表")
    print("3. 🤖 RAG 聊天機器人")
    print("4. 🌐 Web 界面預覽")
    
    input("\n按 Enter 開始演示...")
    
    # 1. API 連線測試
    print_section("1. API 連線測試")
    print("正在測試 RAGFlow API 連線...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c', 
            """
import ragflow_test
from ragflow_test import RAGFlowClient
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

client = RAGFlowClient()
connection_result = client.test_connection()

if connection_result['success']:
    print(f"✅ API 連線成功")
    print(f"   回應時間: {connection_result['response_time']:.2f}s")
else:
    print(f"❌ API 連線失敗: {connection_result['message']}")
            """
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("錯誤:", result.stderr)
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    input("\n按 Enter 繼續...")
    
    # 2. 知識庫列表
    print_section("2. 知識庫列表")
    print("正在獲取知識庫列表...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c',
            """
import ragflow_test
from ragflow_test import RAGFlowClient

client = RAGFlowClient()
kb_result = client.list_knowledge_bases()

if kb_result['success']:
    print(f"✅ 找到 {len(kb_result['data'])} 個知識庫:")
    for i, kb in enumerate(kb_result['data'], 1):
        print(f"  {i}. {kb.get('name', 'N/A')}")
        print(f"     ID: {kb.get('id', 'N/A')}")
        print(f"     文件數量: {kb.get('document_count', 'N/A')}")
else:
    print(f"❌ 獲取失敗: {kb_result['message']}")
            """
        ], capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("錯誤:", result.stderr)
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    input("\n按 Enter 繼續...")
    
    # 3. RAG 聊天機器人演示
    print_section("3. RAG 聊天機器人演示")
    print("正在演示聊天機器人功能...")
    
    try:
        result = subprocess.run([
            sys.executable, '-c',
            """
import simple_chatbot_fixed

# 獲取知識庫
kb = simple_chatbot_fixed.get_first_knowledge_base()
if kb:
    print(f"✅ 使用知識庫: {kb.get('name')}")
    
    # 測試問答
    test_questions = [
        "這個知識庫包含什麼內容？",
        "請簡單介紹主要概念"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\\n{i}. ❓ {question}")
        result = simple_chatbot_fixed.ask_question(question, kb.get('id'))
        
        if result['success']:
            if result['answer']:
                print(f"   🤖 回答: {result['answer'][:100]}...")
                print(f"   📖 來源: {len(result['sources'])} 個")
            else:
                print("   🤖 沒有找到相關內容")
        else:
            print(f"   ❌ 錯誤: {result['error']}")
else:
    print("❌ 無法獲取知識庫")
            """
        ], capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("錯誤:", result.stderr)
            
    except Exception as e:
        print(f"❌ 演示失敗: {e}")
    
    input("\n按 Enter 繼續...")
    
    # 4. 可用工具總結
    print_section("4. 可用工具總結")
    print("以下是所有可用的工具和腳本:")
    print()
    
    tools = [
        ("ragflow_test.py", "基本 API 測試", "python3 ragflow_test.py"),
        ("simple_chatbot_fixed.py", "簡單聊天機器人", "python3 simple_chatbot_fixed.py"),
        ("rag_chatbot.py", "完整聊天機器人", "python3 rag_chatbot.py"),
        ("web_chatbot.py", "Web 聊天機器人", "python3 web_chatbot.py"),
        ("test_chatbots.py", "聊天機器人測試工具", "python3 test_chatbots.py"),
        ("run_test.sh", "一鍵啟動腳本", "./run_test.sh")
    ]
    
    for tool, desc, cmd in tools:
        print(f"📁 {tool:<25} - {desc}")
        print(f"   命令: {cmd}")
        print()
    
    print_section("演示完成")
    print("🎉 RAGFlow API 和聊天機器人演示完成！")
    print()
    print("你現在可以:")
    print("1. 運行任何上述工具進行測試")
    print("2. 修改配置文件適應你的需求")
    print("3. 基於這些範例開發自己的應用")
    print()
    print("如需幫助，請查看 README.md 文件")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 演示被中斷，再見！")
    except Exception as e:
        print(f"\n❌ 演示過程中發生錯誤: {e}")