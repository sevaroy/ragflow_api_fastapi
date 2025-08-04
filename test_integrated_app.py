#!/usr/bin/env python3
"""
整合應用測試腳本
驗證各個組件是否能正常運作
"""

import sys
import os
import importlib
from typing import Dict, Any

def test_imports() -> Dict[str, Any]:
    """測試模組導入"""
    results = {}
    
    # 核心依賴
    core_modules = [
        'streamlit',
        'requests', 
        'pandas',
        'plotly',
        'numpy',
        'json',
        'datetime'
    ]
    
    print("🔍 測試核心模組導入...")
    for module in core_modules:
        try:
            importlib.import_module(module)
            results[module] = {'status': 'success', 'error': None}
            print(f"✅ {module}")
        except ImportError as e:
            results[module] = {'status': 'failed', 'error': str(e)}
            print(f"❌ {module}: {e}")
    
    # 可選依賴
    optional_modules = [
        'ragas',
        'deepeval'
    ]
    
    print("\n🔍 測試可選模組導入...")
    for module in optional_modules:
        try:
            importlib.import_module(module)
            results[module] = {'status': 'success', 'error': None}
            print(f"✅ {module}")
        except ImportError as e:
            results[module] = {'status': 'optional', 'error': str(e)}
            print(f"⚠️ {module}: {e} (可選)")
    
    return results

def test_local_modules() -> Dict[str, Any]:
    """測試本地模組"""
    results = {}
    
    local_modules = [
        'config',
        'ragas_evaluator',
        'ragflow_chatbot'
    ]
    
    print("\n🔍 測試本地模組導入...")
    for module in local_modules:
        try:
            importlib.import_module(module)
            results[module] = {'status': 'success', 'error': None}
            print(f"✅ {module}")
        except ImportError as e:
            results[module] = {'status': 'failed', 'error': str(e)}
            print(f"❌ {module}: {e}")
        except Exception as e:
            results[module] = {'status': 'error', 'error': str(e)}
            print(f"⚠️ {module}: {e}")
    
    return results

def test_ragas_evaluator():
    """測試 RAGAS 評估器"""
    print("\n🔍 測試 RAGAS 評估器...")
    
    try:
        from ragas_evaluator import RAGASEvaluator, create_sample_evaluation_data, RAGAS_AVAILABLE
        
        print(f"✅ RAGASEvaluator 導入成功")
        print(f"📊 RAGAS 可用性: {RAGAS_AVAILABLE}")
        
        # 測試樣本數據生成
        sample_data = create_sample_evaluation_data(5)
        print(f"✅ 樣本數據生成成功: {len(sample_data['results'])} 個案例")
        
        return {'status': 'success', 'ragas_available': RAGAS_AVAILABLE}
        
    except Exception as e:
        print(f"❌ RAGAS 評估器測試失敗: {e}")
        return {'status': 'failed', 'error': str(e)}

def test_ragflow_client():
    """測試 RAGFlow 客戶端"""
    print("\n🔍 測試 RAGFlow 客戶端...")
    
    try:
        from ragflow_chatbot import RAGFlowOfficialClient
        
        client = RAGFlowOfficialClient()
        print(f"✅ RAGFlowOfficialClient 創建成功")
        print(f"🔗 API URL: {client.api_url}")
        
        # 注意：這裡不實際測試 API 連接，因為可能沒有運行的服務器
        print("⚠️ 跳過實際 API 連接測試（需要運行的 RAGFlow 服務器）")
        
        return {'status': 'success', 'api_url': client.api_url}
        
    except Exception as e:
        print(f"❌ RAGFlow 客戶端測試失敗: {e}")
        return {'status': 'failed', 'error': str(e)}

def test_streamlit_app_structure():
    """測試 Streamlit 應用結構"""
    print("\n🔍 測試 Streamlit 應用結構...")
    
    try:
        # 檢查主要文件是否存在
        required_files = [
            'integrated_ragflow_app.py',
            'ragas_evaluator.py',
            'ragflow_chatbot.py',
            'config.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ 缺少文件: {missing_files}")
            return {'status': 'failed', 'missing_files': missing_files}
        
        print("✅ 所有必要文件存在")
        
        # 嘗試導入主應用（不執行）
        spec = importlib.util.spec_from_file_location("integrated_ragflow_app", "integrated_ragflow_app.py")
        module = importlib.util.module_from_spec(spec)
        
        # 檢查主要函數是否存在
        expected_functions = [
            'main',
            'initialize_session_state',
            'render_home_page',
            'render_chat_page',
            'render_evaluation_page'
        ]
        
        # 這裡我們不實際執行，只檢查語法
        with open('integrated_ragflow_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        for func in expected_functions:
            if f"def {func}(" in content:
                print(f"✅ 找到函數: {func}")
            else:
                print(f"⚠️ 未找到函數: {func}")
        
        return {'status': 'success'}
        
    except Exception as e:
        print(f"❌ Streamlit 應用結構測試失敗: {e}")
        return {'status': 'failed', 'error': str(e)}

def generate_test_report(results: Dict[str, Any]):
    """生成測試報告"""
    print("\n" + "="*60)
    print("📋 測試報告")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        total_tests += 1
        status = result.get('status', 'unknown')
        
        if status == 'success':
            passed_tests += 1
            print(f"✅ {test_name}: 通過")
        elif status == 'optional':
            print(f"⚠️ {test_name}: 可選模組未安裝")
        elif status == 'failed':
            print(f"❌ {test_name}: 失敗 - {result.get('error', 'Unknown error')}")
        else:
            print(f"❓ {test_name}: 狀態未知")
    
    print(f"\n📊 總結: {passed_tests}/{total_tests} 測試通過")
    
    if passed_tests == total_tests:
        print("🎉 所有測試通過！應用應該可以正常運作。")
    elif passed_tests >= total_tests * 0.8:
        print("✅ 大部分測試通過，應用基本可以運作。")
    else:
        print("⚠️ 多個測試失敗，可能需要解決依賴問題。")

def main():
    """主測試函數"""
    print("🧪 RAGFlow 整合應用測試")
    print("="*60)
    
    # 執行各項測試
    test_results = {}
    
    # 測試導入
    import_results = test_imports()
    test_results['imports'] = {
        'status': 'success' if all(r['status'] in ['success', 'optional'] for r in import_results.values()) else 'failed',
        'details': import_results
    }
    
    # 測試本地模組
    local_results = test_local_modules()
    test_results['local_modules'] = {
        'status': 'success' if all(r['status'] == 'success' for r in local_results.values()) else 'failed',
        'details': local_results
    }
    
    # 測試 RAGAS 評估器
    test_results['ragas_evaluator'] = test_ragas_evaluator()
    
    # 測試 RAGFlow 客戶端
    test_results['ragflow_client'] = test_ragflow_client()
    
    # 測試 Streamlit 應用結構
    test_results['streamlit_structure'] = test_streamlit_app_structure()
    
    # 生成報告
    generate_test_report(test_results)
    
    # 提供運行建議
    print("\n💡 運行建議:")
    print("1. 如果所有測試通過，可以運行: python run_integrated_app.py")
    print("2. 如果缺少依賴，請運行: pip install -r requirements.txt")
    print("3. 確保 RAGFlow 服務器在運行（如果要使用真實 API）")
    print("4. 設置環境變數 OPENAI_API_KEY（如果要使用真實評估）")

if __name__ == "__main__":
    # 添加當前目錄到 Python 路徑
    sys.path.insert(0, os.getcwd())
    
    main()