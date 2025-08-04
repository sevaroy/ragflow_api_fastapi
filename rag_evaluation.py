#!/usr/bin/env python3
"""
修復版 RAG 評估系統
徹底解決字符串切片問題
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

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

# 導入本地模組
from ragflow_chatbot import RAGFlowOfficialClient, RAGFlowChatbot

class SimpleRAGEvaluator:
    """簡化版 RAG 評估器"""
    
    def __init__(self):
        self.client = RAGFlowOfficialClient()
        self.chatbot = None
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        # 初始化評估指標
        self.metrics = {}
        if DEEPEVAL_AVAILABLE and self.openai_key:
            try:
                self.metrics = {
                    'answer_relevancy': AnswerRelevancyMetric(threshold=0.7),
                    'faithfulness': FaithfulnessMetric(threshold=0.7)
                }
                st.success("✅ DeepEval 指標已初始化")
            except Exception as e:
                st.warning(f"⚠️ DeepEval 指標初始化失敗: {e}")
                self.metrics = {}
    
    def setup_chatbot(self, dataset_id: str, dataset_name: str) -> bool:
        """設置聊天機器人"""
        try:
            self.chatbot = RAGFlowChatbot()
            return self.chatbot.setup_chat(dataset_id, dataset_name)
        except Exception as e:
            st.error(f"聊天機器人設置失敗: {e}")
            return False
    
    def generate_simple_questions(self, dataset_name: str, num_questions: int) -> List[Dict[str, str]]:
        """生成簡單的測試問題"""
        
        # 根據數據集名稱選擇問題模板
        if any(keyword in dataset_name.lower() for keyword in ['法律', 'legal', '憲法', '民法', '行政法']):
            base_questions = [
                "什麼是憲法的基本原則？",
                "民法中的契約自由原則是什麼？",
                "刑法的罪刑法定原則如何理解？",
                "行政法中的比例原則是什麼？",
                "民事訴訟中的舉證責任如何分配？",
                "憲法保障哪些基本權利？",
                "什麼是法治國家的特徵？"
            ]
        elif any(keyword in dataset_name.lower() for keyword in ['技術', 'tech', 'api']):
            base_questions = [
                "什麼是 API？",
                "如何進行系統配置？",
                "有哪些重要的技術概念？",
                "如何解決常見問題？",
                "什麼是微服務架構？",
                "如何進行性能優化？",
                "系統安全有哪些考慮？"
            ]
        else:
            base_questions = [
                f"{dataset_name}包含什麼主要內容？",
                "有哪些重要的概念需要了解？",
                "這個領域的最新發展趨勢是什麼？",
                "有什麼實際應用案例？",
                "如何開始學習這個領域？",
                "常見的問題有哪些？",
                "最佳實踐是什麼？"
            ]
        
        # 生成測試數據
        test_data = []
        for i in range(min(num_questions, len(base_questions))):
            question_text = base_questions[i]
            
            # 確保 question_text 是字符串
            if not isinstance(question_text, str):
                question_text = str(question_text)
            
            test_data.append({
                'id': f"simple_{i+1}",
                'question': question_text,
                'expected_answer': f"關於{dataset_name}的相關回答",
                'source': 'simple_generation'
            })
        
        return test_data
    
    def get_rag_answer(self, question: str) -> Dict[str, Any]:
        """獲取 RAG 系統的回答"""
        if not self.chatbot:
            return {
                'success': False,
                'message': '聊天機器人未初始化'
            }
        
        try:
            result = self.chatbot.ask(question)
            return result
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def evaluate_with_deepeval(self, question: str, actual_output: str, 
                              expected_output: str, retrieval_context: List[str]) -> Dict[str, Any]:
        """使用 DeepEval 進行評估"""
        if not self.metrics:
            return {
                'error': 'DeepEval 指標未初始化',
                'metrics_scores': {}
            }
        
        try:
            # 創建測試案例
            llm_test_case = LLMTestCase(
                input=question,
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context
            )
            
            # 執行評估
            metrics_scores = {}
            for metric_name, metric in self.metrics.items():
                try:
                    metric.measure(llm_test_case)
                    metrics_scores[metric_name] = {
                        'score': metric.score,
                        'passed': metric.is_successful(),
                        'threshold': metric.threshold
                    }
                except Exception as e:
                    metrics_scores[metric_name] = {
                        'score': 0.0,
                        'passed': False,
                        'threshold': metric.threshold,
                        'error': str(e)
                    }
            
            return {
                'metrics_scores': metrics_scores
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'metrics_scores': {}
            }

def main():
    """主函數"""
    st.set_page_config(
        page_title="修復版 RAG 評估",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔧 修復版 RAG 評估系統")
    st.markdown("徹底解決字符串切片問題的版本")
    
    # 檢查 OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        st.warning("⚠️ 未設置 OPENAI_API_KEY，將使用基礎評估模式")
        st.info("💡 設置方法: export OPENAI_API_KEY='your-api-key'")
    else:
        st.success("✅ OpenAI API Key 已設置")
    
    # 側邊欄控制
    with st.sidebar:
        st.header("⚙️ 控制面板")
        
        # 初始化評估器
        if 'evaluator' not in st.session_state:
            st.session_state.evaluator = SimpleRAGEvaluator()
        
        evaluator = st.session_state.evaluator
        
        # 獲取數據集
        st.subheader("📚 數據集選擇")
        
        datasets_result = evaluator.client.list_datasets()
        if not datasets_result['success']:
            st.error(f"❌ 獲取數據集失敗: {datasets_result['message']}")
            return
        
        datasets = datasets_result['data']
        if not datasets:
            st.error("❌ 沒有可用的數據集")
            return
        
        # 數據集選擇
        dataset_names = [f"{ds.get('name', 'N/A')} ({ds.get('document_count', 'N/A')} 文檔)" for ds in datasets]
        selected_index = st.selectbox(
            "選擇數據集:", 
            range(len(dataset_names)), 
            format_func=lambda x: dataset_names[x]
        )
        
        selected_dataset = datasets[selected_index]
        st.session_state.selected_dataset = selected_dataset
        
        # 設置聊天機器人
        if st.session_state.get('current_dataset_id') != selected_dataset['id']:
            if evaluator.setup_chatbot(selected_dataset['id'], selected_dataset['name']):
                st.session_state.current_dataset_id = selected_dataset['id']
                st.success("✅ RAG 系統已連接")
            else:
                st.error("❌ 聊天機器人設置失敗")
                return
        
        st.divider()
        
        # 評估配置
        st.subheader("🎯 評估配置")
        num_questions = st.slider("測試問題數量:", 1, 10, 3)
        
        st.divider()
        
        # 操作按鈕
        st.subheader("🚀 操作")
        
        # 生成測試問題
        if st.button("📝 生成測試問題", use_container_width=True):
            with st.spinner("正在生成測試問題..."):
                try:
                    test_data = evaluator.generate_simple_questions(
                        selected_dataset['name'], num_questions
                    )
                    st.session_state.test_data = test_data
                    st.success(f"✅ 生成了 {len(test_data)} 個測試問題")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 生成測試問題失敗: {e}")
        
        # 執行評估
        if 'test_data' in st.session_state and st.session_state.test_data:
            st.success(f"📝 已準備 {len(st.session_state.test_data)} 個測試問題")
            
            if st.button("🧪 開始評估", type="primary", use_container_width=True):
                run_evaluation(evaluator)
        
        # 清除數據
        if 'test_data' in st.session_state or 'evaluation_results' in st.session_state:
            st.divider()
            if st.button("🗑️ 清除數據", use_container_width=True):
                clear_session_data()
                st.success("✅ 數據已清除")
                st.rerun()
    
    # 主頁面內容
    display_main_content()

def run_evaluation(evaluator):
    """執行評估"""
    test_data = st.session_state.test_data
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, test_case in enumerate(test_data):
        # 確保 question 是字符串
        question = str(test_case['question'])
        
        status_text.text(f"🔄 評估案例 {i+1}/{len(test_data)}: {question[:50]}...")
        progress_bar.progress((i + 1) / len(test_data))
        
        # 獲取 RAG 回答
        rag_result = evaluator.get_rag_answer(question)
        
        if rag_result['success']:
            actual_output = rag_result['answer']
            expected_output = test_case['expected_answer']
            retrieval_context = [
                source.get('content', '') for source in rag_result.get('sources', [])
                if isinstance(source, dict) and source.get('content')
            ]
            
            # DeepEval 評估
            if evaluator.metrics:
                eval_result = evaluator.evaluate_with_deepeval(
                    question, actual_output, expected_output, retrieval_context
                )
                metrics_scores = eval_result.get('metrics_scores', {})
            else:
                # 無評估指標可用
                st.error("❌ 無法進行評估：DeepEval 指標未初始化")
                return
            
            # 計算整體結果
            passed_count = sum(1 for m in metrics_scores.values() if m.get('passed', False))
            total_count = len(metrics_scores)
            overall_passed = passed_count >= total_count * 0.5
            avg_score = sum(m.get('score', 0) for m in metrics_scores.values()) / total_count if total_count > 0 else 0
            
            results.append({
                'test_case_id': test_case['id'],
                'question': question,
                'actual_output': actual_output,
                'expected_output': expected_output,
                'retrieval_context': retrieval_context,
                'metrics_scores': metrics_scores,
                'overall_score': avg_score,
                'passed': overall_passed
            })
        else:
            st.error(f"❌ 案例 {i+1} RAG 查詢失敗: {rag_result.get('message', '未知錯誤')}")
    
    # 清除進度顯示
    progress_bar.empty()
    status_text.empty()
    
    # 保存結果
    st.session_state.evaluation_results = results
    st.success(f"🎉 評估完成！共評估了 {len(results)} 個案例")
    st.rerun()

def display_main_content():
    """顯示主頁面內容"""
    if 'evaluation_results' in st.session_state:
        display_evaluation_results()
    elif 'test_data' in st.session_state:
        display_test_questions()
    else:
        display_welcome_page()

def display_welcome_page():
    """顯示歡迎頁面"""
    st.markdown("""
    ## 🔧 修復版 RAG 評估系統
    
    這是一個徹底解決字符串切片問題的 RAG 評估系統：
    
    ### ✨ 主要特色
    - 🔧 **問題修復**: 徹底解決字符串切片錯誤
    - 🛡️ **錯誤處理**: 完善的異常處理機制
    - 🎯 **簡化邏輯**: 避免複雜的問題生成邏輯
    - 📊 **靈活評估**: 支持有/無 OpenAI API Key 的評估模式
    
    ### 📋 使用步驟
    1. 在左側邊欄選擇數據集
    2. 設定測試問題數量
    3. 生成測試問題
    4. 執行評估
    5. 查看結果
    
    **👈 請在左側邊欄開始操作！**
    """)

def display_test_questions():
    """顯示測試問題預覽"""
    st.subheader("❓ 測試問題預覽")
    
    test_data = st.session_state.test_data
    
    # 統計信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("問題總數", len(test_data))
    with col2:
        avg_len = sum(len(str(q['question'])) for q in test_data) / len(test_data)
        st.metric("平均問題長度", f"{avg_len:.0f} 字符")
    with col3:
        st.metric("數據來源", test_data[0].get('source', 'unknown'))
    
    # 問題列表
    for i, data in enumerate(test_data):
        question = str(data['question'])  # 確保是字符串
        with st.expander(f"問題 {i+1}: {question[:60]}...", expanded=False):
            st.write("**問題:**")
            st.write(question)
            st.write("**期望答案:**")
            st.write(data['expected_answer'])
    
    st.info("💡 問題已準備就緒，請在左側邊欄點擊「開始評估」按鈕！")

def display_evaluation_results():
    """顯示評估結果"""
    results = st.session_state.evaluation_results
    
    st.subheader("📊 評估結果")
    
    # 整體統計
    total_cases = len(results)
    passed_cases = sum(1 for r in results if r['passed'])
    pass_rate = passed_cases / total_cases * 100
    avg_score = sum(r['overall_score'] for r in results) / total_cases
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("總案例數", total_cases)
    with col2:
        st.metric("通過案例", passed_cases)
    with col3:
        st.metric("通過率", f"{pass_rate:.1f}%")
    with col4:
        st.metric("平均分數", f"{avg_score:.3f}")
    
    # 詳細結果
    st.subheader("📋 詳細結果")
    
    for i, result in enumerate(results):
        status = "✅ 通過" if result['passed'] else "❌ 失敗"
        question = str(result['question'])  # 確保是字符串
        
        with st.expander(f"{status} | 案例 {i+1} | 分數: {result['overall_score']:.3f}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("**問題:**")
                st.write(question)
                
                st.write("**RAG 系統回答:**")
                st.write(result['actual_output'])
                
                st.write("**期望回答:**")
                st.write(result['expected_output'])
            
            with col2:
                st.write("**評估指標:**")
                
                for metric_name, metric_data in result['metrics_scores'].items():
                    if 'error' in metric_data:
                        st.write(f"❌ **{metric_name}**: 錯誤")
                    else:
                        score = metric_data.get('score', 0)
                        passed = metric_data.get('passed', False)
                        threshold = metric_data.get('threshold', 0)
                        
                        status_icon = "✅" if passed else "❌"
                        st.write(f"{status_icon} **{metric_name}**: {score:.3f}")
                        st.write(f"   閾值: {threshold}")

def clear_session_data():
    """清除會話數據"""
    keys_to_clear = ['test_data', 'evaluation_results']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

if __name__ == "__main__":
    main()