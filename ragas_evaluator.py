#!/usr/bin/env python3
"""
RAGAS 評估器模組
專門處理 RAG 系統的評估邏輯
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
import random
import uuid

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

class RAGASEvaluator:
    """RAGAS 評估器類"""
    
    def __init__(self, ragflow_client):
        self.client = ragflow_client
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
            print(f"RAGAS 指標載入失敗: {e}")
            return {}
    
    def generate_test_questions(self, dataset_id: str, num_questions: int = 20, 
                              question_types: List[str] = None) -> List[Dict]:
        """生成測試問題"""
        
        # 預定義的問題庫（根據您的領域調整）
        base_questions = {
            "事實查詢": [
                "什麼是憲法第7條的平等原則？",
                "民法中的契約自由原則是什麼？",
                "刑法的罪刑法定原則如何理解？",
                "行政法中的比例原則是什麼？",
                "什麼是物權和債權的區別？"
            ],
            "概念解釋": [
                "請解釋正當防衛的成立條件",
                "什麼是侵權行為的構成要件？",
                "行政處分的定義和特徵是什麼？",
                "基本人權的核心內容是什麼？",
                "權力分立原則如何體現？"
            ],
            "案例分析": [
                "在什麼情況下可以行使正當防衛？",
                "如何判斷是否構成侵權行為？",
                "行政機關的決定何時構成行政處分？",
                "憲法平等原則在實務中如何適用？",
                "契約無效的情況有哪些？"
            ]
        }
        
        if question_types is None:
            question_types = list(base_questions.keys())
        
        # 標準答案庫
        standard_answers = [
            "憲法第7條規定中華民國人民，無分男女、宗教、種族、階級、黨派，在法律上一律平等。",
            "契約自由原則是指當事人有自由決定是否締結契約、與何人締結契約、契約內容等的權利。",
            "罪刑法定原則是指犯罪和刑罰必須由法律明文規定，不得任意擴張解釋。",
            "比例原則要求行政行為必須適當、必要且不過度，以達成行政目的。",
            "物權是對物的直接支配權，債權是請求特定人為特定行為的權利。"
        ]
        
        test_cases = []
        
        for i in range(num_questions):
            # 隨機選擇問題類型和問題
            selected_type = random.choice(question_types)
            question = random.choice(base_questions[selected_type])
            expected_answer = random.choice(standard_answers)
            
            test_cases.append({
                'id': f"test_{i+1:03d}",
                'question': question,
                'expected_answer': expected_answer,
                'question_type': selected_type,
                'dataset_id': dataset_id
            })
        
        return test_cases
    
    def get_rag_responses(self, test_cases: List[Dict]) -> List[Dict]:
        """獲取 RAG 系統的回答"""
        
        enriched_cases = []
        
        for case in test_cases:
            # 調用 RAGFlow API 獲取回答
            response = self.client.send_chat_message(
                question=case['question'],
                dataset_id=case['dataset_id']
            )
            
            if response['success']:
                data = response['data']
                
                # 提取上下文信息
                contexts = []
                if 'sources' in data:
                    contexts = [source.get('content', '') for source in data['sources']]
                
                case.update({
                    'actual_answer': data.get('answer', ''),
                    'contexts': contexts,
                    'response_time': datetime.now().isoformat()
                })
            else:
                case.update({
                    'actual_answer': f"錯誤: {response['error']}",
                    'contexts': [],
                    'response_time': datetime.now().isoformat()
                })
            
            enriched_cases.append(case)
        
        return enriched_cases
    
    def evaluate_with_ragas(self, test_cases: List[Dict], 
                           selected_metrics: List[str]) -> Dict[str, Any]:
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
    
    def calculate_summary_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """計算摘要統計"""
        
        if not results:
            return {}
        
        # 基本統計
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.get('passed', False))
        pass_rate = passed_cases / total_cases if total_cases > 0 else 0
        
        # 分數統計
        overall_scores = [r.get('overall_score', 0) for r in results]
        avg_score = np.mean(overall_scores)
        min_score = np.min(overall_scores)
        max_score = np.max(overall_scores)
        
        # 各指標統計
        metrics_stats = {}
        for result in results:
            for key, value in result.items():
                if key in self.metrics_mapping and isinstance(value, (int, float)):
                    if key not in metrics_stats:
                        metrics_stats[key] = []
                    metrics_stats[key].append(value)
        
        for metric, scores in metrics_stats.items():
            metrics_stats[metric] = {
                'mean': np.mean(scores),
                'min': np.min(scores),
                'max': np.max(scores),
                'std': np.std(scores)
            }
        
        return {
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'pass_rate': pass_rate,
            'avg_score': avg_score,
            'min_score': min_score,
            'max_score': max_score,
            'metrics_stats': metrics_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, results: Dict[str, Any], dataset_name: str = "unknown") -> str:
        """保存評估結果"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ragas_evaluation_{dataset_name}_{timestamp}.json"
        
        # 添加元數據
        results['metadata'] = {
            'evaluation_id': str(uuid.uuid4()),
            'dataset_name': dataset_name,
            'evaluation_time': datetime.now().isoformat(),
            'evaluator_version': '1.0.0',
            'ragas_available': RAGAS_AVAILABLE
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return filename
        except Exception as e:
            print(f"保存結果失敗: {e}")
            return None
    
    def load_results(self, filename: str) -> Optional[Dict[str, Any]]:
        """載入評估結果"""
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入結果失敗: {e}")
            return None
    
    def get_available_result_files(self) -> List[str]:
        """獲取可用的結果文件"""
        
        import glob
        return glob.glob("ragas_evaluation_*.json")

