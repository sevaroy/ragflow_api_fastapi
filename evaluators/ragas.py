#!/usr/bin/env python3
"""
RAGAS 評估器
基於 RAGAS 框架的評估實現
"""

from typing import Dict, List, Any
import random

# 嘗試導入 RAGAS
try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy, 
        context_precision,
        context_recall,
        answer_similarity,
        answer_correctness
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

from .base import BaseEvaluator


class RAGASEvaluator(BaseEvaluator):
    """RAGAS 評估器類"""
    
    def __init__(self, ragflow_client):
        super().__init__(ragflow_client)
        self.metrics_mapping = {
            'faithfulness': '忠實度',
            'answer_relevancy': '答案相關性',
            'context_precision': '上下文精確度',
            'context_recall': '上下文召回率',
            'answer_similarity': '答案相似度',
            'answer_correctness': '答案正確性'
        }
        self.available_metrics = self.get_available_metrics()
    
    def get_available_metrics(self) -> Dict[str, Any]:
        """獲取可用的 RAGAS 指標"""
        if not RAGAS_AVAILABLE:
            return {}
        
        try:
            return {
                'faithfulness': faithfulness,
                'answer_relevancy': answer_relevancy,
                'context_precision': context_precision,
                'context_recall': context_recall,
                'answer_similarity': answer_similarity,
                'answer_correctness': answer_correctness
            }
        except Exception as e:
            print(f"載入 RAGAS 指標時出錯: {e}")
            return {}
    
    def evaluate(self, test_cases: List[Dict], selected_metrics: List[str]) -> Dict[str, Any]:
        """使用 RAGAS 進行評估"""
        
        if not RAGAS_AVAILABLE:
            return {
                'success': False,
                'error': 'RAGAS 未安裝，請先安裝 RAGAS: pip install ragas',
                'results': [],
                'summary': {}
            }
        
        try:
            # 準備數據集
            dataset_dict = {
                'question': [case['question'] for case in test_cases],
                'answer': [case['actual_answer'] for case in test_cases],
                'contexts': [case['contexts'] for case in test_cases],
                'ground_truth': [case['expected_answer'] for case in test_cases]
            }
            
            dataset = Dataset.from_dict(dataset_dict)
            
            # 選擇要使用的指標
            metrics_to_use = []
            for metric_name in selected_metrics:
                if metric_name in self.available_metrics:
                    metrics_to_use.append(self.available_metrics[metric_name])
            
            if not metrics_to_use:
                return {'error': '沒有可用的評估指標'}
            
            # 執行評估
            results = evaluate(dataset, metrics=metrics_to_use)
            
            # 處理結果
            processed_results = self.process_ragas_results(results, test_cases)
            
            return {
                'success': True,
                'results': processed_results,
                'summary': self.calculate_summary_stats(processed_results)
            }
            
        except Exception as e:
            print(f"RAGAS 評估失敗: {e}")
            return {
                'success': False,
                'error': f'RAGAS 評估失敗: {str(e)}',
                'results': [],
                'summary': {}
            }
    
    def process_ragas_results(self, ragas_results, test_cases: List[Dict]) -> List[Dict]:
        """處理 RAGAS 評估結果"""
        
        processed = []
        
        for i, case in enumerate(test_cases):
            result = {
                'test_id': case['id'],
                'question': case['question'],
                'actual_answer': case.get('actual_answer', ''),
                'expected_answer': case['expected_answer'],
                'contexts': case.get('contexts', [])
            }
            
            # 提取各項指標分數
            total_score = 0
            metric_count = 0
            
            for metric_name in ragas_results.keys():
                if isinstance(ragas_results[metric_name], list) and i < len(ragas_results[metric_name]):
                    score = ragas_results[metric_name][i]
                    result[metric_name] = score
                    total_score += score
                    metric_count += 1
            
            # 計算總分
            result['overall_score'] = total_score / metric_count if metric_count > 0 else 0
            result['passed'] = result['overall_score'] >= 0.7
            
            processed.append(result)
        
        return processed
