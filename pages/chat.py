#!/usr/bin/env python3
"""
使用 streamlit-chat 組件的聊天頁面
提供更專業的聊天體驗
"""

import streamlit as st
from streamlit_chat import message
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
        except Exception:
            return None
    
    chat_id = st.session_state.active_chat_sessions.get(dataset_id)
    session_id = st.session_state.active_sessions.get(dataset_id)
    
    if chat_id and session_id:
        return {'chat_id': chat_id, 'session_id': session_id}
    
    return None

def send_message_to_ragflow(chat_id: str, session_id: str, message: str):
    """發送消息到 RAGFlow"""
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

def display_message_with_sources(msg_data: Dict, key: str):
    """顯示帶來源的消息"""
    is_user = msg_data["role"] == "user"
    
    # 使用 streamlit-chat 組件顯示消息
    message(
        msg_data["content"], 
        is_user=is_user,
        key=key,
        avatar_style="thumbs" if not is_user else "personas"
    )
    
    # 如果是助手回應且有來源，顯示來源信息
    if not is_user and msg_data.get("sources"):
        with st.expander("📚 參考來源", expanded=False):
            for i, source in enumerate(msg_data["sources"][:3]):
                if isinstance(source, dict):
                    title = source.get('title', '未知標題')
                    content = source.get('content', '')[:200]
                elif isinstance(source, str):
                    title = f"來源 {i+1}"
                    content = source[:200]
                else:
                    title = f"來源 {i+1}"
                    content = str(source)[:200]
                
                st.markdown(f"""
                **{title}:**
                - {content}...
                """)

def show_st_chat_page():
    """顯示使用 streamlit-chat 的聊天頁面"""
    
    # 檢查可用性
    if not RAGFLOW_AVAILABLE:
        st.error("❌ RAGFlow 客戶端不可用")
        st.info("請確保 ragflow_chatbot.py 已正確配置")
        return
    
    # 自動初始化
    if not initialize_chat_session():
        st.error("❌ 無法初始化聊天客戶端")
        return
    
    # 頁面標題
    st.markdown("""
    ## 💬 智能聊天 (Pro版)
    *powered by streamlit-chat*
    """)
    
    # 簡化的數據集選擇
    if not st.session_state.available_datasets:
        st.warning("⚠️ 沒有可用的知識庫")
        return
    
    # 頂部控制面板
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            dataset_options = {}
            for ds in st.session_state.available_datasets:
                dataset_id = ds.get('id', '')
                dataset_name = ds.get('name', f"Dataset_{dataset_id[:8] if dataset_id else 'Unknown'}")
                dataset_options[dataset_name] = dataset_id
            selected_dataset_name = st.selectbox(
                "🗂️ 選擇知識庫", 
                list(dataset_options.keys()),
                key="dataset_selector"
            )
            selected_dataset_id = dataset_options[selected_dataset_name]
        
        with col2:
            # 連接狀態
            is_connected = (selected_dataset_id in st.session_state.get('active_chat_sessions', {}) and 
                          selected_dataset_id in st.session_state.get('active_sessions', {}))
            
            if is_connected:
                st.success("🟢 已連接")
            else:
                st.info("🔵 就緒")
        
        with col3:
            # 清空對話按鈕
            if st.button("🗑️ 清空對話", use_container_width=True):
                chat_key = f"st_chat_history_{selected_dataset_id}"
                if chat_key in st.session_state:
                    st.session_state[chat_key] = []
                st.rerun()
    
    st.markdown("---")
    
    # 聊天歷史容器
    chat_key = f"st_chat_history_{selected_dataset_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # 聊天區域
    chat_container = st.container()
    
    with chat_container:
        # 歡迎消息
        if not st.session_state[chat_key]:
            message(
                f"🤖 您好！我是 **{selected_dataset_name}** 的智能助手。\n\n我可以幫您解答相關問題，請在下方輸入您的問題。",
                is_user=False,
                key=f"welcome_{selected_dataset_id}",
                avatar_style="bottts"
            )
        
        # 顯示聊天歷史
        for i, msg in enumerate(st.session_state[chat_key]):
            display_message_with_sources(
                msg, 
                f"{chat_key}_msg_{i}"
            )
    
    # 輸入區域 - 使用 form 自動清空
    st.markdown("---")
    
    # 使用 form 來處理輸入，支持自動清空
    with st.form("chat_input_form", clear_on_submit=True):
        input_col, send_col = st.columns([5, 1])
        
        with input_col:
            user_input = st.text_input(
                "輸入消息",
                placeholder="請輸入您的問題...",
                label_visibility="collapsed",
                key="form_chat_input"
            )
        
        with send_col:
            send_clicked = st.form_submit_button("📤", use_container_width=True)
    
    # 處理發送
    if send_clicked and user_input and user_input.strip():
        message_text = user_input.strip()
        
        # 獲取或創建聊天會話
        session_info = get_or_create_chat_session(selected_dataset_id)
        
        if not session_info:
            st.error("❌ 無法創建聊天會話")
            return
        
        chat_id = session_info['chat_id']
        session_id = session_info['session_id']
        
        # 添加用戶消息
        user_msg = {
            "role": "user",
            "content": message_text,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state[chat_key].append(user_msg)
        
        # 發送到 RAGFlow 並獲取回應
        with st.spinner("🤔 AI 正在思考..."):
            response = send_message_to_ragflow(chat_id, session_id, message_text)
        
        if response.get('success'):
            response_data = response.get('data', {})
            answer = response_data.get('answer', '抱歉，我無法回答這個問題。')
            sources = response_data.get('reference', [])
            
            # 調試信息 (可選，在生產環境中移除)
            # st.write(f"DEBUG - Sources type: {type(sources)}, Length: {len(sources) if sources else 0}")
            
            # 添加助手回應
            assistant_msg = {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state[chat_key].append(assistant_msg)
            
            # 保存評估案例
            if 'chat_for_evaluation' not in st.session_state:
                st.session_state.chat_for_evaluation = []
            
            # 處理來源數據，確保格式正確
            contexts = []
            for src in sources:
                if isinstance(src, dict):
                    contexts.append(src.get('content', ''))
                elif isinstance(src, str):
                    contexts.append(src)
                else:
                    contexts.append(str(src))
            
            st.session_state.chat_for_evaluation.append({
                "question": message_text,
                "answer": answer,
                "contexts": contexts,
                "dataset_id": selected_dataset_id,
                "dataset_name": selected_dataset_name,
                "timestamp": datetime.now().isoformat()
            })
            
        else:
            # 錯誤消息
            error_msg = {
                "role": "assistant",
                "content": f"❌ 抱歉，處理您的請求時出現錯誤：{response.get('message', '未知錯誤')}",
                "timestamp": datetime.now().isoformat()
            }
            st.session_state[chat_key].append(error_msg)
        
        # 重新運行以更新界面
        st.rerun()
    
    # 側邊欄統計和工具
    with st.sidebar:
        st.markdown("### 📊 對話統計")
        
        total_messages = len(st.session_state.get(chat_key, []))
        conversation_rounds = total_messages // 2
        evaluation_cases = len(st.session_state.get('chat_for_evaluation', []))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("對話輪數", conversation_rounds)
        with col2:
            st.metric("評估案例", evaluation_cases)
        
        st.markdown("---")
        
        # 功能按鈕
        st.markdown("### 🛠️ 工具")
        
        if st.button("📥 導出對話", use_container_width=True):
            if st.session_state.get(chat_key):
                export_data = {
                    "dataset": selected_dataset_name,
                    "export_time": datetime.now().isoformat(),
                    "conversation_rounds": conversation_rounds,
                    "messages": st.session_state[chat_key]
                }
                
                st.download_button(
                    "💾 下載對話記錄",
                    data=json.dumps(export_data, ensure_ascii=False, indent=2),
                    file_name=f"chat_{selected_dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("沒有對話記錄可導出")
        
        if evaluation_cases > 0:
            if st.button("🔬 前往 RAGAS 評估", use_container_width=True):
                st.success(f"✅ 已準備 {evaluation_cases} 個評估案例")
                st.info("💡 切換到 'RAGAS 評估' 標籤頁開始評估")
        
        # 使用說明
        with st.expander("❓ 使用說明"):
            st.markdown("""
            **聊天功能：**
            1. 選擇知識庫
            2. 輸入問題並按Enter或點擊發送
            3. 查看AI回應和參考來源
            
            **特色功能：**
            - 🎨 專業聊天UI（streamlit-chat）
            - 📚 智能來源引用
            - 📊 實時統計
            - 🔬 自動準備RAGAS評估案例
            - 📥 對話記錄導出
            """)

# 主函數入口  
def show_chat_page():
    """主聊天頁面入口"""
    show_st_chat_page()

if __name__ == "__main__":
    show_st_chat_page()