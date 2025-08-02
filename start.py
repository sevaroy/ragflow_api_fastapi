#!/usr/bin/env python3
"""
RAGFlow 聊天機器人啟動器
選擇並啟動不同版本的聊天機器人
"""

import subprocess
import sys
import os

def show_menu():
    """顯示選單"""
    print("\n🤖 RAGFlow 聊天機器人啟動器")
    print("=" * 40)
    print("1. 🚀 完整功能聊天機器人")
    print("2. ⚡ 簡化版聊天機器人")
    print("3. 🌐 Web 界面聊天機器人")
    print("4. 🧪 運行測試")
    print("5. 退出")
    print("-" * 40)

def check_config():
    """檢查配置文件"""
    if not os.path.exists('config.py'):
        print("❌ 找不到 config.py 配置文件")
        print("請確保配置文件存在並包含正確的 API 設置")
        return False
    return True

def run_chatbot(script_name, description):
    """運行聊天機器人"""
    print(f"\n🚀 啟動 {description}...")
    try:
        subprocess.run([sys.executable, script_name])
    except KeyboardInterrupt:
        print(f"\n👋 {description} 已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

def run_tests():
    """運行測試"""
    print("\n🧪 運行測試...")
    test_files = [
        ('test/ragflow_test.py', 'API 連線測試'),
        ('test/final_demo.py', '完整演示程序')
    ]
    
    for test_file, description in test_files:
        if os.path.exists(test_file):
            print(f"\n📋 {description}")
            try:
                choice = input("是否運行此測試? (y/n): ").strip().lower()
                if choice in ['y', 'yes', '是']:
                    subprocess.run([sys.executable, test_file])
            except KeyboardInterrupt:
                print("\n⏭️  跳過此測試")
        else:
            print(f"❌ 找不到測試文件: {test_file}")

def main():
    """主程序"""
    print("🎯 RAGFlow 聊天機器人項目")
    print("基於官方 RAGFlow Python API 實現")
    
    # 檢查配置
    if not check_config():
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("\n請選擇 [1-5]: ").strip()
            
            if choice == '1':
                run_chatbot('ragflow_chatbot.py', '完整功能聊天機器人')
                
            elif choice == '2':
                run_chatbot('ragflow_simple.py', '簡化版聊天機器人')
                
            elif choice == '3':
                print("\n🌐 啟動 Web 聊天機器人...")
                print("啟動後請訪問: http://localhost:5000")
                input("按 Enter 繼續...")
                run_chatbot('web_chatbot.py', 'Web 聊天機器人')
                
            elif choice == '4':
                run_tests()
                
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