#!/usr/bin/env python3
"""
RAGFlow 整合 Streamlit 應用
集成聊天對話與 RAGAS 評估分析的一站式解決方案
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import glob

# 導入 RAGAS 評估器
try:
    from ragas_evaluator import RAGASEvaluator, RAGAS_AVAILABLE
    RAGAS_EVALUATOR_AVAILABLE = True
except ImportError as e:
    RAGAS_AVAILABLE = False
    RAGAS_EVALUATOR_AVAILABLE = False
    print(f"⚠️ RAGAS 評估器載入失敗: {e}")

# 設置頁面配置
st.set_page_config(
    page_title="RAGFlow 智能評估平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "RAGFlow 智能評估平台 - 集成聊天對話與 RAGAS 評估分析"
    }
)

class RAGFlowClient:
    """RAGFlow API 客戶端"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_url = api_base_url.rstrip('/')
        self.session = requests.Session()
    
    def check_api_health(self) -> Dict:
        """檢查 API 健康狀態"""
        try:
            response = self.session.get(f"{self.api_url}/", timeout=5)
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'API 返回狀態碼: {response.status_code}'
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'連接失敗: {str(e)}'
            }
    
    def get_datasets(self) -> Dict:
        """獲取數據集列表"""
        try:
            response = self.session.get(f"{self.api_url}/datasets", timeout=10)
            response.raise_for_status()
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_chat_message(self, question: str, dataset_id: str, 
                         session_id: Optional[str] = None, 
                         user_id: Optional[str] = None) -> Dict:
        """發送聊天消息"""
        try:
            payload = {
                'question': question,
                'dataset_id': dataset_id,
                'quote': True
            }
            
            if session_id:
                payload['session_id'] = session_id
            if user_id:
                payload['user_id'] = user_id
            
            response = self.session.post(
                f"{self.api_url}/chat",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API 請求失敗: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知錯誤: {str(e)}'
            }

# RAGASEvaluator 現在從 ragas_evaluator.py 導入

def apply_global_theme():
    """應用全局主題樣式"""
    st.markdown("""
    <style>
    /* ===== 全局變量定義 ===== */
    :root {
        --primary-color: #667eea;
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #17a2b8;
        --light-bg: #f8f9fa;
        --white: #ffffff;
        --text-primary: #333333;
        --text-secondary: #6c757d;
        --border-color: #e9ecef;
        
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.08);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
        --shadow-lg: 0 8px 25px rgba(0,0,0,0.15);
        
        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        
        --space-sm: 0.5rem;
        --space-md: 1rem;
        --space-lg: 1.5rem;
        --space-xl: 2rem;
    }
    
    /* ===== 全局樣式 ===== */
    .stApp {
        background: var(--light-bg);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 頂部導航條 */
    .top-navbar {
        background: var(--primary-gradient);
        padding: var(--space-lg) var(--space-xl);
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 15px 15px;
        color: white;
        text-align: center;
        box-shadow: var(--shadow-md);
    }
    
    .top-navbar h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .top-navbar p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* 側邊欄樣式 */
    .sidebar-content {
        background: var(--white);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        margin-bottom: var(--space-md);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .sidebar-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-md);
        padding-bottom: var(--space-sm);
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* 按鈕樣式增強 */
    .stButton > button {
        background: var(--primary-gradient);
        color: var(--white);
        border: none;
        border-radius: var(--radius-md);
        padding: var(--space-sm) var(--space-lg);
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* 指標卡片 */
    .stMetric {
        background: var(--white);
        padding: var(--space-lg);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary-color);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    /* 聊天容器 */
    .chat-container {
        height: 70vh;
        overflow-y: auto;
        padding: var(--space-md);
        background: var(--light-bg);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        margin-bottom: var(--space-md);
    }
    
    /* 消息氣泡 */
    .user-message {
        background: var(--primary-gradient);
        color: white;
        padding: var(--space-md) var(--space-lg);
        border-radius: 20px 20px 5px 20px;
        margin: var(--space-md) 0 var(--space-md) 30%;
        max-width: 70%;
        box-shadow: var(--shadow-sm);
    }
    
    .bot-message {
        background: var(--white);
        color: var(--text-primary);
        padding: var(--space-md) var(--space-lg);
        border-radius: 20px 20px 20px 5px;
        margin: var(--space-md) 30% var(--space-md) 0;
        max-width: 70%;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    /* 響應式設計 */
    @media screen and (max-width: 768px) {
        .main .block-container {
            padding: var(--space-sm);
            max-width: 100%;
        }
        
        .top-navbar {
            margin: -1rem -0.5rem 1rem -0.5rem;
            padding: var(--space-lg) var(--space-md);
        }
        
        .top-navbar h1 {
            font-size: 1.8rem;
        }
        
        .user-message,
        .bot-message {
            max-width: 85%;
            margin-left: 0;
            margin-right: 0;
        }
        
        .user-message {
            margin-left: 15%;
        }
        
        .bot-message {
            margin-right: 15%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """初始化會話狀態"""
    if 'client' not in st.session_state:
        st.session_state.client = RAGFlowClient()
    
    if 'evaluator' not in st.session_state and RAGAS_EVALUATOR_AVAILABLE:
        try:
            st.session_state.evaluator = RAGASEvaluator(st.session_state.client)
        except Exception as e:
            print(f"⚠️ RAGAS 評估器初始化失敗: {e}")
            st.session_state.evaluator = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"streamlit_user_{uuid.uuid4().hex[:8]}"
    
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False
    
    if 'evaluation_step' not in st.session_state:
        st.session_state.evaluation_step = 1
    
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = None

def render_top_navbar():
    """渲染頂部導航條"""
    st.markdown("""
    <div class="top-navbar">
        <h1>🤖 RAGFlow 智能評估平台</h1>
        <p>集成聊天對話與 RAGAS 評估分析的一站式解決方案</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_navigation():
    """渲染側邊欄導航"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">🧭 功能導航</div>', unsafe_allow_html=True)
        
        # 導航選項
        nav_options = [
            {"key": "home", "icon": "🏠", "label": "首頁儀表板", "desc": "總覽和快速訪問"},
            {"key": "chat", "icon": "💬", "label": "RAG 智能聊天", "desc": "與知識庫對話"},
            {"key": "evaluation", "icon": "📊", "label": "RAGAS 評估", "desc": "系統性能評估"},
            {"key": "results", "icon": "📈", "label": "結果分析", "desc": "評估結果視覺化"},
            {"key": "settings", "icon": "⚙️", "label": "系統設置", "desc": "配置和管理"}
        ]
        
        # 渲染導航按鈕
        for option in nav_options:
            if st.button(
                f"{option['icon']} {option['label']}",
                key=f"nav_{option['key']}",
                help=option['desc'],
                use_container_width=True
            ):
                st.session_state.current_page = option["key"]
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 系統狀態區
        render_system_status_sidebar()

def render_system_status_sidebar():
    """系統狀態側邊欄"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-header">📡 系統狀態</div>', unsafe_allow_html=True)
        
        # API 連接狀態
        if st.button("🔄 檢查 API 連接", use_container_width=True):
            with st.spinner("檢查中..."):
                health_result = st.session_state.client.check_api_health()
                if health_result['success']:
                    st.session_state.api_connected = True
                    st.success("✅ API 連接正常")
                else:
                    st.session_state.api_connected = False
                    st.error(f"❌ {health_result['error']}")
        
        # 顯示連接狀態
        if st.session_state.api_connected:
            st.success("✅ FastAPI: 已連接")
        else:
            st.error("❌ FastAPI: 未連接")
        
        # RAGAS 狀態
        if RAGAS_AVAILABLE:
            st.success("✅ RAGAS: 已安裝")
        else:
            st.warning("⚠️ RAGAS: 未安裝")
        
        # 快速統計
        if hasattr(st.session_state, 'quick_stats'):
            stats = st.session_state.quick_stats
            st.markdown(f"""
            **📊 快速統計**
            - 總評估: {stats.get('total_evaluations', 0)}
            - 通過率: {stats.get('pass_rate', 0):.1%}
            - 上次更新: {stats.get('last_update', 'N/A')}
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """主應用程序"""
    # 應用全局主題
    apply_global_theme()
    
    # 初始化會話狀態
    initialize_session_state()
    
    # 渲染頂部導航條
    render_top_navbar()
    
    # 渲染側邊欄導航
    render_sidebar_navigation()
    
    # 根據當前頁面渲染對應內容
    current_page = st.session_state.current_page
    
    if current_page == 'home':
        render_home_page()
    elif current_page == 'chat':
        render_chat_page()
    elif current_page == 'evaluation':
        render_evaluation_page()
    elif current_page == 'results':
        render_results_page()
    elif current_page == 'settings':
        render_settings_page()

def render_home_page():
    """首頁儀表板"""
    st.markdown("## 🏠 首頁儀表板")
    
    # 快速統計卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 總評估次數",
            value="156",
            delta="12"
        )
    
    with col2:
        st.metric(
            label="✅ 平均通過率",
            value="87.3%",
            delta="2.1%"
        )
    
    with col3:
        st.metric(
            label="🔍 平均忠實度",
            value="0.847",
            delta="0.023"
        )
    
    with col4:
        st.metric(
            label="💬 聊天會話",
            value="42",
            delta="8"
        )
    
    st.divider()
    
    # 快速操作區
    st.markdown("### 🚀 快速操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 開始聊天", use_container_width=True, type="primary"):
            st.session_state.current_page = 'chat'
            st.rerun()
    
    with col2:
        if st.button("📊 新建評估", use_container_width=True):
            st.session_state.current_page = 'evaluation'
            st.rerun()
    
    with col3:
        if st.button("📈 查看結果", use_container_width=True):
            st.session_state.current_page = 'results'
            st.rerun()
    
    st.divider()
    
    # 最近活動
    st.markdown("### 📝 最近活動")
    
    activities = [
        {"time": "2 分鐘前", "action": "完成評估", "target": "憲法與行政法數據集", "result": "通過率 89%"},
        {"time": "15 分鐘前", "action": "聊天對話", "target": "民法相關問題", "result": "7 次問答"},
        {"time": "1 小時前", "action": "創建評估", "target": "刑法數據集", "result": "20 個測試案例"},
        {"time": "3 小時前", "action": "導出結果", "target": "評估報告", "result": "PDF 格式"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        **{activity['time']}** - {activity['action']}: {activity['target']}  
        *結果: {activity['result']}*
        """)

def render_chat_page():
    """聊天頁面 - 待實現詳細內容"""
    st.markdown("## 💬 RAG 智能聊天")
    st.info("🚧 聊天功能正在開發中...")
    
    # 基礎聊天界面框架
    if not st.session_state.api_connected:
        st.warning("⚠️ 請先在側邊欄檢查 API 連接")
        return
    
    # 數據集選擇
    datasets_result = st.session_state.client.get_datasets()
    if datasets_result['success']:
        datasets = datasets_result['data']
        if datasets:
            selected_dataset = st.selectbox(
                "📚 選擇知識庫",
                options=datasets,
                format_func=lambda x: f"{x.get('name', 'Unknown')} ({x.get('document_count', 0)} 文檔)"
            )
            st.session_state.selected_dataset = selected_dataset
        else:
            st.warning("沒有可用的數據集")
            return
    else:
        st.error(f"載入數據集失敗: {datasets_result['error']}")
        return
    
    # 聊天歷史顯示
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align: center; color: #6c757d; margin-top: 3rem;">
            <h4>👋 歡迎使用 RAGFlow 智能助手</h4>
            <p>請在下方輸入您的問題，我將基於選定的知識庫為您提供準確的回答</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 您:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bot-message">
                    <strong>🤖 RAGFlow:</strong><br>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
                
                if message.get('sources'):
                    with st.expander(f"📖 參考來源 ({len(message['sources'])} 個)"):
                        for i, source in enumerate(message['sources'], 1):
                            st.write(f"**{i}. {source.get('doc_name', 'Unknown')}**")
                            st.write(source.get('content', '')[:200] + "...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 輸入區域
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "輸入您的問題:",
                placeholder="例如：什麼是憲法第7條的平等原則？",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("🚀 發送", use_container_width=True)
    
    # 處理用戶輸入
    if submit_button and user_input.strip():
        # 添加用戶消息
        user_message = {
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(user_message)
        
        # 發送到 RAGFlow API
        with st.spinner("🔍 正在搜索相關信息..."):
            try:
                chat_result = st.session_state.client.send_chat_message(
                    question=user_input,
                    dataset_id=st.session_state.selected_dataset['id'],
                    session_id=st.session_state.current_session_id,
                    user_id=st.session_state.user_id
                )
            except Exception as e:
                st.error(f"❌ 發送請求時發生錯誤: {str(e)}")
                return
        
        if chat_result['success']:
            response_data = chat_result['data']
            
            # 更新會話 ID
            st.session_state.current_session_id = response_data.get('session_id')
            
            # 添加機器人回應
            bot_message = {
                'role': 'bot',
                'content': response_data.get('answer', '抱歉，無法生成回答'),
                'sources': response_data.get('sources', []),
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(bot_message)
            
            st.rerun()
        else:
            st.error(f"❌ 聊天請求失敗: {chat_result['error']}")

def render_evaluation_page():
    """RAGAS 評估頁面"""
    st.markdown("## 📊 RAGAS 評估")
    
    current_step = st.session_state.get('evaluation_step', 1)
    
    # 步驟指示器
    render_evaluation_steps(current_step)
    
    if current_step == 1:
        render_evaluation_config()
    elif current_step == 2:
        render_data_preparation()
    elif current_step == 3:
        render_evaluation_execution()
    elif current_step == 4:
        render_evaluation_results()

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

def render_results_page():
    """結果分析頁面"""
    st.markdown("## 📈 結果分析")
    
    # 載入可用的評估結果
    available_results = load_available_results()
    
    if not available_results:
        render_no_results_message()
        return
    
    # 控制面板
    render_results_control_panel(available_results)
    
    # 如果有選中的結果，顯示分析
    if hasattr(st.session_state, 'selected_result_data'):
        render_results_dashboard()
    else:
        st.info("📊 請在上方選擇一個評估結果進行分析")

def load_available_results():
    """載入可用的評估結果"""
    try:
        # 查找評估結果文件
        result_files = glob.glob("ragas_evaluation_*.json")
        
        # 如果沒有真實結果文件，返回空列表
        if not result_files:
            return []
        
        results = []
        for file in result_files[:5]:  # 最多載入5個文件
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append({
                        'name': f"評估結果 - {data.get('metadata', {}).get('dataset_name', 'Unknown')}",
                        'data': data,
                        'file': file
                    })
            except Exception as e:
                st.warning(f"載入文件 {file} 失敗: {e}")
        
        return results
    except Exception as e:
        st.error(f"載入結果失敗: {e}")
        return []

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

def render_no_results_message():
    """渲染無結果消息"""
    st.info("📊 沒有找到評估結果文件")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 開始新評估", type="primary", use_container_width=True):
            st.session_state.current_page = 'evaluation'
            st.rerun()
    
    with col2:
        if st.button("🚀 開始新評估", type="primary", use_container_width=True):
            st.session_state.current_page = 'evaluation'
            st.rerun()

def render_settings_page():
    """設置頁面"""
    st.markdown("## ⚙️ 系統設置")
    
    st.markdown("### 🔗 API 設置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input("FastAPI 地址", value="http://localhost:8000")
        timeout = st.slider("請求超時 (秒)", 5, 60, 30)
    
    with col2:
        auto_retry = st.checkbox("自動重試", value=True)
        max_retries = st.slider("最大重試次數", 1, 5, 3)
    
    if st.button("💾 保存設置", type="primary"):
        st.success("✅ 設置已保存")
    
    st.divider()
    
    st.markdown("### 🎨 界面設置")
    
    theme = st.selectbox("主題", ["淺色", "深色", "自動"])
    language = st.selectbox("語言", ["繁體中文", "簡體中文", "English"])
    
    st.divider()
    
    st.markdown("### 📊 評估設置")
    
    default_threshold = st.slider("預設通過閾值", 0.5, 0.9, 0.7)
    auto_save_results = st.checkbox("自動保存評估結果", value=True)
    
    if st.button("🔄 重置為預設值"):
        st.info("所有設置已重置為預設值")

if __name__ == "__main__":
    main()