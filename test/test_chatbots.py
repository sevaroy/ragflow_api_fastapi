#!/usr/bin/env python3
"""
RAGFlow 聊天機器人測試腳本
測試所有聊天機器人功能
"""

import subprocess
import sys
import time

def test_simple_chatbot():
    """測試簡單聊天機器人"""
    print("🤖 測試簡單聊天機器人")
    print("=" * 50)
    
    try:
        # 運行簡單聊天機器人的自動測試部分
        result = subprocess.run([
            sys.executable, 'simple_chatbot.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 簡單聊天機器人測試成功")
            print("輸出預覽:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("❌ 簡單聊天機器人測試失敗")
            print("錯誤:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ 測試超時（這是正常的，因為程序在等待用戶輸入）")
    except Exception as e:
        print(f"❌ 測試錯誤: {e}")

def show_chatbot_menu():
    """顯示聊天機器人選單"""
    print("\n🤖 RAGFlow 聊天機器人測試選單")
    print("=" * 50)
    print("1. 測試簡單聊天機器人 (simple_chatbot.py)")
    print("2. 運行完整聊天機器人 (rag_chatbot.py)")
    print("3. 啟動 Web 聊天機器人 (web_chatbot.py)")
    print("4. 查看所有聊天機器人文件")
    print("5. 退出")
    print("-" * 50)

def list_chatbot_files():
    """列出聊天機器人相關文件"""
    import os
    
    print("\n📁 聊天機器人相關文件:")
    print("-" * 30)
    
    files = [
        ('simple_chatbot.py', '簡單聊天機器人 - 基本問答功能'),
        ('rag_chatbot.py', '完整聊天機器人 - 交互式命令行界面'),
        ('web_chatbot.py', 'Web 聊天機器人 - Flask Web 界面'),
        ('templates/index.html', 'Web 界面模板'),
        ('config.py', 'API 配置文件'),
        ('requirements.txt', 'Python 依賴列表')
    ]
    
    for filename, description in files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename:<25} - {description} ({size} bytes)")
        else:
            print(f"❌ {filename:<25} - 文件不存在")

def main():
    """主程序"""
    print("🚀 RAGFlow 聊天機器人測試工具")
    print("=" * 50)
    
    while True:
        show_chatbot_menu()
        
        try:
            choice = input("\n請選擇 [1-5]: ").strip()
            
            if choice == '1':
                print("\n" + "="*50)
                test_simple_chatbot()
                input("\n按 Enter 繼續...")
                
            elif choice == '2':
                print("\n🚀 啟動完整聊天機器人...")
                print("注意: 這將啟動交互式程序")
                input("按 Enter 繼續，或 Ctrl+C 取消...")
                subprocess.run([sys.executable, 'rag_chatbot.py'])
                
            elif choice == '3':
                print("\n🌐 啟動 Web 聊天機器人...")
                print("注意: 這將啟動 Web 服務器")
                print("啟動後請訪問: http://localhost:5000")
                input("按 Enter 繼續，或 Ctrl+C 取消...")
                subprocess.run([sys.executable, 'web_chatbot.py'])
                
            elif choice == '4':
                list_chatbot_files()
                input("\n按 Enter 繼續...")
                
            elif choice == '5':
                print("👋 再見！")
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