#!/usr/bin/env python3
"""
統一測試啟動腳本
運行所有測試程式
"""

import subprocess
import sys
import os
import time

def print_header(title):
    """打印標題"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title):
    """打印章節"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_test(script_name, description, timeout=60):
    """運行測試腳本"""
    print(f"\n🚀 運行 {description}...")
    print(f"腳本: {script_name}")
    
    if not os.path.exists(script_name):
        print(f"❌ 找不到測試腳本: {script_name}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"✅ {description} - 測試通過")
            # 顯示輸出的前幾行
            output_lines = result.stdout.split('\n')[:10]
            for line in output_lines:
                if line.strip():
                    print(f"   {line}")
            if len(result.stdout.split('\n')) > 10:
                print("   ...")
            return True
        else:
            print(f"❌ {description} - 測試失敗")
            print(f"錯誤輸出: {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - 測試超時")
        return False
    except Exception as e:
        print(f"❌ {description} - 運行異常: {e}")
        return False

def main():
    """主測試函數"""
    print_header("RAGFlow 項目全面測試")
    
    print("🎯 本腳本將運行所有測試程式，驗證項目功能")
    print("📁 測試腳本位置: test/ 資料夾")
    
    # 測試列表
    tests = [
        {
            'script': 'ragflow_test.py',
            'description': 'RAGFlow API 連線測試',
            'timeout': 30
        },
        {
            'script': 'test_api_endpoints.py',
            'description': 'API 端點功能測試',
            'timeout': 60
        },
        {
            'script': 'test_fastapi.py',
            'description': 'FastAPI 服務測試',
            'timeout': 60
        },
        {
            'script': 'test_streamlit.py',
            'description': 'Streamlit 應用測試',
            'timeout': 30
        },
        {
            'script': 'api_client_example.py',
            'description': 'API 客戶端示例',
            'timeout': 90
        }
    ]
    
    # 運行測試
    results = []
    
    for test in tests:
        success = run_test(
            test['script'],
            test['description'],
            test['timeout']
        )
        results.append({
            'name': test['description'],
            'success': success
        })
    
    # 測試總結
    print_header("測試總結")
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"📊 測試結果: {passed}/{total} 通過")
    print()
    
    for result in results:
        status = "✅ 通過" if result['success'] else "❌ 失敗"
        print(f"  {status} - {result['name']}")
    
    if passed == total:
        print(f"\n🎉 所有測試通過！項目功能正常。")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 個測試失敗，請檢查相關功能。")
        return False

def show_test_menu():
    """顯示測試選單"""
    print_header("測試選單")
    
    tests = [
        ('ragflow_test.py', 'RAGFlow API 連線測試'),
        ('test_api_endpoints.py', 'API 端點功能測試'),
        ('test_fastapi.py', 'FastAPI 服務測試'),
        ('test_streamlit.py', 'Streamlit 應用測試'),
        ('api_client_example.py', 'API 客戶端示例'),
        ('final_demo.py', '完整演示程序'),
        ('demo.py', '基礎演示程序')
    ]
    
    print("選擇要運行的測試:")
    print("0. 運行所有測試")
    
    for i, (script, desc) in enumerate(tests, 1):
        print(f"{i}. {desc} ({script})")
    
    print(f"{len(tests) + 1}. 退出")
    
    try:
        choice = int(input(f"\n請選擇 [0-{len(tests) + 1}]: "))
        
        if choice == 0:
            return main()
        elif 1 <= choice <= len(tests):
            script, desc = tests[choice - 1]
            return run_test(script, desc)
        elif choice == len(tests) + 1:
            print("👋 再見！")
            return True
        else:
            print("❌ 無效選擇")
            return False
            
    except (ValueError, KeyboardInterrupt):
        print("\n👋 程序被中斷")
        return False

if __name__ == "__main__":
    print("🧪 RAGFlow 測試工具")
    print("選擇運行模式:")
    print("1. 運行所有測試")
    print("2. 選擇性測試")
    
    try:
        mode = input("\n請選擇模式 [1-2]: ").strip()
        
        if mode == "1":
            success = main()
            sys.exit(0 if success else 1)
        elif mode == "2":
            while True:
                if not show_test_menu():
                    break
        else:
            print("❌ 無效選擇")
            
    except KeyboardInterrupt:
        print("\n👋 程序被中斷，再見！")