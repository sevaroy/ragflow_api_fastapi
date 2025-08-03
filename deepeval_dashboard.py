#!/usr/bin/env python3
"""
DeepEval 評估結果儀表板
使用 Streamlit 創建專業的評估數據視覺化界面
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import glob

# 設置頁面配置
st.set_page_config(
    page_title="DeepEval 評估儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DeepEvalDashboard:
    """DeepEval 儀表板類"""
    
    def __init__(self):
        self.evaluation_data = None
        self.metrics_data = None
        self.summary_stats = None
    
    def load_evaluation_results(self, file_path: str) -> bool:
        """載入評估結果 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.evaluation_data = json.load(f)
            
            # 處理數據格式
            if isinstance(self.evaluation_data, list):
                # 如果是結果列表
                self.process_results_list()
            elif isinstance(self.evaluation_data, dict):
                # 如果是包含摘要的字典
                self.process_results_dict()
            
            return True
            
        except Exception as e:
            st.error(f"載入評估結果失敗: {e}")
            return False
    
    def process_results_list(self):
        """處理結果列表格式"""
        results_df = []
        
        for i, result in enumerate(self.evaluation_data):
            row = {
                'test_id': result.get('test_case_id', f'test_{i+1}'),
                'question': result.get('question', ''),
                'actual_output': result.get('actual_output', ''),
                'expected_output': result.get('expected_output', ''),
                'overall_score': result.get('overall_score', 0),
                'passed': result.get('passed', False)
            }
            
            # 添加各項指標分數
            metrics_scores = result.get('metrics_scores', {})
            for metric, score in metrics_scores.items():
                row[metric] = score
            
            results_df.append(row)
        
        self.metrics_data = pd.DataFrame(results_df)
        self.calculate_summary_stats()
    
    def process_results_dict(self):
        """處理包含摘要的字典格式"""
        if 'dataset_results' in self.evaluation_data:
            # 處理多數據集結果
            all_results = []
            for dataset_result in self.evaluation_data['dataset_results']:
                # 這裡需要根據實際數據結構調整
                all_results.extend(dataset_result.get('results', []))
            self.evaluation_data = all_results
            self.process_results_list()
        else:
            # 單一結果集
            self.process_results_list()
    
    def calculate_summary_stats(self):
        """計算摘要統計"""
        if self.metrics_data is None or self.metrics_data.empty:
            return
        
        total_cases = len(self.metrics_data)
        passed_cases = self.metrics_data['passed'].sum()
        pass_rate = passed_cases / total_cases * 100 if total_cases > 0 else 0
        avg_score = self.metrics_data['overall_score'].mean()
        
        # 計算各指標統計
        metric_columns = [col for col in self.metrics_data.columns 
                         if col not in ['test_id', 'question', 'actual_output', 
                                       'expected_output', 'overall_score', 'passed']]
        
        metric_stats = {}
        for metric in metric_columns:
            if metric in self.metrics_data.columns:
                metric_stats[metric] = {
                    'mean': self.metrics_data[metric].mean(),
                    'min': self.metrics_data[metric].min(),
                    'max': self.metrics_data[metric].max(),
                    'std': self.metrics_data[metric].std()
                }
        
        self.summary_stats = {
            'total_cases': total_cases,
            'passed_cases': passed_cases,
            'pass_rate': pass_rate,
            'avg_score': avg_score,
            'metric_stats': metric_stats
        }
    
    def render_header(self):
        """渲染頁面標題"""
        st.title("📊 DeepEval 評估儀表板")
        st.markdown("---")
        
        # 顯示載入的文件信息
        if hasattr(st.session_state, 'loaded_file'):
            st.info(f"📁 當前載入文件: {st.session_state.loaded_file}")
    
    def render_summary_metrics(self):
        """渲染摘要指標"""
        if not self.summary_stats:
            st.warning("沒有可用的摘要統計數據")
            return
        
        st.subheader("📈 整體表現摘要")
        
        # 創建四列布局
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="總測試案例",
                value=self.summary_stats['total_cases']
            )
        
        with col2:
            st.metric(
                label="通過案例",
                value=self.summary_stats['passed_cases'],
                delta=f"{self.summary_stats['pass_rate']:.1f}%"
            )
        
        with col3:
            st.metric(
                label="通過率",
                value=f"{self.summary_stats['pass_rate']:.1f}%",
                delta="目標: 80%" if self.summary_stats['pass_rate'] >= 80 else "需要改進"
            )
        
        with col4:
            st.metric(
                label="平均分數",
                value=f"{self.summary_stats['avg_score']:.3f}",
                delta="良好" if self.summary_stats['avg_score'] >= 0.7 else "需要改進"
            )
    
    def render_metrics_overview(self):
        """渲染指標概覽"""
        if not self.summary_stats or not self.summary_stats['metric_stats']:
            return
        
        st.subheader("🎯 評估指標詳情")
        
        # 創建指標對比圖
        metrics_df = pd.DataFrame(self.summary_stats['metric_stats']).T
        metrics_df = metrics_df.reset_index()
        metrics_df.columns = ['metric', 'mean', 'min', 'max', 'std']
        
        # 雷達圖
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=metrics_df['mean'].tolist(),
            theta=metrics_df['metric'].tolist(),
            fill='toself',
            name='平均分數',
            line_color='rgb(0, 123, 255)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="評估指標雷達圖"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            # 指標詳細表格
            st.subheader("指標統計表")
            
            # 格式化數據
            display_df = metrics_df.copy()
            for col in ['mean', 'min', 'max', 'std']:
                display_df[col] = display_df[col].round(3)
            
            st.dataframe(
                display_df,
                column_config={
                    "metric": "指標",
                    "mean": "平均值",
                    "min": "最小值", 
                    "max": "最大值",
                    "std": "標準差"
                },
                hide_index=True,
                use_container_width=True
            )
    
    def render_detailed_results(self):
        """渲染詳細結果"""
        if self.metrics_data is None or self.metrics_data.empty:
            return
        
        st.subheader("📋 詳細評估結果")
        
        # 篩選選項
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_passed_only = st.checkbox("只顯示通過的案例")
        
        with col2:
            show_failed_only = st.checkbox("只顯示失敗的案例")
        
        with col3:
            min_score = st.slider("最低分數篩選", 0.0, 1.0, 0.0, 0.1)
        
        # 應用篩選
        filtered_data = self.metrics_data.copy()
        
        if show_passed_only:
            filtered_data = filtered_data[filtered_data['passed'] == True]
        elif show_failed_only:
            filtered_data = filtered_data[filtered_data['passed'] == False]
        
        filtered_data = filtered_data[filtered_data['overall_score'] >= min_score]
        
        # 顯示篩選後的結果
        st.write(f"顯示 {len(filtered_data)} / {len(self.metrics_data)} 個結果")
        
        # 詳細結果展示
        for idx, row in filtered_data.iterrows():
            with st.expander(
                f"{'✅' if row['passed'] else '❌'} {row['test_id']} - 分數: {row['overall_score']:.3f}",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**問題:**")
                    st.write(row['question'])
                    
                    st.write("**實際回答:**")
                    st.write(row['actual_output'][:300] + "..." if len(row['actual_output']) > 300 else row['actual_output'])
                    
                    if row['expected_output']:
                        st.write("**期望回答:**")
                        st.write(row['expected_output'][:300] + "..." if len(row['expected_output']) > 300 else row['expected_output'])
                
                with col2:
                    st.write("**指標分數:**")
                    
                    # 顯示各項指標
                    metric_columns = [col for col in row.index 
                                    if col not in ['test_id', 'question', 'actual_output', 
                                                  'expected_output', 'overall_score', 'passed']]
                    
                    for metric in metric_columns:
                        if pd.notna(row[metric]):
                            score = row[metric]
                            color = "green" if score >= 0.7 else "orange" if score >= 0.5 else "red"
                            st.markdown(f"**{metric}**: <span style='color:{color}'>{score:.3f}</span>", 
                                      unsafe_allow_html=True)
    
    def render_charts(self):
        """渲染圖表分析"""
        if self.metrics_data is None or self.metrics_data.empty:
            return
        
        st.subheader("📊 數據分析圖表")
        
        # 分數分布直方圖
        fig_hist = px.histogram(
            self.metrics_data, 
            x='overall_score',
            nbins=20,
            title="整體分數分布",
            labels={'overall_score': '整體分數', 'count': '案例數量'}
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # 通過/失敗比例餅圖
        pass_fail_counts = self.metrics_data['passed'].value_counts()
        
        fig_pie = px.pie(
            values=pass_fail_counts.values,
            names=['失敗', '通過'] if False in pass_fail_counts.index else ['通過'],
            title="通過/失敗比例",
            color_discrete_map={True: 'green', False: 'red'}
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 指標相關性熱力圖
            metric_columns = [col for col in self.metrics_data.columns 
                            if col not in ['test_id', 'question', 'actual_output', 
                                          'expected_output', 'passed']]
            
            if len(metric_columns) > 1:
                corr_matrix = self.metrics_data[metric_columns].corr()
                
                fig_heatmap = px.imshow(
                    corr_matrix,
                    title="指標相關性熱力圖",
                    color_continuous_scale="RdBu",
                    aspect="auto"
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
    
    def render_export_options(self):
        """渲染導出選項"""
        st.subheader("💾 導出選項")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("導出 CSV"):
                if self.metrics_data is not None:
                    csv = self.metrics_data.to_csv(index=False)
                    st.download_button(
                        label="下載 CSV 文件",
                        data=csv,
                        file_name=f"deepeval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("導出摘要報告"):
                if self.summary_stats:
                    report = self.generate_summary_report()
                    st.download_button(
                        label="下載摘要報告",
                        data=report,
                        file_name=f"deepeval_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
        
        with col3:
            if st.button("導出 JSON"):
                if self.evaluation_data:
                    json_str = json.dumps(self.evaluation_data, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="下載 JSON 文件",
                        data=json_str,
                        file_name=f"deepeval_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
    
    def generate_summary_report(self) -> str:
        """生成摘要報告"""
        if not self.summary_stats:
            return "沒有可用的統計數據"
        
        report = f"""# DeepEval 評估摘要報告

## 📊 整體統計
- **總測試案例**: {self.summary_stats['total_cases']}
- **通過案例**: {self.summary_stats['passed_cases']}
- **通過率**: {self.summary_stats['pass_rate']:.1f}%
- **平均分數**: {self.summary_stats['avg_score']:.3f}

## 📋 指標詳情
"""
        
        for metric, stats in self.summary_stats['metric_stats'].items():
            report += f"""
### {metric}
- 平均值: {stats['mean']:.3f}
- 最小值: {stats['min']:.3f}
- 最大值: {stats['max']:.3f}
- 標準差: {stats['std']:.3f}
"""
        
        report += f"""
## 💡 建議
- {'✅ 系統表現良好' if self.summary_stats['pass_rate'] >= 80 else '⚠️ 需要改進系統性能'}
- {'✅ 平均分數達標' if self.summary_stats['avg_score'] >= 0.7 else '⚠️ 需要提升回答品質'}

---
報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

def main():
    """主函數"""
    dashboard = DeepEvalDashboard()
    
    # 渲染標題
    dashboard.render_header()
    
    # 側邊欄 - 文件載入
    st.sidebar.title("📁 數據載入")
    
    # 查找可用的評估結果文件
    json_files = glob.glob("*.json") + glob.glob("evaluation_*.json")
    
    if json_files:
        st.sidebar.subheader("選擇現有文件")
        selected_file = st.sidebar.selectbox(
            "可用的評估結果文件:",
            [""] + json_files
        )
        
        if selected_file and st.sidebar.button("載入選中文件"):
            if dashboard.load_evaluation_results(selected_file):
                st.session_state.loaded_file = selected_file
                st.success(f"✅ 成功載入: {selected_file}")
                st.rerun()
    
    # 文件上傳
    st.sidebar.subheader("上傳新文件")
    uploaded_file = st.sidebar.file_uploader(
        "上傳 DeepEval 結果 JSON 文件",
        type=['json'],
        help="上傳由 DeepEval 生成的評估結果 JSON 文件"
    )
    
    if uploaded_file is not None:
        # 保存上傳的文件
        file_path = f"uploaded_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if dashboard.load_evaluation_results(file_path):
            st.session_state.loaded_file = file_path
            st.success(f"✅ 成功載入上傳文件: {uploaded_file.name}")
            st.rerun()
    
    # 如果有數據，顯示儀表板
    if dashboard.summary_stats:
        # 渲染各個部分
        dashboard.render_summary_metrics()
        st.markdown("---")
        
        dashboard.render_metrics_overview()
        st.markdown("---")
        
        dashboard.render_charts()
        st.markdown("---")
        
        dashboard.render_detailed_results()
        st.markdown("---")
        
        dashboard.render_export_options()
    
    else:
        # 沒有數據時的提示
        st.info("👆 請在側邊欄載入 DeepEval 評估結果文件來開始分析")
        
        # 顯示示例數據格式
        st.subheader("📋 支援的數據格式")
        
        example_data = {
            "test_case_id": "test_1",
            "question": "什麼是憲法第7條？",
            "actual_output": "憲法第7條規定平等原則...",
            "expected_output": "憲法第7條規定中華民國人民在法律上一律平等...",
            "overall_score": 0.756,
            "passed": True,
            "metrics_scores": {
                "answer_relevancy": 0.823,
                "faithfulness": 0.789,
                "hallucination": 0.234
            }
        }
        
        st.json(example_data)
        
        st.markdown("""
        **支援的文件格式:**
        - 單一評估結果的 JSON 數組
        - 包含摘要統計的 JSON 對象
        - 由 `deepeval_integration.py` 生成的結果文件
        """)

if __name__ == "__main__":
    main()