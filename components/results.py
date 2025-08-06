"""
結果分析頁面組件
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime


def render_results_control_panel(available_results):
    """渲染結果控制面板"""
    st.markdown("### 🎛️ 分析控制面板")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # 結果選擇
        selected_idx = st.selectbox(
            "選擇評估結果",
            options=range(len(available_results)),
            format_func=lambda x: available_results[x]['name'],
            key="selected_result_idx"
        )
        
        if selected_idx is not None:
            st.session_state.selected_result_data = available_results[selected_idx]['data']
    
    with col2:
        # 指標篩選
        if hasattr(st.session_state, 'selected_result_data'):
            results = st.session_state.selected_result_data.get('results', [])
            if results:
                available_metrics = [k for k in results[0].keys() if k not in ['test_id', 'question', 'actual_answer', 'expected_answer', 'contexts', 'overall_score', 'passed']]
                selected_metrics = st.multiselect(
                    "顯示指標",
                    options=available_metrics,
                    default=available_metrics[:4] if len(available_metrics) >= 4 else available_metrics,
                    key="display_metrics"
                )
    
    with col3:
        # 分數範圍
        score_range = st.slider(
            "分數範圍",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
            key="score_range"
        )
    
    with col4:
        # 結果狀態
        status_filter = st.selectbox(
            "結果狀態",
            options=["全部", "僅通過", "僅失敗"],
            key="status_filter"
        )


def render_results_dashboard():
    """渲染結果儀表板"""
    data = st.session_state.selected_result_data
    
    # KPI 卡片
    render_kpi_cards(data)
    
    # 主要視覺化
    col1, col2 = st.columns(2)
    
    with col1:
        render_radar_chart(data)
    
    with col2:
        render_score_distribution(data)
    
    # 詳細分析標籤頁
    tab1, tab2, tab3, tab4 = st.tabs(["📋 結果列表", "📊 指標分析", "📈 趨勢分析", "📄 導出報告"])
    
    with tab1:
        render_detailed_results_table(data)
    
    with tab2:
        render_metrics_analysis(data)
    
    with tab3:
        render_trend_analysis()
    
    with tab4:
        render_export_options(data)


def render_kpi_cards(data):
    """渲染 KPI 卡片"""
    st.markdown("### 📊 核心指標總覽")
    
    summary = data.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🎯 總體評分",
            f"{summary.get('avg_score', 0):.3f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "✅ 通過率",
            f"{summary.get('pass_rate', 0):.1%}",
            delta=None
        )
    
    with col3:
        st.metric(
            "📊 測試案例",
            summary.get('total_cases', 0),
            delta=None
        )
    
    with col4:
        st.metric(
            "🔍 分數範圍",
            f"{summary.get('min_score', 0):.2f} - {summary.get('max_score', 0):.2f}",
            delta=None
        )


def render_radar_chart(data):
    """渲染雷達圖"""
    st.markdown("#### 🎯 RAGAS 指標雷達圖")
    
    summary = data.get('summary', {})
    metrics_stats = summary.get('metrics_stats', {})
    
    if not metrics_stats:
        st.info("沒有可用的指標數據")
        return
    
    # 準備雷達圖數據
    metrics = list(metrics_stats.keys())
    values = [metrics_stats[m]['mean'] for m in metrics]
    
    # 創建雷達圖
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name='平均分數',
        fillcolor='rgba(102, 126, 234, 0.25)',
        line=dict(color='rgba(102, 126, 234, 1)', width=2)
    ))
    
    # 添加閾值線
    threshold_values = [0.7] * len(metrics)
    fig.add_trace(go.Scatterpolar(
        r=threshold_values,
        theta=metrics,
        mode='lines',
        name='通過閾值 (0.7)',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickmode='linear',
                tick0=0,
                dtick=0.2
            )
        ),
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_score_distribution(data):
    """渲染分數分佈圖"""
    st.markdown("#### 📊 分數分佈分析")
    
    results = data.get('results', [])
    if not results:
        st.info("沒有可用的結果數據")
        return
    
    # 提取總分數據
    overall_scores = [r.get('overall_score', 0) for r in results]
    
    # 創建直方圖
    fig = go.Figure(data=[go.Histogram(
        x=overall_scores,
        nbinsx=20,
        name='分數分佈',
        marker_color='rgba(102, 126, 234, 0.7)'
    )])
    
    # 添加平均值線
    mean_score = np.mean(overall_scores)
    fig.add_vline(
        x=mean_score,
        line_dash="dash",
        line_color="red",
        annotation_text=f"平均值: {mean_score:.3f}"
    )
    
    # 添加通過閾值線
    fig.add_vline(
        x=0.7,
        line_dash="dot",
        line_color="green",
        annotation_text="通過閾值: 0.7"
    )
    
    fig.update_layout(
        title="整體分數分佈",
        xaxis_title="分數",
        yaxis_title="頻次",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_detailed_results_table(data):
    """渲染詳細結果表格"""
    st.markdown("#### 📋 詳細評估結果")
    
    results = data.get('results', [])
    if not results:
        st.info("沒有可用的結果數據")
        return
    
    # 應用篩選
    filtered_results = apply_filters(results)
    
    st.write(f"顯示 {len(filtered_results)} / {len(results)} 個結果")
    
    # 分頁顯示
    page_size = 10
    total_pages = (len(filtered_results) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.selectbox("選擇頁面", range(1, total_pages + 1))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = filtered_results[start_idx:end_idx]
    else:
        page_results = filtered_results
    
    # 顯示結果
    for result in page_results:
        status = "✅ 通過" if result.get('passed', False) else "❌ 失敗"
        score = result.get('overall_score', 0)
        
        with st.expander(f"{status} - {result.get('test_id', 'Unknown')} (分數: {score:.3f})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**問題**: {result.get('question', 'N/A')}")
                answer = result.get('actual_answer', 'N/A')
                if len(answer) > 200:
                    st.write(f"**回答**: {answer[:200]}...")
                else:
                    st.write(f"**回答**: {answer}")
            
            with col2:
                # 顯示各項指標
                selected_metrics = st.session_state.get('display_metrics', [])
                for metric in selected_metrics:
                    if metric in result:
                        st.metric(metric, f"{result[metric]:.3f}")


def render_metrics_analysis(data):
    """渲染指標分析"""
    st.markdown("#### 📊 指標詳細分析")
    
    summary = data.get('summary', {})
    metrics_stats = summary.get('metrics_stats', {})
    
    if not metrics_stats:
        st.info("沒有可用的指標統計數據")
        return
    
    # 指標統計表格
    metrics_df = pd.DataFrame([
        {
            'metric': metric,
            'mean': stats['mean'],
            'min': stats['min'],
            'max': stats['max'],
            'std': stats['std']
        }
        for metric, stats in metrics_stats.items()
    ])
    
    st.dataframe(metrics_df, use_container_width=True)
    
    # 指標對比圖
    fig = px.bar(
        metrics_df,
        x='metric',
        y='mean',
        title='各指標平均分數對比',
        error_y='std'
    )
    
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="通過閾值")
    
    st.plotly_chart(fig, use_container_width=True)


def render_trend_analysis():
    """渲染趨勢分析"""
    st.markdown("#### 📈 歷史趨勢分析")
    
    st.info("📊 趨勢分析需要多次真實評估數據，請先進行 RAGAS 評估以生成歷史數據")


def render_export_options(data):
    """渲染導出選項"""
    st.markdown("#### 📤 導出選項")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 導出 CSV", use_container_width=True):
            csv_data = export_to_csv(data)
            st.download_button(
                label="下載 CSV 文件",
                data=csv_data,
                file_name=f"ragas_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🔧 導出 JSON", use_container_width=True):
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                label="下載 JSON 文件",
                data=json_data,
                file_name=f"ragas_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📄 生成報告", use_container_width=True):
            report = generate_markdown_report(data)
            st.download_button(
                label="下載 Markdown 報告",
                data=report,
                file_name=f"ragas_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
    
    with col4:
        if st.button("🔄 刷新數據", use_container_width=True):
            st.rerun()


def apply_filters(results):
    """應用篩選條件"""
    filtered = results
    
    # 狀態篩選
    status_filter = st.session_state.get('status_filter', '全部')
    if status_filter == '僅通過':
        filtered = [r for r in filtered if r.get('passed', False)]
    elif status_filter == '僅失敗':
        filtered = [r for r in filtered if not r.get('passed', True)]
    
    # 分數範圍篩選
    score_range = st.session_state.get('score_range', (0.0, 1.0))
    filtered = [r for r in filtered if score_range[0] <= r.get('overall_score', 0) <= score_range[1]]
    
    return filtered


def export_to_csv(data):
    """導出為 CSV"""
    results = data.get('results', [])
    if not results:
        return ""
    
    df = pd.DataFrame(results)
    return df.to_csv(index=False, encoding='utf-8')


def generate_markdown_report(data):
    """生成 Markdown 報告"""
    summary = data.get('summary', {})
    
    report = f"""# RAGAS 評估報告
    
## 評估摘要
- **評估時間**: {summary.get('timestamp', 'N/A')}
- **總測試案例**: {summary.get('total_cases', 0)}
- **通過案例**: {summary.get('passed_cases', 0)}
- **通過率**: {summary.get('pass_rate', 0):.1%}
- **平均分數**: {summary.get('avg_score', 0):.3f}

## 指標統計
"""
    
    metrics_stats = summary.get('metrics_stats', {})
    for metric, stats in metrics_stats.items():
        report += f"""
### {metric}
- 平均值: {stats['mean']:.3f}
- 最小值: {stats['min']:.3f}
- 最大值: {stats['max']:.3f}
- 標準差: {stats['std']:.3f}
"""
    
    report += f"""
## 評估詳情
共 {len(data.get('results', []))} 個測試案例的詳細結果。

---
*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return report
