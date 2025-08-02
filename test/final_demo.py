#!/usr/bin/env python3
"""
RAGFlow 聊天機器人最終演示
展示所有基於官方 API 的聊天機器人實現
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

def show_menu():
    """顯示選單"""
    print("\n🤖 RAGFlow 聊天機器人演示選單")
    print("=" * 50)
    print("1. 🔍 API 連線測試")
    print("2. 📚 知識庫列表")
    print("3. 🤖 完整功能聊天機器人 (推薦)")
    print("4. ⚡ 簡化版聊天機器人")
    print("5. 🌐 Web 聊天機器人")
    print("6. 📊 所有工具對比")
    print("7. 🧪 運行自動測試")
    print("8. 退出")
    print("-" * 50)

def run_api_test():
    """運行 API 測試"""
    print_section("API 連線測試")
    try:
        result = subprocess.run([
            sys.executable, 'ragflow_test.py'
        ], timeout=30)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ 測試超時")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def run_chatbot(script_name, description):
    """運行聊天機器人"""
    print_section(f"{description}")
    print(f"🚀 啟動 {script_name}...")
    print("注意: 這將啟動交互式程序")
    
    try:
        input("按 Enter 繼續，或 Ctrl+C 取消...")
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print("\n❌ 用戶取消")

def show_comparison():
    """顯示工具對比"""
    print_section("聊天機器人工具對比")
    
    tools = [
        {
            'name': 'ragflow_official_chatbot.py',
            'description': '完整功能聊天機器人',
            'features': ['✅ 數據集選擇', '✅ 會話管理', '✅ 詳細回答', '✅ 來源引用', '✅ 自動測試'],
            'use_case': '完整功能演示和開發參考'
        },
        {
            'name': 'ragflow_simple_official.py',
            'description': '簡化版聊天機器人',
            'features': ['✅ 自動選擇數據集', '✅ 快速設置', '✅ 基本問答', '✅ 來源引用'],
            'use_case': '快速測試和簡單集成'
        },
        {
            'name': 'web_chatbot.py',
            'description': 'Web 界面聊天機器人',
            'features': ['✅ Web 界面', '✅ 響應式設計', '✅ 會話歷史', '✅ 多數據集支持'],
            'use_case': 'Web 應用和用戶界面'
        },
        {
            'name': 'simple_chatbot_fixed.py',
            'description': '修復版聊天機器人 (舊版)',
            'features': ['⚠️ 舊版 API', '✅ 基本功能', '✅ 自動測試'],
            'use_case': '向後兼容性參考'
        }
    ]
    
    for tool in tools:
        print(f"\n📁 {tool['name']}")
        print(f"   描述: {tool['description']}")
        print(f"   功能: {', '.join(tool['features'])}")
        print(f"   適用: {tool['use_case']}")

def run_auto_test():
    """運行自動測試"""
    print_section("自動測試所有聊天機器人")
    
    tests = [
        ('ragflow_simple_official.py', '簡化版聊天機器人'),
        ('ragflow_official_chatbot.py', '完整功能聊天機器人')
    ]
    
    for script, name in tests:
        print(f"\n🧪 測試 {name}...")
        try:
            # 運行自動測試部分
            result = subprocess.run([
                sys.executable, '-c', f"""
import {script.replace('.py', '')}

# 測試基本功能
try:
    if hasattr({script.replace('.py', '')}, 'SimpleRAGFlowBot'):
        bot = {script.replace('.py', '')}.SimpleRAGFlowBot()
        dataset = bot.get_first_dataset()
        if dataset:
            print(f"✅ {name} - 數據集獲取成功: {{dataset.get('name')}}")
            if bot.setup_chat(dataset.get('id')):
                print(f"✅ {name} - 聊天環境設置成功")
                result = bot.ask("測試問題")
                if result:
                    print(f"✅ {name} - 問答功能正常")
                else:
                    print(f"❌ {name} - 問答功能失敗")
            else:
                print(f"❌ {name} - 聊天環境設置失敗")
        else:
            print(f"❌ {name} - 數據集獲取失敗")
    else:
        print(f"⚠️ {name} - 跳過自動測試（需要交互）")
except Exception as e:
    print(f"❌ {name} - 測試異常: {{e}}")
                """
            ], capture_output=True, text=True, timeout=60)
            
            print(result.stdout)
            if result.stderr:
                print(f"錯誤: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {name} - 測試超時")
        except Exception as e:
            print(f"❌ {name} - 測試失敗: {e}")

def main():
    """主程序"""
    print_header("RAGFlow 聊天機器人最終演示")
    
    print("🎯 本演示展示基於官方 RAGFlow Python API 的聊天機器人實現")
    print("📖 參考文檔: https://ragflow.io/docs/dev/python_api_reference")
    print()
    print("✨ 特色功能:")
    print("  • 基於官方 API 文檔的標準實現")
    print("  • 支持多種使用場景和複雜度")
    print("  • 完整的錯誤處理和會話管理")
    print("  • Web 界面和命令行界面")
    
    while True:
        show_menu()
        
        try:
            choice = input("\n請選擇 [1-8]: ").strip()
            
            if choice == '1':
                run_api_test()
                input("\n按 Enter 繼續...")
                
            elif choice == '2':
                print_section("知識庫列表")
                subprocess.run([sys.executable, '-c', """
from ragflow_official_chatbot import RAGFlowOfficialClient
client = RAGFlowOfficialClient()
result = client.list_datasets()
if result['success']:
    print(f"✅ 找到 {len(result['data'])} 個數據集:")
    for i, ds in enumerate(result['data'], 1):
        print(f"  {i}. {ds.get('name', 'N/A')} (ID: {ds.get('id', 'N/A')})")
        print(f"     文件數量: {ds.get('document_count', 'N/A')}")
else:
    print(f"❌ 獲取失敗: {result['message']}")
                """])
                input("\n按 Enter 繼續...")
                
            elif choice == '3':
                run_chatbot('ragflow_official_chatbot.py', '完整功能聊天機器人')
                
            elif choice == '4':
                run_chatbot('ragflow_simple_official.py', '簡化版聊天機器人')
                
            elif choice == '5':
                print_section("Web 聊天機器人")
                print("🌐 啟動 Web 聊天機器人...")
                print("啟動後請訪問: http://localhost:5000")
                try:
                    input("按 Enter 繼續，或 Ctrl+C 取消...")
                    subprocess.run([sys.executable, 'web_chatbot.py'])
                except KeyboardInterrupt:
                    print("\n❌ 用戶取消")
                
            elif choice == '6':
                show_comparison()
                input("\n按 Enter 繼續...")
                
            elif choice == '7':
                run_auto_test()
                input("\n按 Enter 繼續...")
                
            elif choice == '8':
                print("👋 感謝使用 RAGFlow 聊天機器人演示！")
                break
                
            else:
                print("❌ 無效選擇，請重新輸入")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序被中斷，再見！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()