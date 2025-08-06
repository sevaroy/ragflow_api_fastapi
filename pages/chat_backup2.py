#!/usr/bin/env python3
"""
改進的聊天頁面模組 - 更簡潔易用的界面
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

# 導入 RAGFlow 客戶端
try:
    from ragflow_chatbot import RAGFlowOfficialClient
    RAGFLOW_AVAILABLE = True
except ImportError:
    RAGFLOW_AVAILABLE = False

def initialize_chat_session():
    """自動初始化聊天會話"""
    if 'chat_client' not in st.session_state:
        if RAGFLOW_AVAILABLE:
            st.session_state.chat_client = RAGFlowOfficialClient()
        else:
            return False
    
    if 'available_datasets' not in st.session_state:
        try:
            result = st.session_state.chat_client.list_datasets()
            if result.get('success'):
                st.session_state.available_datasets = result.get('data', [])
            else:
                st.session_state.available_datasets = []
        except:
            st.session_state.available_datasets = []
    
    return True

def get_or_create_chat_session(dataset_id: str):
    """獲取或創建聊天會話"""
    if 'active_chat_sessions' not in st.session_state:
        st.session_state.active_chat_sessions = {}
    if 'active_sessions' not in st.session_state:
        st.session_state.active_sessions = {}
    
    if dataset_id not in st.session_state.active_chat_sessions:
        try:
            # 1. 創建聊天助手
            chat_name = f"Chat_{datetime.now().strftime('%H%M%S')}"
            chat_result = st.session_state.chat_client.create_chat(
                name=chat_name,
                dataset_ids=[dataset_id]
            )
            
            if chat_result.get('success'):
                chat_id = chat_result.get('data', {}).get('id')
                st.session_state.active_chat_sessions[dataset_id] = chat_id
                
                # 2. 創建會話
                session_result = st.session_state.chat_client.create_session(chat_id)
                if session_result.get('success'):
                    session_id = session_result.get('data', {}).get('id')
                    st.session_state.active_sessions[dataset_id] = session_id
                    return {'chat_id': chat_id, 'session_id': session_id}
        except Exception as e:
            st.error(f"創建會話失敗: {e}")
            return None
    
    chat_id = st.session_state.active_chat_sessions.get(dataset_id)
    session_id = st.session_state.active_sessions.get(dataset_id)
    
    if chat_id and session_id:
        return {'chat_id': chat_id, 'session_id': session_id}
    
    return None

def send_message(chat_id: str, session_id: str, message: str):
    """發送消息"""
    try:
        result = st.session_state.chat_client.chat_completion(
            chat_id=chat_id,
            session_id=session_id,
            question=message,
            quote=True,
            stream=False
        )
        return result
    except Exception as e:
        return {'success': False, 'message': f'發送失敗: {e}'}

def show_improved_chat_page():
    """顯示改進的聊天頁面"""
    
    # 檢查可用性
    if not RAGFLOW_AVAILABLE:
        st.error("❌ RAGFlow 客戶端不可用")
        return
    
    # 自動初始化
    if not initialize_chat_session():
        st.error("❌ 無法初始化聊天客戶端")
        return
    
    # 頁面標題
    st.markdown("## 💬 智能聊天")
    
    # 簡化的數據集選擇
    if not st.session_state.available_datasets:
        st.warning("⚠️ 沒有可用的知識庫")
        return
    
    # 數據集選擇器 - 簡潔版本
    col1, col2 = st.columns([3, 1])
    with col1:
        dataset_options = {ds.get('name', f"Dataset_{ds.get('id', '')[:8]}"): ds.get('id') 
                          for ds in st.session_state.available_datasets}
        selected_dataset_name = st.selectbox("🗂️ 選擇知識庫", list(dataset_options.keys()))
        selected_dataset_id = dataset_options[selected_dataset_name]
    
    with col2:
        # 顯示數據集狀態  
        if (selected_dataset_id in st.session_state.get('active_chat_sessions', {}) and 
            selected_dataset_id in st.session_state.get('active_sessions', {})):
            st.success("🟢 已連接")
        else:
            st.info("🔵 準備就緒")
    
    # 聊天容器 - 固定高度
    chat_container = st.container()
    with chat_container:
        # 聊天歷史
        chat_key = f"chat_history_{selected_dataset_id}"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
        
        # 顯示聊天記錄
        if st.session_state[chat_key]:
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and msg.get("sources"):
                        with st.expander("📚 參考來源", expanded=False):
                            for i, source in enumerate(msg["sources"][:3]):  # 限制顯示前3個來源
                                st.caption(f"{i+1}. {source.get('content', '')[:150]}...")
        else:
            st.info(f"🤖 您好！我是 {selected_dataset_name} 的智能助手，有什麼可以幫助您的嗎？")
    
    # 聊天輸入 - 放在底部
    st.markdown("---")
    
    # 使用表單來支持 Enter 鍵提交
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_message = st.text_input(
                "💭",
                placeholder="輸入您的問題，按 Enter 發送...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit = st.form_submit_button("📤", use_container_width=True)
    
    # 處理消息發送
    if submit and user_message.strip():
        message = user_message.strip()
        
        # 獲取或創建聊天會話
        session_info = get_or_create_chat_session(selected_dataset_id)
        
        if not session_info:
            st.error("❌ 無法創建聊天會話")
            return
        
        chat_id = session_info['chat_id']
        session_id = session_info['session_id']
        
        # 添加用戶消息
        st.session_state[chat_key].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 發送消息並獲取回應
        with st.spinner("🤔 思考中..."):
            response = send_message(chat_id, session_id, message)
        
        if response.get('success'):
            response_data = response.get('data', {})
            answer = response_data.get('answer', '抱歉，我無法回答這個問題。')
            sources = response_data.get('reference', [])
            
            # 添加助手回應
            st.session_state[chat_key].append({
                "role": "assistant", 
                "content": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            })
            
            # 保存評估案例
            if 'chat_for_evaluation' not in st.session_state:
                st.session_state.chat_for_evaluation = []
            
            st.session_state.chat_for_evaluation.append({
                "question": message,
                "answer": answer,
                "contexts": [src.get('content', '') for src in sources],
                "dataset_id": selected_dataset_id,
                "dataset_name": selected_dataset_name,
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            st.error(f"❌ 發送失敗: {response.get('message', '未知錯誤')}")
        
        st.rerun()
    
    # 側邊欄工具
    with st.sidebar:
        st.markdown("### 🛠️ 聊天工具")
        
        # 統計信息
        total_messages = len(st.session_state.get(chat_key, []))
        if total_messages > 0:
            st.metric("對話輪數", total_messages // 2)
            st.metric("評估案例", len(st.session_state.get('chat_for_evaluation', [])))
        
        st.markdown("---")
        
        # 操作按鈕
        if st.button("🗑️ 清空對話", use_container_width=True):
            if chat_key in st.session_state:
                st.session_state[chat_key] = []
            st.rerun()
        
        if st.button("📥 導出對話", use_container_width=True):
            if chat_key in st.session_state and st.session_state[chat_key]:
                export_data = {
                    "dataset": selected_dataset_name,
                    "export_time": datetime.now().isoformat(),
                    "messages": st.session_state[chat_key]
                }
                
                st.download_button(
                    "💾 下載 JSON",
                    data=json.dumps(export_data, ensure_ascii=False, indent=2),
                    file_name=f"chat_{selected_dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        if st.button("📊 轉至評估", use_container_width=True):
            evaluation_count = len(st.session_state.get('chat_for_evaluation', []))
            if evaluation_count > 0:
                st.success(f"✅ 已準備 {evaluation_count} 個評估案例")
                st.info("💡 請切換到 RAGAS 評估標籤頁")
            else:
                st.warning("⚠️ 沒有可用的評估案例")

# 主函數入口
def show_chat_page():
    """主聊天頁面入口"""
    show_improved_chat_page()

if __name__ == "__main__":
    show_improved_chat_page()