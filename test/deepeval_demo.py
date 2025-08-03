#!/usr/bin/env python3
"""
DeepEval 快速演示腳本
展示如何使用 DeepEval 評估 RAGFlow 聊天機器人
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deepeval_integration import RAGFlowEvaluator

def quick_demo():
    """快速演示 DeepEval 功能"""
    print("🚀 DeepEval 快速演示")
    print("=" * 40)
    
    # 創建評估器
    evaluator = RAGFlowEvaluator()
    
    # 獲取第一個可用數據集
    datasets_result = evaluator.client.list_datasets()
    if not datasets_result['success'] or not datasets_result['data']:
        print("❌ 無法獲取數據集")
        return
    
    dataset = datasets_result['data'][0]
    dataset_id = dataset['id']
    dataset_name = dataset['name']
    
    print(f"📖 使用數據集: {dataset_name}")
    
    # 設置聊天機器人
    if not evaluator.setup_chatbot(dataset_id, dataset_name):
        print("❌ 聊天機器人設置失敗")
        return
    
    # 生成 3 個測試問題
    print("\n📝 生成測試問題...")
    test_data = evaluator.generate_test_data_from_documents(dataset_id, 3)
    
    if not test_data:
        print("❌ 測試數據生成失敗")
        return
    
    print(f"✅ 生成了 {len(test_data)} 個測試問題:")
    for i, data in enumerate(test_data, 1):
        print(f"  {i}. {data['question']}")
    
    # 評估
    print("\n🧪 開始評估...")
    results = evaluator.evaluate_test_cases(test_data)
    
    if not results:
        print("❌ 評估失敗")
        return
    
    # 顯示結果
    print("\n📊 評估結果:")
    for i, result in enumerate(results, 1):
        status = "✅" if result.passed else "❌"
        print(f"{i}. {status} 分數: {result.overall_score:.2f}")
        print(f"   問題: {result.question}")
        print(f"   回答: {result.actual_output[:100]}...")
        print()
    
    # 生成簡單報告
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    avg_score = sum(r.overall_score for r in results) / total
    
    print(f"📈 總結:")
    print(f"   通過率: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"   平均分數: {avg_score:.3f}")
    
    print("\n🎉 演示完成！")

if __name__ == "__main__":
    quick_demo()