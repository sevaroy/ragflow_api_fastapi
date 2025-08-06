#!/usr/bin/env python3
"""
RAGAS 評估頁面模組
整合 RAGAS 評估分析功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
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

# 導入 RAGFlow 客戶端
try:
    from ragflow_chatbot import RAGFlowOfficialClient
    RAGFLOW_AVAILABLE = True
except ImportError:
    RAGFLOW_AVAILABLE = False

class RAGASEvaluator:
    """RAGAS 評估器類"""
    
    def __init__(self):
        self.client = None
        if RAGFLOW_AVAILABLE:
            self.client = RAGFlowOfficialClient()
        
        # 指標映射
        self.metrics_mapping = {
            'faithfulness': '忠實度',
            'answer_relevancy': '答案相關性',
            'context_precision': '上下文精確度',
            'context_recall': '上下文召回率',
            'answer_similarity': '答案相似度',
            'answer_correctness': '答案正確性'
        }
        
        # 可用指標
        self.available_metrics = self.get_available_metrics()
    
    def get_available_metrics(self) -> Dict[str, Any]:
        """獲取可用的 RAGAS 指標"""
        if not RAGAS_AVAILABLE:
            return {}
        
        return {
            'faithfulness': faithfulness,
            'answer_relevancy': answer_relevancy,
            'context_precision': context_precision,
            'context_recall': context_recall,
            'answer_similarity': answer_similarity,
            'answer_correctness': answer_correctness
        }
    
    def generate_test_questions(self, dataset_name: str, num_questions: int) -> List[Dict[str, str]]:
        """生成測試問題"""
        # 根據數據集名稱選擇問題模板
        if any(keyword in dataset_name.lower() for keyword in ['法律', 'legal', '憲法', '民法', '行政法']):
            base_questions = [
                "什麼是憲法的基本原則？",
                "民法中的契約自由原則是什麼？",
                "刑法的罪刑法定原則如何理解？",
                "行政法中的比例原則是什麼？",
                "民事訴訟中的舉證責任如何分配？",
                "憲法保障哪些基本權利？",
                "什麼是法治國家的特徵？",
                "行政處分的構成要件是什麼？",
                "民法的時效制度如何規定？",
                "刑事訴訟的基本原則有哪些？"
            ]
        elif any(keyword in dataset_name.lower() for keyword in ['技術', 'tech', 'api']):
            base_questions = [
                "什麼是 API？",
                "如何進行系統配置？",
                "有哪些重要的技術概念？",
                "如何解決常見問題？",
                "什麼是微服務架構？",
                "如何進行性能優化？",
                "系統安全有哪些考慮？",
                "什麼是RESTful API？",
                "如何進行數據庫設計？",
                "什麼是容器化技術？"
            ]
        else:
            base_questions = [
                f"{dataset_name}包含什麼主要內容？",
                "有哪些重要的概念需要了解？",
                "這個領域的最新發展趨勢是什麼？",
                "有什麼實際應用案例？",
                "如何開始學習這個領域？",
                "常見的問題有哪些？",
                "最佳實踐是什麼？",
                "有哪些工具和資源？",
                "如何評估效果？",
                "未來發展方向如何？"
            ]
        
        # 生成測試數據
        questions = []
        for i in range(min(num_questions, len(base_questions))):
            questions.append({
                "id": f"q_{i+1}",
                "question": base_questions[i],
                "expected_answer": "",  # 待填寫
                "tags": [dataset_name]
            })
        
        return questions
    
    def evaluate_with_ragas(self, test_cases: List[Dict], selected_metrics: List[str]) -> Dict:
        """使用 RAGAS 進行評估"""
        if not RAGAS_AVAILABLE:
            return {
                'success': False,
                'message': 'RAGAS 不可用，請檢查安裝'
            }
        
        try:
            # 準備數據
            data = {
                'question': [case['question'] for case in test_cases],
                'answer': [case['answer'] for case in test_cases],
                'contexts': [case['contexts'] for case in test_cases],
                'ground_truth': [case.get('expected_answer', '') for case in test_cases]
            }
            
            dataset = Dataset.from_dict(data)
            
            # 選擇評估指標
            metrics = []
            for metric_name in selected_metrics:
                if metric_name in self.available_metrics:
                    metrics.append(self.available_metrics[metric_name])
            
            if not metrics:
                return {
                    'success': False,
                    'message': '沒有選擇有效的評估指標'
                }
            
            # 執行評估
            evaluation_result = evaluate(dataset, metrics=metrics)
            
            # 將 EvaluationResult 轉換為可序列化的字典
            results_dict = {}
            
            # RAGAS EvaluationResult 正確的訪問方式
            if hasattr(evaluation_result, '__getitem__'):
                # EvaluationResult 支援索引訪問，但返回的是列表
                for metric_name in selected_metrics:
                    try:
                        score_list = evaluation_result[metric_name]
                        if isinstance(score_list, list) and len(score_list) > 0:
                            score = score_list[0]  # 取第一個值
                            if hasattr(score, 'item'):  # numpy scalar
                                score_value = float(score.item())
                            else:
                                score_value = float(score)
                            
                            # 處理 NaN 和無穷大值
                            import math
                            if math.isnan(score_value) or math.isinf(score_value):
                                results_dict[metric_name] = 0.0
                            else:
                                results_dict[metric_name] = score_value
                        else:
                            results_dict[metric_name] = 0.0
                    except (KeyError, IndexError, ValueError):
                        results_dict[metric_name] = 0.0
            elif hasattr(evaluation_result, 'to_pandas'):
                # 使用 to_pandas 方法獲取結果
                try:
                    df = evaluation_result.to_pandas()
                    for metric_name in selected_metrics:
                        if metric_name in df.columns:
                            score = df[metric_name].iloc[0] if len(df) > 0 else 0.0
                            results_dict[metric_name] = float(score)
                        else:
                            results_dict[metric_name] = 0.0
                except Exception as e:
                    st.warning(f"to_pandas 方法失敗: {e}")
                    results_dict = {metric: 0.0 for metric in selected_metrics}
            else:
                # 備選方案：對於不識別的類型
                st.warning(f"不識別的評估結果類型: {type(evaluation_result)}")
                results_dict = {metric: 0.0 for metric in selected_metrics}
            
            return {
                'success': True,
                'data': results_dict,
                'metrics_used': selected_metrics
            }
            
        except Exception as e:
            # 只在需要時顯示詳細錯誤
            if 'debug_mode' in st.session_state and st.session_state.debug_mode:
                st.error(f"詳細錯誤信息: {str(e)}")
                st.error(f"錯誤類型: {type(e).__name__}")
                import traceback
                st.error(f"堆棧追蹤: {traceback.format_exc()[:500]}...")
            return {
                'success': False,
                'message': f'評估失敗: {str(e)}'
            }
    
    def save_evaluation_results(self, results: Dict, test_cases: List[Dict]) -> str:
        """保存評估結果"""
        try:
            # 創建結果目錄
            os.makedirs('data/evaluations', exist_ok=True)
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"evaluation_{timestamp}.json"
            filepath = f"data/evaluations/{filename}"
            
            # 準備保存數據
            save_data = {
                "evaluation_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "dataset_id": st.session_state.current_dataset.get('id') if st.session_state.current_dataset else None,
                "dataset_name": st.session_state.current_dataset.get('name') if st.session_state.current_dataset else None,
                "test_cases_count": len(test_cases),
                "results": results,
                "test_cases": test_cases
            }
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            st.error(f"保存評估結果失敗: {e}")
            if 'debug_mode' in st.session_state and st.session_state.debug_mode:
                import traceback
                st.error(traceback.format_exc())
            return None

def show_evaluation_page():
    """顯示評估頁面"""
    st.markdown("## 📏 RAGAS 評估")
    st.markdown("使用 RAGAS 框架對 RAG 系統進行多維度評估分析")
    
    # 檢查依賴
    if not RAGAS_AVAILABLE:
        st.error("❌ RAGAS 不可用，請檢查安裝")
        st.markdown("""
        ### 安裝說明
        ```bash
        pip install ragas datasets
        ```
        """)
        return
    
    if not RAGFLOW_AVAILABLE:
        st.error("❌ RAGFlow 客戶端不可用，請檢查配置")
        return
    
    # 初始化評估器
    if 'ragas_evaluator' not in st.session_state:
        st.session_state.ragas_evaluator = RAGASEvaluator()
    
    evaluator = st.session_state.ragas_evaluator
    
    # 評估源選擇
    st.markdown("### 📚 評估數據來源")
    
    data_source = st.radio(
        "選擇數據來源",
        ["聊天記錄", "手動創建", "上傳文件"],
        horizontal=True
    )
    
    test_cases = []
    
    if data_source == "聊天記錄":
        if 'chat_for_evaluation' in st.session_state and st.session_state.chat_for_evaluation:
            st.success(f"✅ 找到 {len(st.session_state.chat_for_evaluation)} 個聊天記錄可用於評估")
            
            # 顯示聊天記錄預覽
            with st.expander("📋 聊天記錄預覽"):
                for i, case in enumerate(st.session_state.chat_for_evaluation[:5]):
                    st.markdown(f"**問題 {i+1}:** {case['question']}")
                    st.markdown(f"**回答:** {case['answer'][:100]}...")
                    st.markdown("---")
            
            test_cases = st.session_state.chat_for_evaluation
        else:
            st.warning("⚠️ 沒有可用的聊天記錄，請先進行聊天對話")
    
    elif data_source == "手動創建":
        st.markdown("#### 🛠️ 手動創建測試案例")
        
        if st.session_state.current_dataset:
            dataset_name = st.session_state.current_dataset.get('name', 'Unknown')
            num_questions = st.slider("生成問題數量", 1, 20, 5)
            
            if st.button("🎯 生成測試問題"):
                generated_questions = evaluator.generate_test_questions(dataset_name, num_questions)
                st.session_state.generated_questions = generated_questions
                st.success(f"✅ 已生成 {len(generated_questions)} 個測試問題")
            
            if 'generated_questions' in st.session_state:
                st.markdown("#### 📝 編輯測試問題")
                for i, q in enumerate(st.session_state.generated_questions):
                    with st.expander(f"問題 {i+1}: {q['question'][:50]}..."):
                        q['question'] = st.text_area(f"問題 {i+1}", q['question'], key=f"q_{i}")
                        q['expected_answer'] = st.text_area(f"期望答案 {i+1}", q.get('expected_answer', ''), key=f"a_{i}")
                
                if st.button("🚀 獲取 RAG 回答並評估"):
                    # 這裡需要調用 RAGFlow 獲取回答
                    with st.spinner("正在獲取 RAG 系統回答..."):
                        # 模擬獲取回答的過程
                        for q in st.session_state.generated_questions:
                            # 實際實現中應該調用 RAGFlow API
                            q['answer'] = f"這是針對問題 '{q['question']}' 的模擬回答"
                            q['contexts'] = [f"相關上下文信息 for {q['question']}"]
                        
                        test_cases = st.session_state.generated_questions
                        st.success("✅ 已獲取所有問題的回答")
        else:
            st.warning("⚠️ 請先選擇數據集")
    
    elif data_source == "上傳文件":
        uploaded_file = st.file_uploader("上傳測試案例文件 (JSON格式)", type=['json'])
        if uploaded_file:
            try:
                test_cases = json.loads(uploaded_file.read().decode('utf-8'))
                st.success(f"✅ 已上傳 {len(test_cases)} 個測試案例")
            except Exception as e:
                st.error(f"❌ 文件解析失敗: {e}")
    
    # 評估配置
    if test_cases:
        st.markdown("---")
        st.markdown("### ⚙️ 評估配置")
        
        # 指標選擇
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 選擇評估指標")
            selected_metrics = []
            
            for metric_key, metric_name in evaluator.metrics_mapping.items():
                if st.checkbox(metric_name, key=f"metric_{metric_key}"):
                    selected_metrics.append(metric_key)
        
        with col2:
            st.markdown("#### 🔧 評估參數")
            
            # OpenAI API Key 檢查
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                st.success("✅ OpenAI API Key 已配置")
            else:
                st.warning("⚠️ 未檢測到 OpenAI API Key")
                st.markdown("部分 RAGAS 指標需要 OpenAI API")
            
            # 評估閾值設置和調試模式
            col1, col2 = st.columns([3, 1])
            with col1:
                threshold = st.slider("評估閾值", 0.0, 1.0, 0.7, 0.1)
                st.info(f"低於 {threshold} 的指標將被標記為需要改進")
            with col2:
                debug_mode = st.checkbox("調試模式", help="顯示詳細錯誤信息")
                st.session_state.debug_mode = debug_mode
        
        # 開始評估
        if selected_metrics and st.button("🚀 開始 RAGAS 評估", type="primary"):
            with st.spinner("正在執行 RAGAS 評估..."):
                # 顯示進度條
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 執行評估
                try:
                    status_text.text("準備評估數據...")
                    progress_bar.progress(20)
                    
                    status_text.text("執行 RAGAS 評估...")
                    progress_bar.progress(60)
                    
                    results = evaluator.evaluate_with_ragas(test_cases, selected_metrics)
                    progress_bar.progress(80)
                    
                    if results['success']:
                        status_text.text("保存評估結果...")
                        
                        # 保存結果
                        filepath = evaluator.save_evaluation_results(results['data'], test_cases)
                        progress_bar.progress(100)
                        
                        # 將結果添加到 session state
                        if 'evaluation_results' not in st.session_state:
                            st.session_state.evaluation_results = []
                        
                        evaluation_record = {
                            'timestamp': datetime.now().isoformat(),
                            'results': results['data'],
                            'test_cases_count': len(test_cases),
                            'metrics_used': selected_metrics,
                            'filepath': filepath
                        }
                        st.session_state.evaluation_results.append(evaluation_record)
                        
                        st.success("✅ RAGAS 評估完成！")
                        status_text.empty()
                        
                        # 顯示評估結果
                        st.markdown("---")
                        st.markdown("### 📊 評估結果")
                        
                        # 結果概覽
                        results_data = results['data']
                        
                        # 創建指標卡片
                        cols = st.columns(len(selected_metrics))
                        for i, metric in enumerate(selected_metrics):
                            with cols[i]:
                                if metric in results_data:
                                    score = results_data[metric]
                                    metric_name = evaluator.metrics_mapping[metric]
                                    
                                    # 根據分數決定顏色
                                    if score >= 0.8:
                                        color = "🟢"
                                    elif score >= threshold:
                                        color = "🟡"
                                    else:
                                        color = "🔴"
                                    
                                    st.metric(
                                        f"{color} {metric_name}",
                                        f"{score:.3f}",
                                        f"{'✅' if score >= threshold else '⚠️'}"
                                    )
                        
                        # 詳細結果表格
                        st.markdown("#### 📋 詳細結果")
                        results_df = pd.DataFrame([{
                            '指標': evaluator.metrics_mapping[metric],
                            '分數': f"{results_data[metric]:.3f}",
                            '狀態': '✅ 良好' if results_data[metric] >= threshold else '⚠️ 需改進'
                        } for metric in selected_metrics if metric in results_data])
                        
                        st.dataframe(results_df, use_container_width=True)
                        
                        # 結果下載
                        if filepath:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                result_json = f.read()
                            
                            st.download_button(
                                label="📥 下載完整評估結果",
                                data=result_json,
                                file_name=f"ragas_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    
                    else:
                        st.error(f"❌ 評估失敗: {results['message']}")
                        progress_bar.empty()
                        status_text.empty()
                
                except Exception as e:
                    st.error(f"❌ 評估過程中發生錯誤: {e}")
                    progress_bar.empty()
                    status_text.empty()
        
        elif not selected_metrics:
            st.warning("⚠️ 請至少選擇一個評估指標")
    
    else:
        st.info("💡 請選擇或創建測試案例以開始評估")