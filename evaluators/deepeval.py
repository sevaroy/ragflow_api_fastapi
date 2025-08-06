#!/usr/bin/env python3
"""
DeepEval 評估器
基於 DeepEval 框架的評估實現
"""

import os
from typing import Dict, List, Any

# 只在有 OpenAI API Key 時才導入 DeepEval
try:
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
            ContextualPrecisionMetric,
            ContextualRecallMetric,
            HallucinationMetric,
            BiasMetric
        )
        from deepeval.test_case import LLMTestCase
        DEEPEVAL_AVAILABLE = True
    else:
        DEEPEVAL_AVAILABLE = False
except ImportError:
    DEEPEVAL_AVAILABLE = False

from .base import BaseEvaluator


class DeepEvalEvaluator(BaseEvaluator):
    """DeepEval 評估器類"""
    
    def __init__(self, ragflow_client):
        super().__init__(ragflow_client)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.metrics_mapping = {
            'answer_relevancy': '答案相關性',
            'faithfulness': '忠實度',
            'contextual_precision': '上下文精確度',
            'contextual_recall': '上下文召回率',
            'hallucination': '幻覺檢測',
            'bias': '偏見檢測'
        }
        self.metrics = self.get_available_metrics()
    
    def get_available_metrics(self) -> Dict[str, Any]:
        """獲取可用的 DeepEval 指標"""
        if not DEEPEVAL_AVAILABLE or not self.openai_key:
            return {}
        
        try:
            return {
                'answer_relevancy': AnswerRelevancyMetric(threshold=0.7),
                'faithfulness': FaithfulnessMetric(threshold=0.7),
                'contextual_precision': ContextualPrecisionMetric(threshold=0.7),
                'contextual_recall': ContextualRecallMetric(threshold=0.7),
                'hallucination': HallucinationMetric(threshold=0.5),
                'bias': BiasMetric(threshold=0.5)
            }
        except Exception as e:
            print(f"DeepEval 指標載入失敗: {e}")
            return {}
    
    def evaluate(self, test_cases: List[Dict], selected_metrics: List[str]) -> Dict[str, Any]:
        """使用 DeepEval 進行評估"""
        
        if not self.metrics:
            return {
                'success': False,
                'error': 'DeepEval 指標未初始化，請檢查 OpenAI API Key 設置',
                'results': [],
                'summary': {}
            }
        
        try:
            results = []
            
            for case in test_cases:
                # 創建測試案例
                llm_test_case = LLMTestCase(
                    input=case['question'],
                    actual_output=case['actual_answer'],
                    expected_output=case['expected_answer'],
                    retrieval_context=case['contexts']
                )
                
                # 執行評估
                case_result = {
                    'test_id': case['id'],
                    'question': case['question'],
                    'actual_answer': case['actual_answer'],
                    'expected_answer': case['expected_answer'],
                    'contexts': case['contexts']
                }
                
                total_score = 0
                metric_count = 0
                
                for metric_name in selected_metrics:
                    if metric_name in self.metrics:
                        try:
                            metric = self.metrics[metric_name]
                            metric.measure(llm_test_case)
                            score = metric.score
                            passed = metric.is_successful()
                            
                            case_result[metric_name] = {
                                'score': score,
                                'passed': passed,
                                'threshold': metric.threshold
                            }
                            
                            total_score += score
                            metric_count += 1
                        except Exception as e:
                            case_result[metric_name] = {
                                'score': 0.0,
                                'passed': False,
                                'threshold': 0.0,
                                'error': str(e)
                            }
                
                # 計算總分
                case_result['overall_score'] = total_score / metric_count if metric_count > 0 else 0
                case_result['passed'] = case_result['overall_score'] >= 0.7
                
                results.append(case_result)
            
            return {
                'success': True,
                'results': results,
                'summary': self.calculate_summary_stats(results)
            }
            
        except Exception as e:
            print(f"DeepEval 評估失敗: {e}")
            return {
                'success': False,
                'error': f'DeepEval 評估失敗: {str(e)}',
                'results': [],
                'summary': {}
            }
