#!/usr/bin/env python3
"""
生成示例 DeepEval 數據
用於測試儀表板功能
"""

import json
import random
from datetime import datetime
from typing import List, Dict, Any

def generate_sample_evaluation_data(num_cases: int = 20) -> List[Dict[str, Any]]:
    """生成示例評估數據"""
    
    # 法律相關的示例問題
    sample_questions = [
        "什麼是憲法第7條的平等原則？",
        "民法中的契約自由原則是什麼？", 
        "刑法的罪刑法定原則如何理解？",
        "行政法中的比例原則是什麼？",
        "民事訴訟中的舉證責任如何分配？",
        "什麼是物權和債權的區別？",
        "侵權行為的構成要件有哪些？",
        "犯罪的構成要件包括什麼？",
        "正當防衛的成立條件是什麼？",
        "行政處分的定義和特徵？",
        "國家賠償的適用範圍？",
        "基本人權的核心內容是什麼？",
        "權力分立原則如何體現？",
        "法治國家的基本要求？",
        "憲法修正的程序為何？"
    ]
    
    sample_answers = [
        "憲法第7條規定中華民國人民，無分男女、宗教、種族、階級、黨派，在法律上一律平等。",
        "契約自由原則是指當事人有自由決定是否締結契約、與何人締結契約、契約內容等的權利。",
        "罪刑法定原則是指犯罪和刑罰必須由法律明文規定，不得任意擴張解釋。",
        "比例原則要求行政行為必須適當、必要且不過度，以達成行政目的。",
        "舉證責任原則上由主張事實存在的當事人負擔，但法律另有規定者除外。"
    ]
    
    results = []
    
    for i in range(num_cases):
        # 隨機選擇問題和答案
        question = random.choice(sample_questions)
        expected_answer = random.choice(sample_answers)
        
        # 生成實際回答（稍作變化）
        actual_answer = expected_answer
        if random.random() < 0.3:  # 30% 機率生成不完整答案
            actual_answer = expected_answer[:len(expected_answer)//2] + "..."
        
        # 生成指標分數
        base_score = random.uniform(0.4, 0.95)
        
        # 相關性分數
        answer_relevancy = max(0.1, min(0.99, base_score + random.uniform(-0.1, 0.1)))
        
        # 忠實度分數
        faithfulness = max(0.1, min(0.99, base_score + random.uniform(-0.15, 0.1)))
        
        # 上下文精確度
        contextual_precision = max(0.1, min(0.99, base_score + random.uniform(-0.1, 0.15)))
        
        # 上下文召回率
        contextual_recall = max(0.1, min(0.99, base_score + random.uniform(-0.1, 0.1)))
        
        # 幻覺分數（越低越好）
        hallucination = max(0.01, min(0.8, 0.5 - base_score + random.uniform(-0.1, 0.2)))
        
        # 偏見分數（越低越好）
        bias = max(0.01, min(0.7, 0.4 - base_score * 0.5 + random.uniform(-0.1, 0.1)))
        
        # 計算整體分數
        positive_metrics = [answer_relevancy, faithfulness, contextual_precision, contextual_recall]
        negative_metrics = [hallucination, bias]
        
        overall_score = (
            sum(positive_metrics) / len(positive_metrics) * 0.7 +
            (1 - sum(negative_metrics) / len(negative_metrics)) * 0.3
        )
        
        # 判斷是否通過
        passed = (
            answer_relevancy >= 0.7 and
            faithfulness >= 0.7 and
            contextual_precision >= 0.7 and
            contextual_recall >= 0.7 and
            hallucination <= 0.3 and
            bias <= 0.5
        )
        
        result = {
            "test_case_id": f"test_{i+1:03d}",
            "question": question,
            "actual_output": actual_answer,
            "expected_output": expected_answer,
            "retrieval_context": [
                f"相關法條內容片段 {j+1}" for j in range(random.randint(1, 4))
            ],
            "metrics_scores": {
                "answer_relevancy": round(answer_relevancy, 3),
                "faithfulness": round(faithfulness, 3),
                "contextual_precision": round(contextual_precision, 3),
                "contextual_recall": round(contextual_recall, 3),
                "hallucination": round(hallucination, 3),
                "bias": round(bias, 3)
            },
            "overall_score": round(overall_score, 3),
            "passed": passed
        }
        
        results.append(result)
    
    return results

def generate_summary_data(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成摘要數據"""
    total_cases = len(results)
    passed_cases = sum(1 for r in results if r['passed'])
    pass_rate = passed_cases / total_cases * 100 if total_cases > 0 else 0
    avg_score = sum(r['overall_score'] for r in results) / total_cases if total_cases > 0 else 0
    
    return {
        'timestamp': datetime.now().isoformat(),
        'total_cases': total_cases,
        'passed_cases': passed_cases,
        'overall_pass_rate': pass_rate,
        'overall_avg_score': avg_score,
        'dataset_results': [{
            'dataset_name': '法律考試數據集',
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'pass_rate': pass_rate,
            'avg_score': avg_score,
            'results': results
        }]
    }

def main():
    """主函數"""
    print("📊 生成 DeepEval 示例數據")
    print("=" * 30)
    
    # 獲取用戶輸入
    try:
        num_cases = int(input("請輸入要生成的測試案例數量 [預設: 20]: ") or "20")
        num_cases = max(1, min(100, num_cases))  # 限制在 1-100 之間
    except ValueError:
        num_cases = 20
    
    print(f"📝 生成 {num_cases} 個測試案例...")
    
    # 生成數據
    results = generate_sample_evaluation_data(num_cases)
    summary = generate_summary_data(results)
    
    # 保存結果文件
    results_filename = f"sample_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_filename = f"sample_evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 保存詳細結果
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存摘要
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 詳細結果已保存到: {results_filename}")
    print(f"✅ 摘要數據已保存到: {summary_filename}")
    
    # 顯示統計信息
    passed_count = sum(1 for r in results if r['passed'])
    pass_rate = passed_count / num_cases * 100
    avg_score = sum(r['overall_score'] for r in results) / num_cases
    
    print(f"\n📈 生成數據統計:")
    print(f"   總案例數: {num_cases}")
    print(f"   通過案例: {passed_count}")
    print(f"   通過率: {pass_rate:.1f}%")
    print(f"   平均分數: {avg_score:.3f}")
    
    print(f"\n🚀 現在你可以:")
    print(f"   1. 運行儀表板: python3 run_dashboard.py")
    print(f"   2. 直接啟動: streamlit run deepeval_dashboard.py")
    print(f"   3. 在儀表板中載入文件: {results_filename}")

if __name__ == "__main__":
    main()