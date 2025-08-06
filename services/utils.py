"""
工具服務
"""
import streamlit as st
from typing import List, Dict, Any


def apply_global_theme() -> None:
    """應用全局主題樣式"""
    st.markdown("""
    <style>
    /* 全局樣式 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 聊天消息樣式 */
    .user-message {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .bot-message {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 聊天容器 */
    .chat-container {
        height: 500px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        background-color: white;
        margin-bottom: 20px;
    }
    
    /* 按鈕樣式 */
    .stButton>button {
        border-radius: 8px;
    }
    
    /* 指標卡片 */
    .stMetric {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 側邊欄 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* 標題 */
    h1, h2, h3 {
        color: #333;
    }
    
    /* 鏈接 */
    a {
        color: #1976d2;
    }
    
    /* 表格 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* 分隔線 */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0));
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state() -> None:
    """初始化會話狀態"""
    # 頁面狀態
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # API 客戶端
    if 'client' not in st.session_state:
        from services.api_client import get_api_client
        st.session_state.client = get_api_client()
    
    # API 連接狀態
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False
    
    # 用戶信息
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'user_001'
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    # 聊天歷史
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []  # type: List[Dict[str, Any]]
    
    # 評估步驟
    if 'evaluation_step' not in st.session_state:
        st.session_state.evaluation_step = 1
