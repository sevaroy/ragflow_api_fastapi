#!/usr/bin/env python3
"""
RAGFlow 整合智能平台
集成聊天對話、RAGAS 評估分析和數據儀表板的統一解決方案
"""

import streamlit as st
import os
import sys
from pathlib import Path

# 設置頁面配置
st.set_page_config(
    page_title="RAGFlow 智能評估平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "RAGFlow 智能評估平台 - 整合聊天對話與 RAGAS 評估分析的一站式解決方案"
    }
)

# 添加專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# 導入頁面模組
try:
    from pages import chat, evaluation, dashboard, settings
except ImportError:
    st.error("❌ 無法導入頁面模組，請確保 pages 目錄存在且包含必要的模組")
    st.stop()

# 全域 CSS 樣式
st.markdown("""
<style>
    /* 主要樣式 */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* 側邊欄樣式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 指標卡片樣式 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .metric-card h3 {
        color: #333;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin: 0;
    }
    
    /* 聊天樣式 */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
    }
    
    /* 評估結果樣式 */
    .evaluation-result {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    .score-excellent { color: #4caf50; font-weight: bold; }
    .score-good { color: #8bc34a; font-weight: bold; }
    .score-average { color: #ff9800; font-weight: bold; }
    .score-poor { color: #f44336; font-weight: bold; }
    
    /* 狀態消息樣式 */
    .status-success {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        color: #f57c00;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }
    
    /* 導航標籤樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
        color: #333;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        transform: translateY(-1px);
    }
    
    /* 隱藏 Streamlit 默認元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def main():
    """主應用程式入口"""
    
    # 應用標題
    st.markdown("""
    <div class="main-header">
        <h1>🤖 RAGFlow 智能評估平台</h1>
        <p>整合聊天對話、RAGAS 評估分析和數據儀表板的一站式解決方案</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化 session state
    if 'current_dataset' not in st.session_state:
        st.session_state.current_dataset = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = []
    if 'selected_dataset_id' not in st.session_state:
        st.session_state.selected_dataset_id = None
    
    # 側邊欄 - 應用導航和狀態
    with st.sidebar:
        st.markdown("## 🚀 應用導航")
        st.markdown("---")
        
        # 系統狀態檢查
        st.markdown("### 📊 系統狀態")
        
        # 檢查必要的環境變數
        ragflow_api_url = os.getenv('RAGFLOW_API_URL', 'http://localhost:8080')
        ragflow_api_key = os.getenv('RAGFLOW_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # 顯示配置狀態
        if ragflow_api_key:
            st.markdown("✅ RAGFlow API 已配置")
        else:
            st.markdown("❌ RAGFlow API 未配置")
        
        if openai_api_key:
            st.markdown("✅ OpenAI API 已配置")
        else:
            st.markdown("⚠️ OpenAI API 未配置 (RAGAS 功能受限)")
        
        st.markdown("---")
        
        # 當前選擇的數據集
        if st.session_state.current_dataset:
            st.markdown("### 📚 當前數據集")
            st.info(f"**{st.session_state.current_dataset.get('name', 'Unknown')}**")
        
        st.markdown("---")
        
        # 快速統計
        st.markdown("### 📈 快速統計")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("聊天記錄", len(st.session_state.chat_history))
        
        with col2:
            st.metric("評估結果", len(st.session_state.evaluation_results))
        
        st.markdown("---")
        
        # 系統設置按鈕
        if st.button("⚙️ 系統設置", use_container_width=True):
            st.session_state.show_settings = True
    
    # 主要內容區域 - 使用標籤頁
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 智能聊天", 
        "📏 RAGAS 評估", 
        "📊 數據儀表板", 
        "⚙️ 系統設置"
    ])
    
    with tab1:
        try:
            chat.show_chat_page()
        except Exception as e:
            st.error(f"聊天頁面載入錯誤: {e}")
            st.info("請檢查 RAGFlow 客戶端配置")
    
    with tab2:
        try:
            evaluation.show_evaluation_page()
        except Exception as e:
            st.error(f"評估頁面載入錯誤: {e}")
            st.info("請檢查 RAGAS 和相關依賴是否已安裝")
    
    with tab3:
        try:
            dashboard.show_dashboard_page()
        except Exception as e:
            st.error(f"儀表板頁面載入錯誤: {e}")
            st.info("請檢查 Plotly 是否已安裝")
    
    with tab4:
        try:
            settings.show_settings_page()
        except Exception as e:
            st.error(f"設置頁面載入錯誤: {e}")
            st.info("請檢查系統配置")
    

if __name__ == "__main__":
    main()