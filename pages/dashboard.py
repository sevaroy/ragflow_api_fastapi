#!/usr/bin/env python3
"""
RAGAS 儀表板頁面模組
數據視覺化和分析功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import glob

def load_evaluation_results() -> List[Dict]:
    """載入所有評估結果"""
    results = []
    
    # 從 session state 載入
    if 'evaluation_results' in st.session_state:
        results.extend(st.session_state.evaluation_results)
    
    # 從文件系統載入
    if os.path.exists('data/evaluations'):
        for filepath in glob.glob('data/evaluations/*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 處理 results 數據，支援多種格式
                    results_data = data.get('results')
                    if not results_data:
                        print(f"跳過空的評估文件: {filepath}")
                        continue
                    
                    # 如果 results 是 EvaluationResult 或其他物件，轉換為字典
                    if hasattr(results_data, 'to_dict'):
                        results_dict = results_data.to_dict()
                    elif hasattr(results_data, '__dict__'):
                        results_dict = {k: float(v) if hasattr(v, 'item') else v 
                                      for k, v in results_data.__dict__.items() 
                                      if not k.startswith('_')}
                    elif isinstance(results_data, dict):
                        results_dict = results_data
                    else:
                        # 嘗試將物件轉換為字典
                        try:
                            results_dict = dict(results_data)
                        except:
                            print(f"無法處理的 results 數據類型: {type(results_data)}, 路徑: {filepath}")
                            continue
                    
                    # 確保所有數值都是可序列化的
                    processed_results = {}
                    for k, v in results_dict.items():
                        if hasattr(v, 'item'):  # numpy scalar
                            processed_results[k] = float(v.item())
                        elif isinstance(v, (int, float)):
                            processed_results[k] = float(v)
                        else:
                            try:
                                processed_results[k] = float(v)
                            except (ValueError, TypeError):
                                processed_results[k] = str(v)
                    
                    if not processed_results:
                        print(f"跳過沒有有效結果的文件: {filepath}")
                        continue
                    
                    results.append({
                        'timestamp': data.get('timestamp', ''),
                        'results': processed_results,
                        'test_cases_count': data.get('test_cases_count', 0),
                        'dataset_name': data.get('dataset_name', 'Unknown'),
                        'filepath': filepath
                    })
            except json.JSONDecodeError as e:
                # JSON 格式錯誤，可以選擇刪除損壞的文件
                print(f"刪除損壞的JSON文件: {filepath}")
                try:
                    os.remove(filepath)
                except:
                    pass
            except Exception as e:
                print(f"載入評估結果失敗 {filepath}: {e}")
    
    # 按時間排序
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    return results

def create_metrics_overview_chart(results: List[Dict]) -> go.Figure:
    """創建指標概覽圖表"""
    if not results:
        return go.Figure()
    
    # 準備數據
    metrics_data = []
    for result in results:
        timestamp = result['timestamp'][:10]  # 只取日期部分
        for metric, score in result['results'].items():
            if isinstance(score, (int, float)):
                metrics_data.append({
                    'date': timestamp,
                    'metric': metric,
                    'score': score,
                    'dataset': result['dataset_name']
                })
    
    df = pd.DataFrame(metrics_data)
    
    if df.empty:
        return go.Figure()
    
    # 創建雷達圖 - 最新結果
    latest_result = results[0]['results']
    metrics = list(latest_result.keys())
    scores = [latest_result[m] for m in metrics if isinstance(latest_result[m], (int, float))]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=metrics,
        fill='toself',
        name='當前評估'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="RAGAS 指標雷達圖"
    )
    
    return fig

def create_trend_chart(results: List[Dict]) -> go.Figure:
    """創建趋势图表"""
    if not results:
        return go.Figure()
    
    # 準備數據
    trend_data = []
    for result in results:
        timestamp = result['timestamp']
        for metric, score in result['results'].items():
            if isinstance(score, (int, float)):
                trend_data.append({
                    'timestamp': timestamp,
                    'metric': metric,
                    'score': score
                })
    
    df = pd.DataFrame(trend_data)
    
    if df.empty:
        return go.Figure()
    
    # 轉換時間格式
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = px.line(df, x='timestamp', y='score', color='metric',
                  title='評估指標趋勢圖',
                  labels={'timestamp': '時間', 'score': '分數', 'metric': '指標'})
    
    fig.update_layout(
        xaxis_title="時間",
        yaxis_title="分數",
        yaxis=dict(range=[0, 1])
    )
    
    return fig

def create_comparison_chart(results: List[Dict]) -> go.Figure:
    """創建比較圖表"""
    if len(results) < 2:
        return go.Figure()
    
    # 取最新的兩次評估進行比較
    latest = results[0]['results']
    previous = results[1]['results']
    
    metrics = set(latest.keys()) & set(previous.keys())
    metrics = [m for m in metrics if isinstance(latest[m], (int, float)) and isinstance(previous[m], (int, float))]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='最新評估',
        x=metrics,
        y=[latest[m] for m in metrics]
    ))
    
    fig.add_trace(go.Bar(
        name='上次評估',
        x=metrics,
        y=[previous[m] for m in metrics]
    ))
    
    fig.update_layout(
        title='評估結果對比',
        xaxis_title='指標',
        yaxis_title='分數',
        yaxis=dict(range=[0, 1]),
        barmode='group'
    )
    
    return fig

def create_distribution_chart(results: List[Dict]) -> go.Figure:
    """創建分數分布圖表"""
    if not results:
        return go.Figure()
    
    # 收集所有分數
    all_scores = []
    for result in results:
        for metric, score in result['results'].items():
            if isinstance(score, (int, float)):
                all_scores.append(score)
    
    if not all_scores:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=all_scores,
        nbinsx=20,
        name='分數分布'
    ))
    
    fig.update_layout(
        title='評估分數分布',
        xaxis_title='分數',
        yaxis_title='頻率'
    )
    
    return fig

def show_dashboard_page():
    """顯示儀表板頁面"""
    st.markdown("## 📊 RAGAS 數據儀表板")
    st.markdown("全面的評估結果分析和可視化")
    
    # 載入數據
    results = load_evaluation_results()
    
    if not results:
        st.info("📊 沒有可用的評估結果數據")
        st.markdown("""
        ### 開始使用
        1. 在 **智能聊天** 頁面進行對話
        2. 在 **RAGAS 評估** 頁面執行評估
        3. 返回此頁面查看評估結果分析
        """)
        return
    
    # 總覽統計
    st.markdown("### 📈 總覽統計")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_evaluations = len(results)
        st.metric("總評估次數", total_evaluations)
    
    with col2:
        if results:
            latest_result = results[0]['results']
            avg_score = np.mean([score for score in latest_result.values() 
                               if isinstance(score, (int, float))])
            st.metric("最新平均分數", f"{avg_score:.3f}")
    
    with col3:
        if results:
            latest_result = results[0]['results']
            numeric_scores = {k: v for k, v in latest_result.items() 
                            if isinstance(v, (int, float))}
            if numeric_scores:
                best_metric = max(numeric_scores, key=numeric_scores.get)
                st.metric("最佳指標", best_metric, f"{numeric_scores[best_metric]:.3f}")
    
    with col4:
        if results:
            latest_result = results[0]['results']
            numeric_scores = {k: v for k, v in latest_result.items() 
                            if isinstance(v, (int, float))}
            if numeric_scores:
                worst_metric = min(numeric_scores, key=numeric_scores.get)
                st.metric("待改進指標", worst_metric, f"{numeric_scores[worst_metric]:.3f}")
    
    st.markdown("---")
    
    # 可視化選項
    st.markdown("### 📊 數據可視化")
    
    viz_tabs = st.tabs(["雷達圖", "趋勢圖", "對比分析", "分數分布"])
    
    with viz_tabs[0]:
        st.markdown("#### 🎯 指標雷達圖")
        radar_chart = create_metrics_overview_chart(results)
        if radar_chart.data:
            st.plotly_chart(radar_chart, use_container_width=True)
        else:
            st.info("沒有足夠的數據生成雷達圖")
    
    with viz_tabs[1]:
        st.markdown("#### 📈 評估趋勢")
        trend_chart = create_trend_chart(results)
        if trend_chart.data:
            st.plotly_chart(trend_chart, use_container_width=True)
        else:
            st.info("沒有足夠的數據生成趋勢圖")
    
    with viz_tabs[2]:
        st.markdown("#### ⚖️ 結果對比")
        if len(results) >= 2:
            comparison_chart = create_comparison_chart(results)
            if comparison_chart.data:
                st.plotly_chart(comparison_chart, use_container_width=True)
        else:
            st.info("需要至少2次評估結果才能進行對比分析")
    
    with viz_tabs[3]:
        st.markdown("#### 📊 分數分布")
        dist_chart = create_distribution_chart(results)
        if dist_chart.data:
            st.plotly_chart(dist_chart, use_container_width=True)
        else:
            st.info("沒有足夠的數據生成分布圖")
    
    st.markdown("---")
    
    # 詳細數據表格
    st.markdown("### 📋 評估歷史記錄")
    
    if st.checkbox("顯示詳細數據"):
        # 準備表格數據
        table_data = []
        for i, result in enumerate(results):
            row = {
                '序號': i + 1,
                '時間': result['timestamp'][:19].replace('T', ' '),
                '數據集': result['dataset_name'],
                '測試案例數': result['test_cases_count']
            }
            
            # 添加各個指標分數
            for metric, score in result['results'].items():
                if isinstance(score, (int, float)):
                    row[metric] = f"{score:.3f}"
            
            table_data.append(row)
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
    
    # 操作區域
    st.markdown("---")
    st.markdown("### 🛠️ 數據管理")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 刷新數據", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📥 導出報告", use_container_width=True):
            if results:
                # 創建導出數據
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'summary': {
                        'total_evaluations': len(results),
                        'date_range': f"{results[-1]['timestamp'][:10]} 至 {results[0]['timestamp'][:10]}"
                    },
                    'evaluations': results
                }
                
                st.download_button(
                    label="📄 下載 JSON 報告",
                    data=json.dumps(export_data, ensure_ascii=False, indent=2),
                    file_name=f"ragas_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.warning("沒有數據可導出")
    
    with col3:
        if st.button("🗑️ 清空數據", use_container_width=True):
            if st.session_state.get('confirm_clear', False):
                # 清空 session state
                if 'evaluation_results' in st.session_state:
                    del st.session_state.evaluation_results
                
                # 可選：刪除文件（謹慎操作）
                st.success("✅ 數據已清空")
                st.session_state.confirm_clear = False
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ 再次點擊確認清空所有評估數據")
    
    # 數據洞察
    if len(results) >= 3:
        st.markdown("---")
        st.markdown("### 🔍 數據洞察")
        
        # 計算改進趋勢
        latest_scores = [score for score in results[0]['results'].values() 
                        if isinstance(score, (int, float))]
        previous_scores = [score for score in results[1]['results'].values() 
                          if isinstance(score, (int, float))]
        
        if latest_scores and previous_scores:
            latest_avg = np.mean(latest_scores)
            previous_avg = np.mean(previous_scores)
            improvement = latest_avg - previous_avg
            
            if improvement > 0.01:
                st.success(f"📈 系統性能提升 {improvement:.3f} 分！")
            elif improvement < -0.01:
                st.warning(f"📉 系統性能下降 {abs(improvement):.3f} 分")
            else:
                st.info("📊 系統性能保持穩定")
        
        # 最佳實踐建議
        st.markdown("#### 💡 優化建議")
        
        if results:
            latest_result = results[0]['results']
            low_scores = {k: v for k, v in latest_result.items() 
                         if isinstance(v, (int, float)) and v < 0.7}
            
            if low_scores:
                st.warning("**需要關注的指標：**")
                for metric, score in low_scores.items():
                    st.markdown(f"- **{metric}**: {score:.3f} - 建議優化相關配置")
            else:
                st.success("🎉 所有指標表現良好！")

if __name__ == "__main__":
    show_dashboard_page()