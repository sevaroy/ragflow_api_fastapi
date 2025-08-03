#!/usr/bin/env python3
"""
DeepEval 整合模組 - RAGFlow 聊天機器人評估系統
自動生成問答數據並評估 RAG 系統性能
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

# DeepEval imports
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
    BiasMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.synthesizer import Synthesizer

# 本地模組
from ragflow_chatbot import RAGFlowChatbot, RAGFlowOfficialClient

@dataclass
class EvaluationResult:
    """評估結果數據類"""
    test_case_id: str
    question: str
    actual_output: str
    expected_output: str
    retrieval_context: List[str]
    metrics_scores: Dict[str, float]
    overall_score: float
    passed: bool

class RAGFlowEvaluator:
    """RAGFlow 系統評估器"""
    
    def __init__(self, openai_api_key: str = None):
        """
        初始化評估器
        
        Args:
            openai_api_key: OpenAI API 密鑰 (用於 DeepEval)
        """
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  警告: 未設置 OPENAI_API_KEY，某些評估功能可能無法使用")
        
        # 設置 OpenAI API 密鑰
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        self.client = RAGFlowOfficialClient()
        self.chatbot = None
        self.synthesizer = None
        
        # 只有在有 API Key 時才初始化評估指標
        self.metrics = {}
        if self.openai_api_key:
            try:
                self.metrics = {
                    'answer_relevancy': AnswerRelevancyMetric(threshold=0.7),
                    'faithfulness': FaithfulnessMetric(threshold=0.7),
                    'contextual_precision': ContextualPrecisionMetric(threshold=0.7),
                    'contextual_recall': ContextualRecallMetric(threshold=0.7),
                    'hallucination': HallucinationMetric(threshold=0.3),
                    'bias': BiasMetric(threshold=0.5)
                }
                print("✅ DeepEval 指標初始化成功")
            except Exception as e:
                print(f"⚠️  DeepEval 指標初始化失敗: {e}")
                self.metrics = {}
        else:
            print("ℹ️  跳過 DeepEval 指標初始化（需要 OpenAI API Key）")
    
    def setup_chatbot(self, dataset_id: str, dataset_name: str = "Unknown") -> bool:
        """設置聊天機器人"""
        self.chatbot = RAGFlowChatbot()
        return self.chatbot.setup_chat(dataset_id, dataset_name)
    
    def generate_test_data_from_documents(self, dataset_id: str, num_questions: int = 10) -> List[Dict[str, Any]]:
        """
        從文檔生成測試問答數據
        
        Args:
            dataset_id: 數據集 ID
            num_questions: 生成問題數量
            
        Returns:
            生成的測試數據列表
        """
        print(f"📝 正在生成 {num_questions} 個測試問題...")
        
        # 如果有 OpenAI API，使用 DeepEval Synthesizer
        if self.openai_api_key:
            try:
                return self._generate_with_synthesizer(dataset_id, num_questions)
            except Exception as e:
                print(f"⚠️  Synthesizer 生成失敗: {e}")
                print("🔄 切換到手動生成模式...")
        
        # 手動生成測試數據
        return self._generate_manual_test_data(dataset_id, num_questions)
    
    def _generate_with_synthesizer(self, dataset_id: str, num_questions: int) -> List[Dict[str, Any]]:
        """使用 DeepEval Synthesizer 生成測試數據"""
        if not self.synthesizer:
            self.synthesizer = Synthesizer()
        
        # 獲取數據集信息
        datasets_result = self.client.list_datasets()
        if not datasets_result['success']:
            raise Exception("無法獲取數據集信息")
        
        dataset_info = None
        for ds in datasets_result['data']:
            if ds['id'] == dataset_id:
                dataset_info = ds
                break
        
        if not dataset_info:
            raise Exception(f"找不到數據集 {dataset_id}")
        
        # 嘗試獲取實際的文檔內容作為上下文
        try:
            # 使用聊天機器人獲取一些示例內容
            sample_questions = [
                "這個知識庫包含什麼內容？",
                "主要涵蓋哪些主題？",
                "有什麼重要信息？"
            ]
            
            contexts = []
            for question in sample_questions[:2]:  # 只取前2個問題避免過多請求
                result = self.chatbot.ask(question)
                if result['success'] and result['sources']:
                    for source in result['sources'][:2]:  # 每個問題取前2個來源
                        if isinstance(source, dict) and source.get('content'):
                            content = source['content'].strip()
                            if content and len(content) > 50:  # 確保內容有意義
                                contexts.append(content[:500])  # 限制長度
            
            # 如果沒有獲取到足夠的上下文，使用基本描述
            if not contexts:
                contexts = [
                    f"這是一個關於{dataset_info['name']}的知識庫，包含{dataset_info.get('document_count', '多個')}個文檔。",
                    f"知識庫涵蓋了{dataset_info['name']}相關的各種信息和內容。"
                ]
            
            print(f"📚 使用 {len(contexts)} 個上下文生成測試問題")
            
        except Exception as e:
            print(f"⚠️ 獲取上下文失敗: {e}")
            # 使用基本上下文
            contexts = [
                f"這是一個關於{dataset_info['name']}的知識庫，包含{dataset_info.get('document_count', '多個')}個文檔。",
                f"知識庫涵蓋了{dataset_info['name']}相關的各種信息和內容。"
            ]
        
        # 生成合成數據
        synthetic_data = self.synthesizer.generate_goldens_from_contexts(
            contexts=contexts,
            max_goldens_per_context=max(1, num_questions // len(contexts))
        )
        
        test_data = []
        for i, golden in enumerate(synthetic_data):
            test_data.append({
                'id': f"synthetic_{i+1}",
                'question': golden.input,
                'expected_answer': golden.expected_output,
                'context': golden.context if isinstance(golden.context, str) else str(golden.context),
                'source': 'synthesizer'
            })
        
        return test_data[:num_questions]  # 確保不超過請求的數量
    
    def _generate_manual_test_data(self, dataset_id: str, num_questions: int) -> List[Dict[str, Any]]:
        """手動生成測試數據"""
        print("🔄 使用手動生成模式...")
        
        # 獲取數據集信息
        datasets_result = self.client.list_datasets()
        if not datasets_result['success']:
            raise Exception("無法獲取數據集信息")
        
        dataset_info = None
        for ds in datasets_result['data']:
            if ds['id'] == dataset_id:
                dataset_info = ds
                break
        
        if not dataset_info:
            raise Exception(f"找不到數據集 {dataset_id}")
        
        dataset_name = dataset_info['name']
        print(f"📚 為數據集 '{dataset_name}' 生成 {num_questions} 個測試問題")
        
        # 使用簡單的問題列表，避免複雜的生成邏輯
        if "法律" in dataset_name or "legal" in dataset_name.lower() or "憲法" in dataset_name or "民法" in dataset_name:
            simple_questions = [
                "什麼是憲法的基本原則？",
                "民法中的契約自由原則是什麼？",
                "刑法的罪刑法定原則如何理解？",
                "行政法中的比例原則是什麼？",
                "民事訴訟中的舉證責任如何分配？"
            ]
        elif "技術" in dataset_name or "tech" in dataset_name.lower() or "api" in dataset_name.lower():
            simple_questions = [
                "什麼是 API？",
                "如何進行系統配置？",
                "有哪些重要的技術概念？",
                "如何解決常見問題？",
                "什麼是微服務架構？"
            ]
        else:
            simple_questions = [
                f"{dataset_name} 包含什麼主要內容？",
                "有哪些重要的概念需要了解？",
                "這個領域的最新發展趨勢是什麼？",
                "有什麼實際應用案例？",
                "如何開始學習這個領域？"
            ]
        
        # 生成測試數據
        test_data = []
        for i in range(min(num_questions, len(simple_questions))):
            question_text = simple_questions[i]
            print(f"🔍 生成問題 {i+1}/{num_questions}: {question_text[:50]}...")
            
            # 向 RAG 系統詢問以獲取期望答案
            try:
                result = self.chatbot.ask(question_text)
                if result['success']:
                    expected_answer = result['answer']
                    context = result['sources'][0].get('content', '') if result['sources'] else f"來自 {dataset_name} 知識庫的內容"
                else:
                    expected_answer = f"關於 {dataset_name} 的相關信息"
                    context = f"來自 {dataset_name} 知識庫的內容"
            except Exception as e:
                print(f"⚠️ 獲取答案失敗: {e}")
                expected_answer = f"關於 {dataset_name} 的相關信息"
                context = f"來自 {dataset_name} 知識庫的內容"
            
            test_data.append({
                'id': f"manual_{i+1}",
                'question': question_text,
                'expected_answer': expected_answer,
                'context': context,
                'source': 'manual'
            })
        
        print(f"✅ 成功生成 {len(test_data)} 個測試問題")
        return test_data
        
        test_data = []
        for i, q in enumerate(questions[:num_questions]):
            test_data.append({
                'id': f"manual_{i+1}",
                'question': q['question'],
                'expected_answer': q['expected_answer'],
                'context': q['context'],
                'source': 'manual'
            })
        
        return test_data
    
    def _generate_legal_questions(self, dataset_name: str, num_questions: int) -> List[Dict[str, Any]]:
        """生成法律相關問題"""
        base_questions = [
            {
                'question': '什麼是憲法的基本原則？',
                'expected_answer': '憲法的基本原則包括人民主權、權力分立、基本人權保障等核心概念。',
                'context': f'基於 {dataset_name} 中的憲法相關內容'
            },
            {
                'question': '民法中的契約自由原則是什麼？',
                'expected_answer': '契約自由原則是指當事人有自由決定是否締結契約、與何人締結契約、契約內容等的權利。',
                'context': f'基於 {dataset_name} 中的民法相關內容'
            },
            {
                'question': '刑法的罪刑法定原則如何理解？',
                'expected_answer': '罪刑法定原則是指犯罪和刑罰必須由法律明文規定，不得任意擴張解釋。',
                'context': f'基於 {dataset_name} 中的刑法相關內容'
            },
            {
                'question': '行政法中的比例原則是什麼？',
                'expected_answer': '比例原則要求行政行為必須適當、必要且不過度，以達成行政目的。',
                'context': f'基於 {dataset_name} 中的行政法相關內容'
            },
            {
                'question': '民事訴訟中的舉證責任如何分配？',
                'expected_answer': '舉證責任原則上由主張事實存在的當事人負擔，但法律另有規定者除外。',
                'context': f'基於 {dataset_name} 中的民事訴訟法相關內容'
            }
        ]
        
        # 擴展問題列表
        extended_questions = base_questions * (num_questions // len(base_questions) + 1)
        return extended_questions[:num_questions]
    
    def _generate_tech_questions(self, dataset_name: str, num_questions: int) -> List[Dict[str, Any]]:
        """生成技術相關問題"""
        base_questions = [
            {
                'question': '什麼是 API？',
                'expected_answer': 'API (Application Programming Interface) 是應用程式介面，用於不同軟體組件之間的通信。',
                'context': f'基於 {dataset_name} 中的 API 相關內容'
            },
            {
                'question': '什麼是 RESTful 架構？',
                'expected_answer': 'RESTful 是一種軟體架構風格，使用 HTTP 方法進行資源操作，具有無狀態、統一介面等特點。',
                'context': f'基於 {dataset_name} 中的 REST 相關內容'
            },
            {
                'question': '什麼是微服務架構？',
                'expected_answer': '微服務架構是將大型應用程式分解為多個小型、獨立的服務，每個服務負責特定的業務功能。',
                'context': f'基於 {dataset_name} 中的微服務相關內容'
            }
        ]
        
        extended_questions = base_questions * (num_questions // len(base_questions) + 1)
        return extended_questions[:num_questions]
    
    def _generate_general_questions(self, dataset_name: str, num_questions: int) -> List[Dict[str, Any]]:
        """生成通用問題"""
        base_questions = [
            {
                'question': f'{dataset_name} 包含什麼主要內容？',
                'expected_answer': f'{dataset_name} 包含相關領域的核心知識和重要概念。',
                'context': f'基於 {dataset_name} 的整體內容概述'
            },
            {
                'question': '有哪些重要的概念需要了解？',
                'expected_answer': '重要概念包括基礎理論、實務應用和相關案例等。',
                'context': f'基於 {dataset_name} 中的核心概念'
            },
            {
                'question': '這個領域的最新發展趨勢是什麼？',
                'expected_answer': '最新發展趨勢包括技術創新、政策變化和實務演進等方面。',
                'context': f'基於 {dataset_name} 中的趨勢分析'
            }
        ]
        
        extended_questions = base_questions * (num_questions // len(base_questions) + 1)
        return extended_questions[:num_questions]
    
    def evaluate_test_cases(self, test_data: List[Dict[str, Any]]) -> List[EvaluationResult]:
        """評估測試案例"""
        if not self.chatbot:
            raise Exception("聊天機器人未設置，請先調用 setup_chatbot()")
        
        print(f"🧪 開始評估 {len(test_data)} 個測試案例...")
        results = []
        
        for i, test_case in enumerate(test_data, 1):
            print(f"📝 評估案例 {i}/{len(test_data)}: {test_case['question'][:50]}...")
            
            # 獲取 RAG 系統回答
            rag_result = self.chatbot.ask(test_case['question'])
            
            if not rag_result['success']:
                print(f"❌ 案例 {i} 查詢失敗: {rag_result['message']}")
                continue
            
            # 準備評估數據
            actual_output = rag_result['answer']
            expected_output = test_case['expected_answer']
            retrieval_context = [source.get('content', '') for source in rag_result['sources'] if isinstance(source, dict)]
            
            # 創建 LLM 測試案例
            llm_test_case = LLMTestCase(
                input=test_case['question'],
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context
            )
            
            # 評估指標
            metrics_scores = {}
            overall_score = 0
            passed_count = 0
            
            # 根據 API 可用性和評估模式選擇指標
            if self.openai_api_key:
                # 有 API 時使用標準評估（避免過多指標）
                from deepeval_config import DeepEvalConfig
                metrics_to_evaluate = DeepEvalConfig.EVALUATION_STAGES.get('standard', ['answer_relevancy', 'faithfulness'])
            else:
                # 無 API 時跳過需要 LLM 的指標
                metrics_to_evaluate = []
            
            for metric_name, metric in self.metrics.items():
                if not metrics_to_evaluate or metric_name in metrics_to_evaluate:
                    try:
                        metric.measure(llm_test_case)
                        score = metric.score
                        metrics_scores[metric_name] = score
                        overall_score += score
                        if metric.is_successful():
                            passed_count += 1
                    except Exception as e:
                        print(f"⚠️  指標 {metric_name} 評估失敗: {e}")
                        metrics_scores[metric_name] = 0.0
            
            # 計算整體分數
            if metrics_scores:
                overall_score = overall_score / len(metrics_scores)
                passed = passed_count >= len(metrics_scores) * 0.6  # 60% 通過率
            else:
                overall_score = 0.5  # 預設分數
                passed = len(actual_output) > 10  # 簡單的通過標準
            
            result = EvaluationResult(
                test_case_id=test_case['id'],
                question=test_case['question'],
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context,
                metrics_scores=metrics_scores,
                overall_score=overall_score,
                passed=passed
            )
            
            results.append(result)
            print(f"✅ 案例 {i} 完成，分數: {overall_score:.2f}")
        
        return results
    
    def save_results(self, results: List[EvaluationResult], filename: str = "evaluation_results.json"):
        """保存評估結果"""
        results_data = []
        for result in results:
            results_data.append({
                'test_case_id': result.test_case_id,
                'question': result.question,
                'actual_output': result.actual_output,
                'expected_output': result.expected_output,
                'retrieval_context': result.retrieval_context,
                'metrics_scores': result.metrics_scores,
                'overall_score': result.overall_score,
                'passed': result.passed
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 評估結果已保存到 {filename}")
    
    def generate_report(self, results: List[EvaluationResult]) -> str:
        """生成評估報告"""
        if not results:
            return "沒有評估結果"
        
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r.passed)
        pass_rate = passed_cases / total_cases * 100
        
        avg_score = sum(r.overall_score for r in results) / total_cases
        
        # 指標統計
        all_metrics = set()
        for result in results:
            all_metrics.update(result.metrics_scores.keys())
        
        metric_stats = {}
        for metric in all_metrics:
            scores = [r.metrics_scores.get(metric, 0) for r in results if metric in r.metrics_scores]
            if scores:
                metric_stats[metric] = {
                    'avg': sum(scores) / len(scores),
                    'min': min(scores),
                    'max': max(scores)
                }
        
        report = f"""
📊 RAGFlow 系統評估報告
{'='*50}

📈 整體統計:
- 總測試案例: {total_cases}
- 通過案例: {passed_cases}
- 通過率: {pass_rate:.1f}%
- 平均分數: {avg_score:.3f}

📋 指標詳情:
"""
        
        for metric, stats in metric_stats.items():
            report += f"- {metric}: 平均 {stats['avg']:.3f} (範圍: {stats['min']:.3f} - {stats['max']:.3f})\n"
        
        report += f"""
🔍 詳細結果:
"""
        
        for i, result in enumerate(results, 1):
            status = "✅ 通過" if result.passed else "❌ 失敗"
            report += f"{i}. {status} | 分數: {result.overall_score:.3f} | {result.question[:50]}...\n"
        
        return report

def main():
    """主函數 - 演示 DeepEval 整合"""
    print("🧪 RAGFlow DeepEval 評估系統")
    print("=" * 50)
    
    # 檢查 OpenAI API 密鑰
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("⚠️  未設置 OPENAI_API_KEY")
        print("   某些高級評估功能將無法使用")
        print("   你仍然可以使用基本的評估功能")
        print()
    
    # 創建評估器
    evaluator = RAGFlowEvaluator(openai_api_key)
    
    # 獲取數據集
    datasets_result = evaluator.client.list_datasets()
    if not datasets_result['success']:
        print(f"❌ 獲取數據集失敗: {datasets_result['message']}")
        return
    
    datasets = datasets_result['data']
    if not datasets:
        print("❌ 沒有可用的數據集")
        return
    
    print(f"📚 找到 {len(datasets)} 個數據集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"  {i}. {dataset.get('name', 'N/A')} (ID: {dataset.get('id', 'N/A')})")
    
    # 選擇數據集
    try:
        choice = input(f"\n請選擇要評估的數據集 [1-{len(datasets)}]: ").strip()
        index = int(choice) - 1
        
        if 0 <= index < len(datasets):
            selected_dataset = datasets[index]
        else:
            print("❌ 無效選擇，使用第一個數據集")
            selected_dataset = datasets[0]
    except (ValueError, KeyboardInterrupt):
        print("❌ 無效輸入，使用第一個數據集")
        selected_dataset = datasets[0]
    
    dataset_id = selected_dataset['id']
    dataset_name = selected_dataset['name']
    
    print(f"📖 選擇數據集: {dataset_name}")
    
    # 設置聊天機器人
    if not evaluator.setup_chatbot(dataset_id, dataset_name):
        print("❌ 聊天機器人設置失敗")
        return
    
    # 生成測試數據
    try:
        num_questions = int(input("請輸入要生成的測試問題數量 [預設: 5]: ").strip() or "5")
    except ValueError:
        num_questions = 5
    
    test_data = evaluator.generate_test_data_from_documents(dataset_id, num_questions)
    
    if not test_data:
        print("❌ 測試數據生成失敗")
        return
    
    print(f"✅ 成功生成 {len(test_data)} 個測試問題")
    
    # 顯示生成的問題
    print("\n📝 生成的測試問題:")
    for i, data in enumerate(test_data, 1):
        print(f"  {i}. {data['question']}")
    
    # 開始評估
    input("\n按 Enter 開始評估...")
    
    results = evaluator.evaluate_test_cases(test_data)
    
    if not results:
        print("❌ 評估失敗")
        return
    
    # 生成報告
    report = evaluator.generate_report(results)
    print(report)
    
    # 保存結果
    evaluator.save_results(results)
    
    print("\n🎉 評估完成！")

if __name__ == "__main__":
    main()