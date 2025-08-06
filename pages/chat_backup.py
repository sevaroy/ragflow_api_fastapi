#!/usr/bin/env python3
"""
聊天頁面模組
整合 RAGFlow 聊天機器人功能
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os

# 導入 RAGFlow 客戶端
try:
    from ragflow_chatbot import RAGFlowOfficialClient
    RAGFLOW_AVAILABLE = True
except ImportError:
    RAGFLOW_AVAILABLE = False

class RAGFlowChatInterface:
    """RAGFlow 聊天界面類"""
    
    def __init__(self):
        self.client = None
        if RAGFLOW_AVAILABLE:
            self.client = RAGFlowOfficialClient()
        self.current_session_id = None
        self.current_chat_id = None
    
    def initialize_client(self) -> bool:
        """初始化 RAGFlow 客戶端"""
        if not RAGFLOW_AVAILABLE:
            st.error("❌ RAGFlow 客戶端不可用，請檢查安裝")
            return False
        
        try:
            self.client = RAGFlowOfficialClient()
            return True
        except Exception as e:
            st.error(f"❌ RAGFlow 客戶端初始化失敗: {e}")
            return False
    
    def get_datasets(self) -> List[Dict]:
        """獲取可用的數據集列表"""
        if not self.client:
            return []
        
        try:
            result = self.client.list_datasets()
            if result.get('success'):
                return result.get('data', [])
            else:
                st.error(f"獲取數據集失敗: {result.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            st.error(f"獲取數據集時發生錯誤: {e}")
            return []
    
    def create_chat_session(self, dataset_ids: List[str], chat_name: str) -> bool:
        """創建聊天會話"""
        if not self.client:
            return False
        
        try:
            result = self.client.create_chat(
                name=chat_name,
                dataset_ids=dataset_ids
            )
            
            if result.get('success'):
                chat_data = result.get('data', {})
                self.current_chat_id = chat_data.get('id')
                st.success(f"✅ 聊天會話創建成功: {chat_name}")
                return True
            else:
                st.error(f"❌ 創建聊天會話失敗: {result.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            st.error(f"❌ 創建聊天會話時發生錯誤: {e}")
            return False
    
    def send_message(self, message: str, conversation_id: str = None) -> Dict:
        """發送聊天消息"""
        if not self.client or not self.current_chat_id:
            return {'success': False, 'message': '聊天會話未初始化'}
        
        try:
            result = self.client.chat_with_assistant(
                chat_id=self.current_chat_id,
                question=message,
                conversation_id=conversation_id,
                stream=False
            )
            
            return result
        except Exception as e:
            return {'success': False, 'message': f'發送消息失敗: {e}'}

def show_chat_page():
    """顯示聊天頁面"""
    st.markdown("## 💬 智能聊天")
    st.markdown("與 RAGFlow 知識庫進行智能對話")
    
    # 初始化聊天界面
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = RAGFlowChatInterface()
    
    chat_interface = st.session_state.chat_interface
    
    # 檢查 RAGFlow 可用性
    if not RAGFLOW_AVAILABLE:
        st.error("❌ RAGFlow 客戶端不可用，請檢查配置和安裝")
        st.markdown("""
        ### 配置說明
        1. 確保已安裝 `ragflow_chatbot.py` 模組
        2. 設置環境變數 `RAGFLOW_API_URL` 和 `RAGFLOW_API_KEY`
        3. 確保 RAGFlow 服務正在運行
        """)
        return
    
    # 初始化客戶端按鈕
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 初始化客戶端", use_container_width=True):
            if chat_interface.initialize_client():
                st.success("✅ 客戶端初始化成功")
                st.rerun()
            else:
                st.error("❌ 客戶端初始化失敗")
    
    # 數據集選擇
    if chat_interface.client:
        datasets = chat_interface.get_datasets()
        
        if datasets:
            dataset_options = {f"{ds.get('name', 'Unknown')} ({ds.get('id', 'No ID')})": ds for ds in datasets}
            selected_dataset_key = st.selectbox(
                "📚 選擇知識庫",
                options=list(dataset_options.keys()),
                key="dataset_selector"
            )
            
            if selected_dataset_key:
                selected_dataset = dataset_options[selected_dataset_key]
                st.session_state.current_dataset = selected_dataset
                
                # 顯示數據集信息
                with st.expander("📋 數據集詳情"):
                    st.json(selected_dataset)
                
                # 創建聊天會話
                col1, col2 = st.columns([2, 1])
                with col1:
                    chat_name = st.text_input("聊天會話名稱", value=f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                with col2:
                    if st.button("🚀 開始聊天會話", use_container_width=True):
                        if chat_interface.create_chat_session([selected_dataset.get('id')], chat_name):
                            st.success("✅ 聊天會話已建立")
                            st.rerun()
        else:
            st.warning("⚠️ 沒有可用的數據集")
    else:
        st.warning("⚠️ 請先初始化客戶端")
    
    st.markdown("---")
    
    # 主要聊天區域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 聊天歷史顯示
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                with st.chat_message(chat["role"]):
                    st.markdown(chat["content"])
                    
                    # 如果是機器人回應，顯示來源
                    if chat["role"] == "assistant" and "sources" in chat:
                        with st.expander("📚 參考來源"):
                            for source in chat["sources"]:
                                st.markdown(f"• **{source.get('title', 'Unknown')}**: {source.get('content', '')[:200]}...")
        else:
            st.info("👋 歡迎使用 RAGFlow 智能聊天！請選擇知識庫並開始對話。")
        
        # 聊天輸入區域 (使用 text_input 替代 chat_input)
        st.markdown("---")
        st.markdown("### 💬 發送消息")
        
        col_input, col_send = st.columns([4, 1])
        
        with col_input:
            user_input = st.text_input("輸入問題", placeholder="請輸入您的問題...", key="chat_text_input", label_visibility="collapsed")
        
        with col_send:
            send_button = st.button("📤 發送", use_container_width=True)
        
        if send_button and user_input.strip():
            prompt = user_input.strip()
            
            if not chat_interface.current_chat_id:
                st.error("❌ 請先創建聊天會話")
            else:
                # 添加用戶消息到歷史
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": prompt,
                    "timestamp": datetime.now().isoformat()
                })
                
                # 發送消息並獲取回應
                with st.spinner("🤔 正在思考..."):
                    response = chat_interface.send_message(prompt)
                
                if response.get('success'):
                    response_data = response.get('data', {})
                    answer = response_data.get('answer', '沒有找到合適的回答')
                    sources = response_data.get('reference', [])
                    
                    # 添加機器人回應到歷史
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.chat_history.append(assistant_message)
                    
                    # 保存對話用於評估
                    evaluation_case = {
                        "question": prompt,
                        "answer": answer,
                        "contexts": [src.get('content', '') for src in sources],
                        "dataset_id": st.session_state.current_dataset.get('id') if st.session_state.current_dataset else None,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    if 'chat_for_evaluation' not in st.session_state:
                        st.session_state.chat_for_evaluation = []
                    st.session_state.chat_for_evaluation.append(evaluation_case)
                    
                    # 清空輸入框
                    st.session_state.chat_text_input = ""
                    
                else:
                    st.error(f"❌ 獲取回應失敗: {response.get('message', 'Unknown error')}")
                
                st.rerun()
    
    with col2:
        st.markdown("### 📊 聊天統計")
        
        # 統計信息
        total_messages = len(st.session_state.chat_history)
        user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
        bot_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "assistant"])
        
        st.metric("總消息數", total_messages)
        st.metric("用戶消息", user_messages)
        st.metric("機器人回應", bot_messages)
        
        st.markdown("---")
        
        # 操作按鈕
        st.markdown("### 🛠️ 操作")
        
        if st.button("🗑️ 清空聊天記錄", use_container_width=True):
            st.session_state.chat_history = []
            if 'chat_for_evaluation' in st.session_state:
                st.session_state.chat_for_evaluation = []
            st.success("✅ 聊天記錄已清空")
            st.rerun()
        
        if st.button("💾 導出聊天記錄", use_container_width=True):
            if st.session_state.chat_history:
                chat_data = {
                    "export_time": datetime.now().isoformat(),
                    "total_messages": len(st.session_state.chat_history),
                    "dataset": st.session_state.current_dataset,
                    "messages": st.session_state.chat_history
                }
                
                st.download_button(
                    label="📥 下載 JSON 文件",
                    data=json.dumps(chat_data, ensure_ascii=False, indent=2),
                    file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ 沒有聊天記錄可導出")
        
        if st.button("📏 轉至評估", use_container_width=True):
            if 'chat_for_evaluation' in st.session_state and st.session_state.chat_for_evaluation:
                st.success(f"✅ 已準備 {len(st.session_state.chat_for_evaluation)} 個評估案例")
                st.info("💡 請切換到 'RAGAS 評估' 標籤頁進行評估")
            else:
                st.warning("⚠️ 沒有可用於評估的對話記錄")
        
        st.markdown("---")
        
        # 當前狀態
        st.markdown("### 🔍 當前狀態")
        
        if st.session_state.current_dataset:
            st.success(f"✅ 數據集: {st.session_state.current_dataset.get('name', 'Unknown')}")
        else:
            st.warning("⚠️ 未選擇數據集")
        
        if chat_interface.current_chat_id:
            st.success(f"✅ 會話: {chat_interface.current_chat_id[:8]}...")
        else:
            st.warning("⚠️ 未建立聊天會話")
