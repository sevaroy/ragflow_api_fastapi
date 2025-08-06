"""
評估頁面組件
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from evaluators.ragas import RAGASEvaluator


def render_evaluation_steps(current_step):
    """渲染評估步驟指示器"""
    step_cols = st.columns(4)
    steps = [
        {"num": 1, "name": "⚙️ 配置設定", "desc": "選擇數據集和指標"},
        {"num": 2, "name": "📝 數據準備", "desc": "生成測試問題"},
        {"num": 3, "name": "🔄 執行評估", "desc": "運行 RAGAS 評估"},
        {"num": 4, "name": "📈 結果分析", "desc": "查看評估結果"}
    ]
    
    for i, (col, step) in enumerate(zip(step_cols, steps)):
        with col:
            if step["num"] == current_step:
                st.success(f"**{step['name']}**\n\n{step['desc']}")
            elif step["num"] < current_step:
                st.info(f"✅ **{step['name']}**")
            else:
                st.write(f"⏳ **{step['name']}**")


def render_evaluation_config():
    """渲染評估配置"""
    st.markdown("### ⚙️ 評估配置")
    
    # 檢查 API 連接
    if not st.session_state.api_connected:
        st.warning("⚠️ 請先在側邊欄檢查 API 連接")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📚 數據集選擇**")
        
        # 獲取可用數據集
        datasets_result = st.session_state.client.get_datasets()
        if datasets_result['success']:
            datasets = datasets_result['data']
            if datasets:
                selected_dataset = st.selectbox(
                    "選擇知識庫",
                    options=datasets,
                    format_func=lambda x: f"{x.get('name', 'Unknown')} ({x.get('document_count', 0)} 文檔)",
                    key="eval_dataset"
                )
                # selected_dataset 會自動存儲在 st.session_state.eval_dataset 中
            else:
                st.warning("沒有可用的數據集")
                return
        else:
            st.error(f"載入數據集失敗: {datasets_result['error']}")
            return
        
        st.markdown("**📊 測試參數**")
        num_questions = st.slider("測試問題數量", 5, 50, 20, key="eval_num_questions")
        threshold = st.slider("通過閾值", 0.5, 0.9, 0.7, step=0.05, key="eval_threshold")
    
    with col2:
        st.markdown("**🎯 評估指標選擇**")
        
        try:
            from ragas import EvaluationDataset
            RAGAS_AVAILABLE = True
        except ImportError:
            RAGAS_AVAILABLE = False
        
        if RAGAS_AVAILABLE:
            available_metrics = [
                'faithfulness',
                'answer_relevancy', 
                'context_precision',
                'context_recall',
                'answer_similarity',
                'answer_correctness'
            ]
        else:
            st.error("❌ RAGAS 未安裝，無法進行評估")
            st.info("💡 請安裝 RAGAS: pip install ragas")
            return
        
        metric_labels = {
            'faithfulness': '🔍 忠實度',
            'answer_relevancy': '🎯 答案相關性',
            'context_precision': '📍 上下文精確度',
            'context_recall': '📋 上下文召回率',
            'answer_similarity': '🔄 答案相似度',
            'answer_correctness': '✅ 答案正確性'
        }
        
        selected_metrics = []
        for metric in available_metrics:
            if st.checkbox(
                metric_labels.get(metric, metric),
                value=metric in ['faithfulness', 'answer_relevancy', 'context_precision'],
                key=f"metric_{metric}"
            ):
                selected_metrics.append(metric)
        
        st.session_state.eval_metrics = selected_metrics
        
        if not selected_metrics:
            st.warning("⚠️ 請至少選擇一個評估指標")
            return
        
        st.markdown("**📋 問題類型**")
        question_types = st.multiselect(
            "選擇問題類型",
            ["事實查詢", "概念解釋", "案例分析"],
            default=["事實查詢", "概念解釋"],
            key="eval_question_types"
        )
        # question_types 會自動存儲在 st.session_state.eval_question_types 中
    
    st.divider()
    
    # 配置摘要
    if hasattr(st.session_state, 'eval_dataset') and selected_metrics:
        st.markdown("**📋 配置摘要**")
        st.info(f"""
        - **數據集**: {st.session_state.eval_dataset.get('name', 'Unknown')}
        - **測試問題**: {num_questions} 個
        - **評估指標**: {len(selected_metrics)} 個 ({', '.join(selected_metrics)})
        - **問題類型**: {', '.join(question_types)}
        - **通過閾值**: {threshold}
        """)
        
        if st.button("➡️ 下一步：準備數據", type="primary", use_container_width=True):
            st.session_state.evaluation_step = 2
            st.rerun()


def render_data_preparation():
    """渲染數據準備階段"""
    st.markdown("### 📝 數據準備")
    
    # 檢查配置
    if not hasattr(st.session_state, 'eval_dataset'):
        st.error("❌ 請先完成評估配置")
        return
    
    st.info("🔄 正在準備測試數據...")
    
    # 顯示配置信息
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 評估配置**")
        st.write(f"數據集: {st.session_state.eval_dataset.get('name', 'Unknown')}")
        st.write(f"問題數量: {st.session_state.get('eval_num_questions', 20)}")
        st.write(f"評估指標: {len(st.session_state.get('eval_metrics', []))} 個")
    
    with col2:
        st.markdown("**🎯 生成策略**")
        st.write(f"問題類型: {', '.join(st.session_state.get('eval_question_types', []))}")
        st.write(f"通過閾值: {st.session_state.get('eval_threshold', 0.7)}")
    
    # 生成測試數據預覽
    if st.button("🔍 預覽測試問題", use_container_width=True):
        with st.spinner("生成問題預覽..."):
            evaluator = RAGASEvaluator(st.session_state.client)
            sample_questions = evaluator.generate_test_questions(
                dataset_id=st.session_state.eval_dataset['id'],
                num_questions=5,
                question_types=st.session_state.get('eval_question_types', [])
            )
            
            st.markdown("**📋 問題預覽**")
            for i, q in enumerate(sample_questions, 1):
                st.write(f"{i}. {q['question']} *({q['question_type']})*")
    
    st.divider()
    
    # 導航按鈕
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ 返回配置", use_container_width=True):
            st.session_state.evaluation_step = 1
            st.rerun()
    
    with col2:
        if st.button("➡️ 開始評估", type="primary", use_container_width=True):
            st.session_state.evaluation_step = 3
            st.rerun()


def render_evaluation_execution():
    """渲染評估執行階段"""
    st.markdown("### 🔄 執行評估")
    
    # 初始化評估狀態
    if 'evaluation_progress' not in st.session_state:
        st.session_state.evaluation_progress = {
            'status': 'starting',
            'current_step': 0,
            'total_steps': 4,
            'message': '準備開始評估...'
        }
    
    progress = st.session_state.evaluation_progress
    
    # 進度顯示
    progress_bar = st.progress(progress['current_step'] / progress['total_steps'])
    status_text = st.empty()
    status_text.info(f"📊 {progress['message']}")
    
    # 執行評估
    if progress['status'] == 'starting':
        st.session_state.evaluation_progress.update({
            'status': 'generating_questions',
            'current_step': 1,
            'message': '生成測試問題...'
        })
        st.rerun()
    
    elif progress['status'] == 'generating_questions':
        with st.spinner("生成測試問題..."):
            evaluator = RAGASEvaluator(st.session_state.client)
            test_cases = evaluator.generate_test_questions(
                dataset_id=st.session_state.eval_dataset['id'],
                num_questions=st.session_state.get('eval_num_questions', 20),
                question_types=st.session_state.get('eval_question_types', [])
            )
            st.session_state.test_cases = test_cases
        
        st.session_state.evaluation_progress.update({
            'status': 'getting_responses',
            'current_step': 2,
            'message': '獲取 RAG 系統回答...'
        })
        st.rerun()
    
    elif progress['status'] == 'getting_responses':
        with st.spinner("獲取 RAG 系統回答..."):
            evaluator = RAGASEvaluator(st.session_state.client)
            enriched_cases = evaluator.get_rag_responses(st.session_state.test_cases)
            st.session_state.enriched_cases = enriched_cases
        
        st.session_state.evaluation_progress.update({
            'status': 'evaluating',
            'current_step': 3,
            'message': '執行 RAGAS 評估...'
        })
        st.rerun()
    
    elif progress['status'] == 'evaluating':
        with st.spinner("執行 RAGAS 評估..."):
            evaluator = RAGASEvaluator(st.session_state.client)
            results = evaluator.evaluate_with_ragas(
                st.session_state.enriched_cases,
                st.session_state.get('eval_metrics', [])
            )
            st.session_state.evaluation_results = results
        
        st.session_state.evaluation_progress.update({
            'status': 'completed',
            'current_step': 4,
            'message': '評估完成！'
        })
        st.success("✅ 評估完成！")
        
        if st.button("➡️ 查看結果", type="primary", use_container_width=True):
            st.session_state.evaluation_step = 4
            st.rerun()


def render_evaluation_results():
    """渲染評估結果"""
    st.markdown("### 📈 評估結果")
    
    if not hasattr(st.session_state, 'evaluation_results'):
        st.error("❌ 沒有評估結果")
        return
    
    results = st.session_state.evaluation_results
    
    if not results.get('success'):
        st.error(f"❌ 評估失敗: {results.get('error', 'Unknown error')}")
        return
    
    # 摘要統計
    summary = results.get('summary', {})
    
    st.markdown("#### 📊 評估摘要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "總測試案例",
            summary.get('total_cases', 0)
        )
    
    with col2:
        st.metric(
            "通過案例",
            summary.get('passed_cases', 0),
            f"{summary.get('pass_rate', 0):.1%}"
        )
    
    with col3:
        st.metric(
            "平均分數",
            f"{summary.get('avg_score', 0):.3f}"
        )
    
    with col4:
        st.metric(
            "分數範圍",
            f"{summary.get('min_score', 0):.2f} - {summary.get('max_score', 0):.2f}"
        )
    
    # 指標詳情
    if 'metrics_stats' in summary:
        st.markdown("#### 📈 各指標統計")
        
        metrics_data = []
        for metric, stats in summary['metrics_stats'].items():
            metrics_data.append({
                'metric': metric,
                'mean': stats['mean'],
                'min': stats['min'],
                'max': stats['max'],
                'std': stats['std']
            })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            st.dataframe(df, use_container_width=True)
    
    # 詳細結果
    st.markdown("#### 📋 詳細結果")
    
    detailed_results = results.get('results', [])
    
    if detailed_results:
        # 篩選選項
        col1, col2 = st.columns(2)
        
        with col1:
            show_only_failed = st.checkbox("只顯示失敗案例")
        
        with col2:
            min_score_filter = st.slider("最低分數篩選", 0.0, 1.0, 0.0, 0.1)
        
        # 應用篩選
        filtered_results = detailed_results
        if show_only_failed:
            filtered_results = [r for r in filtered_results if not r.get('passed', True)]
        
        filtered_results = [r for r in filtered_results if r.get('overall_score', 0) >= min_score_filter]
        
        st.write(f"顯示 {len(filtered_results)} / {len(detailed_results)} 個結果")
        
        # 顯示結果
        for result in filtered_results[:10]:  # 只顯示前10個
            status = "✅ 通過" if result.get('passed', False) else "❌ 失敗"
            
            with st.expander(f"{status} - {result.get('test_id', 'Unknown')} (分數: {result.get('overall_score', 0):.3f})"):
                st.write(f"**問題**: {result.get('question', 'N/A')}")
                st.write(f"**回答**: {result.get('actual_answer', 'N/A')[:200]}...")
                
                # 顯示各項指標分數
                metrics_cols = st.columns(3)
                for i, (metric, score) in enumerate([(k, v) for k, v in result.items() if k in st.session_state.get('eval_metrics', [])]):
                    with metrics_cols[i % 3]:
                        st.metric(metric, f"{score:.3f}")
    
    # 操作按鈕
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 重新評估", use_container_width=True):
            # 重置評估狀態
            if 'evaluation_progress' in st.session_state:
                del st.session_state.evaluation_progress
            st.session_state.evaluation_step = 1
            st.rerun()
    
    with col2:
        if st.button("📊 查看詳細分析", use_container_width=True):
            st.session_state.current_page = 'results'
            st.rerun()
    
    with col3:
        # 保存結果
        if st.button("💾 保存結果", use_container_width=True):
            evaluator = RAGASEvaluator(st.session_state.client)
            filename = evaluator.save_results(
                results, 
                st.session_state.eval_dataset.get('name', 'unknown')
            )
            if filename:
                st.success(f"✅ 結果已保存至: {filename}")
            else:
                st.error("❌ 保存失敗")
