#!/usr/bin/env python3
"""
DeepEval 完整測試腳本
演示完整的 RAGFlow 評估流程
"""

import sys
import os
import json
from datetime import datetime

# 添加父目錄到路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deepeval_integration import RAGFlowEvaluator
from deepeval_config import DeepEvalConfig

def run_comprehensive_evaluation():
    """運行完整的評估流程"""
    print("🧪 RAGFlow DeepEval 完整評估")
    print("=" * 50)
    
    # 顯示配置狀態
    DeepEvalConfig.print_config_status()
    print()
    
    # 創建評估器
    evaluator = RAGFlowEvaluator()
    
    # 獲取數據集列表
    print("📚 獲取數據集列表...")
    datasets_result = evaluator.client.list_datasets()
    
    if not datasets_result['success']:
        print(f"❌ 獲取數據集失敗: {datasets_result['message']}")
        return False
    
    datasets = datasets_result['data']
    if not datasets:
        print("❌ 沒有可用的數據集")
        return False
    
    print(f"✅ 找到 {len(datasets)} 個數據集:")
    for i, dataset in enumerate(datasets, 1):
        doc_count = dataset.get('document_count', 'N/A')
        print(f"  {i}. {dataset.get('name', 'N/A')} ({doc_count} 文件)")
    
    # 選擇數據集進行評估
    results_summary = []
    
    for dataset in datasets[:2]:  # 評估前兩個數據集
        dataset_id = dataset['id']
        dataset_name = dataset['name']
        
        print(f"\n🔍 評估數據集: {dataset_name}")
        print("-" * 40)
        
        # 設置聊天機器人
        if not evaluator.setup_chatbot(dataset_id, dataset_name):
            print(f"❌ 數據集 {dataset_name} 設置失敗，跳過")
            continue
        
        # 生成測試數據
        print("📝 生成測試問題...")
        test_data = evaluator.generate_test_data_from_documents(
            dataset_id, 
            DeepEvalConfig.DEFAULT_QUESTION_COUNT
        )
        
        if not test_data:
            print(f"❌ 數據集 {dataset_name} 測試數據生成失敗，跳過")
            continue
        
        print(f"✅ 生成了 {len(test_data)} 個測試問題")
        
        # 顯示部分問題
        print("📋 測試問題預覽:")
        for i, data in enumerate(test_data[:3], 1):
            print(f"  {i}. {data['question']}")
        if len(test_data) > 3:
            print(f"  ... 還有 {len(test_data) - 3} 個問題")
        
        # 執行評估
        print("\n🧪 開始評估...")
        results = evaluator.evaluate_test_cases(test_data)
        
        if not results:
            print(f"❌ 數據集 {dataset_name} 評估失敗，跳過")
            continue
        
        # 生成報告
        report = evaluator.generate_report(results)
        print(report)
        
        # 保存結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{dataset_name}_{timestamp}.json"
        evaluator.save_results(results, filename)
        
        # 收集摘要信息
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.passed)
        avg_score = sum(r.overall_score for r in results) / total_cases
        
        results_summary.append({
            'dataset_name': dataset_name,
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'pass_rate': passed_cases / total_cases * 100,
            'avg_score': avg_score,
            'filename': filename
        })
    
    # 生成總體摘要
    if results_summary:
        print("\n📊 評估總結")
        print("=" * 50)
        
        for summary in results_summary:
            print(f"📖 {summary['dataset_name']}:")
            print(f"   通過率: {summary['passed_cases']}/{summary['total_cases']} ({summary['pass_rate']:.1f}%)")
            print(f"   平均分數: {summary['avg_score']:.3f}")
            print(f"   結果文件: {summary['filename']}")
            print()
        
        # 計算整體統計
        total_all = sum(s['total_cases'] for s in results_summary)
        passed_all = sum(s['passed_cases'] for s in results_summary)
        avg_all = sum(s['avg_score'] * s['total_cases'] for s in results_summary) / total_all
        
        print(f"🎯 整體表現:")
        print(f"   總測試案例: {total_all}")
        print(f"   總通過案例: {passed_all}")
        print(f"   整體通過率: {passed_all/total_all*100:.1f}%")
        print(f"   整體平均分數: {avg_all:.3f}")
        
        # 保存總結
        summary_filename = f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'datasets_evaluated': len(results_summary),
                'total_cases': total_all,
                'passed_cases': passed_all,
                'overall_pass_rate': passed_all/total_all*100,
                'overall_avg_score': avg_all,
                'dataset_results': results_summary
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 總結已保存到 {summary_filename}")
    
    print("\n🎉 完整評估完成！")
    return True

def run_single_dataset_evaluation():
    """運行單一數據集的詳細評估"""
    print("🎯 單一數據集詳細評估")
    print("=" * 40)
    
    evaluator = RAGFlowEvaluator()
    
    # 獲取數據集
    datasets_result = evaluator.client.list_datasets()
    if not datasets_result['success'] or not datasets_result['data']:
        print("❌ 無法獲取數據集")
        return False
    
    datasets = datasets_result['data']
    print(f"📚 可用數據集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset.get('name', 'N/A')}")
    
    # 選擇數據集
    try:
        choice = input(f"\n請選擇數據集 [1-{len(datasets)}]: ").strip()
        index = int(choice) - 1
        if 0 <= index < len(datasets):
            selected_dataset = datasets[index]
        else:
            selected_dataset = datasets[0]
    except (ValueError, KeyboardInterrupt):
        selected_dataset = datasets[0]
    
    dataset_id = selected_dataset['id']
    dataset_name = selected_dataset['name']
    
    print(f"📖 選擇數據集: {dataset_name}")
    
    # 設置聊天機器人
    if not evaluator.setup_chatbot(dataset_id, dataset_name):
        print("❌ 聊天機器人設置失敗")
        return False
    
    # 獲取問題數量
    try:
        num_questions = int(input(f"請輸入測試問題數量 [預設: {DeepEvalConfig.DEFAULT_QUESTION_COUNT}]: ").strip() or str(DeepEvalConfig.DEFAULT_QUESTION_COUNT))
        num_questions = min(num_questions, DeepEvalConfig.MAX_QUESTION_COUNT)
    except ValueError:
        num_questions = DeepEvalConfig.DEFAULT_QUESTION_COUNT
    
    # 生成測試數據
    print(f"\n📝 生成 {num_questions} 個測試問題...")
    test_data = evaluator.generate_test_data_from_documents(dataset_id, num_questions)
    
    if not test_data:
        print("❌ 測試數據生成失敗")
        return False
    
    print(f"✅ 成功生成 {len(test_data)} 個測試問題:")
    for i, data in enumerate(test_data, 1):
        print(f"  {i}. {data['question']}")
    
    # 確認開始評估
    input("\n按 Enter 開始評估...")
    
    # 執行評估
    results = evaluator.evaluate_test_cases(test_data)
    
    if not results:
        print("❌ 評估失敗")
        return False
    
    # 詳細結果顯示
    print("\n📋 詳細評估結果:")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        status = "✅ 通過" if result.passed else "❌ 失敗"
        print(f"\n{i}. {status} | 總分: {result.overall_score:.3f}")
        print(f"問題: {result.question}")
        print(f"回答: {result.actual_output[:150]}...")
        
        if result.metrics_scores:
            print("指標分數:")
            for metric, score in result.metrics_scores.items():
                print(f"  - {metric}: {score:.3f}")
        
        if result.retrieval_context:
            print(f"檢索上下文: {len(result.retrieval_context)} 個片段")
    
    # 生成並顯示報告
    report = evaluator.generate_report(results)
    print(f"\n{report}")
    
    # 保存結果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"detailed_evaluation_{dataset_name}_{timestamp}.json"
    evaluator.save_results(results, filename)
    
    print(f"\n💾 詳細結果已保存到 {filename}")
    print("🎉 單一數據集評估完成！")
    
    return True

def main():
    """主函數"""
    print("🚀 DeepEval 測試選單")
    print("=" * 30)
    print("1. 快速評估 (所有數據集)")
    print("2. 詳細評估 (單一數據集)")
    print("3. 配置檢查")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n請選擇操作 [1-4]: ").strip()
            
            if choice == '1':
                run_comprehensive_evaluation()
                break
            elif choice == '2':
                run_single_dataset_evaluation()
                break
            elif choice == '3':
                DeepEvalConfig.print_config_status()
            elif choice == '4':
                print("👋 再見！")
                break
            else:
                print("❌ 無效選擇，請重新輸入")
        
        except KeyboardInterrupt:
            print("\n👋 程序被中斷，再見！")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()