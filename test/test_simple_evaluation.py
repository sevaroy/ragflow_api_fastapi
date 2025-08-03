#!/usr/bin/env python3
"""
測試簡化版評估功能
"""

import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_connection():
    """測試基本連接"""
    try:
        from deepeval_integration import RAGFlowEvaluator
        
        print("🔍 測試 RAGFlow 連接...")
        evaluator = RAGFlowEvaluator()
        
        # 測試數據集獲取
        datasets_result = evaluator.client.list_datasets()
        if datasets_result['success']:
            datasets = datasets_result['data']
            print(f"✅ 成功獲取 {len(datasets)} 個數據集")
            
            if datasets:
                dataset = datasets[0]
                print(f"📚 第一個數據集: {dataset['name']}")
                
                # 測試聊天機器人設置
                if evaluator.setup_chatbot(dataset['id'], dataset['name']):
                    print("✅ 聊天機器人設置成功")
                    
                    # 測試簡單問答
                    test_question = "這個知識庫包含什麼內容？"
                    result = evaluator.chatbot.ask(test_question)
                    
                    if result['success']:
                        print(f"✅ 測試問答成功")
                        print(f"問題: {test_question}")
                        print(f"回答: {result['answer'][:100]}...")
                        print(f"來源數量: {len(result['sources'])}")
                    else:
                        print(f"❌ 測試問答失敗: {result['message']}")
                else:
                    print("❌ 聊天機器人設置失敗")
            else:
                print("⚠️ 沒有可用的數據集")
        else:
            print(f"❌ 獲取數據集失敗: {datasets_result['message']}")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

def test_manual_generation():
    """測試手動問題生成"""
    try:
        from deepeval_integration import RAGFlowEvaluator
        
        print("\n🔍 測試手動問題生成...")
        evaluator = RAGFlowEvaluator()
        
        # 獲取數據集
        datasets_result = evaluator.client.list_datasets()
        if datasets_result['success'] and datasets_result['data']:
            dataset = datasets_result['data'][0]
            dataset_id = dataset['id']
            
            # 設置聊天機器人
            if evaluator.setup_chatbot(dataset_id, dataset['name']):
                print("✅ 聊天機器人設置成功")
                
                # 測試手動生成
                test_data = evaluator._generate_manual_test_data(dataset_id, 2)
                
                if test_data:
                    print(f"✅ 成功生成 {len(test_data)} 個測試問題")
                    for i, data in enumerate(test_data):
                        print(f"\n問題 {i+1}:")
                        print(f"  問題: {data['question']}")
                        print(f"  答案: {data['expected_answer'][:100]}...")
                else:
                    print("❌ 沒有生成任何測試問題")
            else:
                print("❌ 聊天機器人設置失敗")
        else:
            print("❌ 無法獲取數據集")
            
    except Exception as e:
        print(f"❌ 手動生成測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 開始測試簡化版評估功能\n")
    
    # 測試基本連接
    test_basic_connection()
    
    # 測試手動生成
    test_manual_generation()
    
    print("\n🏁 測試完成")