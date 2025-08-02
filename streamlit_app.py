#!/usr/bin/env python3
"""
RAGFlow Streamlit 聊天機器人前端
與 FastAPI 後端交互的 RAG 聊天界面
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import uuid

# 配置頁面
st.set_page_config(
    page_title="RAGFlow 聊天機器人",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .bot-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    .source-item {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        border-left: 3px solid #4caf50;
    }
    
    .session-info {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ff9800;
    }
    
    .error-message {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f44336;
    }
    
    .success-message {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitRAGClient:
    """Streamlit RAG 客戶端"""
    
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
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_sessions(self) -> Dict:
        """獲取活躍會話列表"""
        try:
            response = self.session.get(f"{self.api_url}/sessions", timeout=10)
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
    
    def delete_session(self, session_id: str) -> Dict:
        """刪除會話"""
        try:
            response = self.session.delete(f"{self.api_url}/sessions/{session_id}", timeout=10)
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

def initialize_session_state():
    """初始化 Streamlit 會話狀態"""
    if 'client' not in st.session_state:
        st.session_state.client = StreamlitRAGClient()
    
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

def check_api_connection():
    """檢查 API 連接狀態"""
    with st.spinner("檢查 API 連接..."):
        health_result = st.session_state.client.check_api_health()
        
        if health_result['success']:
            st.session_state.api_connected = True
            st.success("✅ API 連接正常")
            
            # 顯示 API 信息
            api_info = health_result['data']
            st.info(f"🔗 服務: {api_info.get('service', 'Unknown')} | "
                   f"版本: {api_info.get('version', 'Unknown')} | "
                   f"狀態: {api_info.get('status', 'Unknown')}")
        else:
            st.session_state.api_connected = False
            st.error(f"❌ API 連接失敗: {health_result['error']}")
            st.info("請確保 FastAPI 服務器正在運行: `python3 fastapi_server.py`")

def load_datasets():
    """載入數據集列表"""
    if not st.session_state.api_connected:
        return []
    
    with st.spinner("載入數據集..."):
        datasets_result = st.session_state.client.get_datasets()
        
        if datasets_result['success']:
            return datasets_result['data']
        else:
            st.error(f"❌ 載入數據集失敗: {datasets_result['error']}")
            return []

def display_chat_message(message: Dict, is_user: bool = True):
    """顯示聊天消息"""
    if is_user:
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 你:</strong><br>
            {message['content']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>🤖 RAGFlow:</strong><br>
            {message['content']}
        </div>
        """, unsafe_allow_html=True)
        
        # 顯示來源信息
        if message.get('sources'):
            with st.expander(f"📖 參考來源 ({len(message['sources'])} 個)", expanded=False):
                for i, source in enumerate(message['sources'], 1):
                    if isinstance(source, dict):
                        doc_name = source.get('doc_name', 'Unknown')
                        content = source.get('content', '')[:200]
                        
                        st.markdown(f"""
                        <div class="source-item">
                            <strong>{i}. {doc_name}</strong><br>
                            <small>{content}{'...' if len(source.get('content', '')) > 200 else ''}</small>
                        </div>
                        """, unsafe_allow_html=True)

def main():
    """主應用程序"""
    # 初始化會話狀態
    initialize_session_state()
    
    # 主標題
    st.markdown("""
    <div class="main-header">
        <h1>🤖 RAGFlow 聊天機器人</h1>
        <p>基於 RAGFlow 的智能問答系統</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 側邊欄配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # API 連接狀態
        st.subheader("🔗 API 連接")
        api_url = st.text_input("API 地址", value="http://localhost:8000")
        
        if st.button("檢查連接"):
            st.session_state.client = StreamlitRAGClient(api_url)
            check_api_connection()
        
        # 顯示連接狀態
        if st.session_state.api_connected:
            st.success("✅ 已連接")
        else:
            st.error("❌ 未連接")
            st.stop()
        
        st.divider()
        
        # 數據集選擇
        st.subheader("📚 數據集選擇")
        datasets = load_datasets()
        
        if datasets:
            dataset_options = {f"{ds['name']} ({ds['document_count']} 文件)": ds for ds in datasets}
            selected_dataset_name = st.selectbox(
                "選擇知識庫",
                options=list(dataset_options.keys()),
                index=0
            )
            
            st.session_state.selected_dataset = dataset_options[selected_dataset_name]
            
            # 顯示數據集信息
            dataset = st.session_state.selected_dataset
            st.info(f"""
            **數據集信息:**
            - 名稱: {dataset['name']}
            - 文件數量: {dataset['document_count']}
            - ID: {dataset['id'][:16]}...
            """)
        else:
            st.warning("沒有可用的數據集")
            st.stop()
        
        st.divider()
        
        # 會話管理
        st.subheader("💬 會話管理")
        
        # 顯示當前會話信息
        if st.session_state.current_session_id:
            st.markdown(f"""
            <div class="session-info">
                <strong>當前會話:</strong><br>
                <small>{st.session_state.current_session_id[:16]}...</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("尚未開始會話")
        
        # 會話操作按鈕
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🆕 新會話"):
                st.session_state.current_session_id = None
                st.session_state.chat_history = []
                st.success("已開始新會話")
                st.rerun()
        
        with col2:
            if st.button("🗑️ 清除歷史"):
                st.session_state.chat_history = []
                st.success("已清除聊天歷史")
                st.rerun()
        
        # 顯示活躍會話
        if st.button("📊 查看活躍會話"):
            sessions_result = st.session_state.client.get_sessions()
            if sessions_result['success']:
                sessions = sessions_result['data']
                if sessions:
                    st.write(f"找到 {len(sessions)} 個活躍會話:")
                    for session in sessions[:5]:  # 只顯示前5個
                        st.text(f"• {session['session_id'][:16]}... ({session['dataset_name']})")
                else:
                    st.info("沒有活躍會話")
            else:
                st.error(f"獲取會話失敗: {sessions_result['error']}")
    
    # 主聊天界面
    st.header("💬 聊天對話")
    
    # 顯示聊天歷史
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    display_chat_message(message, is_user=True)
                else:
                    display_chat_message(message, is_user=False)
        else:
            st.info("👋 歡迎使用 RAGFlow 聊天機器人！請在下方輸入您的問題。")
    
    # 聊天輸入
    st.divider()
    
    # 使用表單來處理輸入
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "輸入您的問題:",
                placeholder="例如：什麼是憲法？",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("發送 🚀", use_container_width=True)
    
    # 處理用戶輸入
    if submit_button and user_input.strip():
        if not st.session_state.selected_dataset:
            st.error("請先選擇數據集")
            return
        
        # 添加用戶消息到歷史
        user_message = {
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(user_message)
        
        # 發送聊天請求
        with st.spinner("🔍 正在搜索相關信息..."):
            chat_result = st.session_state.client.send_chat_message(
                question=user_input,
                dataset_id=st.session_state.selected_dataset['id'],
                session_id=st.session_state.current_session_id,
                user_id=st.session_state.user_id
            )
        
        if chat_result['success']:
            response_data = chat_result['data']
            
            # 更新會話 ID
            st.session_state.current_session_id = response_data['session_id']
            
            # 添加機器人回應到歷史
            bot_message = {
                'role': 'bot',
                'content': response_data['answer'],
                'sources': response_data.get('sources', []),
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(bot_message)
            
            # 重新運行以顯示新消息
            st.rerun()
        else:
            st.error(f"❌ 聊天請求失敗: {chat_result['error']}")
    
    # 快速問題按鈕
    st.divider()
    st.subheader("💡 快速問題")
    
    quick_questions = [
        "這個數據集包含什麼內容？",
        "請簡單介紹主要概念",
        "有什麼重要信息？",
        "能否提供更多細節？"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}"):
                # 模擬表單提交
                st.session_state.quick_question = question
                st.rerun()
    
    # 處理快速問題
    if hasattr(st.session_state, 'quick_question'):
        question = st.session_state.quick_question
        del st.session_state.quick_question
        
        if st.session_state.selected_dataset:
            # 添加用戶消息
            user_message = {
                'role': 'user',
                'content': question,
                'timestamp': datetime.now()
            }
            st.session_state.chat_history.append(user_message)
            
            # 發送請求
            with st.spinner("🔍 正在搜索相關信息..."):
                chat_result = st.session_state.client.send_chat_message(
                    question=question,
                    dataset_id=st.session_state.selected_dataset['id'],
                    session_id=st.session_state.current_session_id,
                    user_id=st.session_state.user_id
                )
            
            if chat_result['success']:
                response_data = chat_result['data']
                st.session_state.current_session_id = response_data['session_id']
                
                bot_message = {
                    'role': 'bot',
                    'content': response_data['answer'],
                    'sources': response_data.get('sources', []),
                    'timestamp': datetime.now()
                }
                st.session_state.chat_history.append(bot_message)
                st.rerun()
    
    # 頁腳信息
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>
        🤖 RAGFlow 聊天機器人 | 
        基於 <a href="https://ragflow.io" target="_blank">RAGFlow</a> 構建 | 
        用戶 ID: {user_id}
        </small>
    </div>
    """.format(user_id=st.session_state.user_id), unsafe_allow_html=True)

if __name__ == "__main__":
    main()