"""
導航組件
"""
import streamlit as st
from typing import Dict, Tuple


def render_top_navbar() -> None:
    """渲染頂部導航條"""
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <h2 style='margin: 0; text-align: center;'>🤖 RAGFlow 智能評估平台</h2>
        <p style='text-align: center; margin: 0.5rem 0 0 0; color: #666;'>企業級 RAG 系統效能評估與優化平台</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_navigation() -> None:
    """渲染側邊欄導航"""
    with st.sidebar:
        st.markdown("## 🧭 導航")
        
        # 頁面選擇
        page_options: Dict[str, str] = {
            'home': '🏠 首頁',
            'chat': '💬 聊天',
            'evaluation': '📊 評估',
            'results': '📈 結果',
            'settings': '⚙️ 設置'
        }
        
        # 使用圖標按鈕
        cols: Tuple[st.delta_generator.DeltaGenerator, ...] = st.columns(len(page_options))
        page_item: Tuple[str, str]
        for i, page_item in enumerate(page_options.items()):
            page_key, page_label = page_item
            with cols[i]:
                if st.button(page_label, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
        
        st.divider()
        
        # 顯示當前頁面
        current_page_label: str = page_options.get(st.session_state.current_page, '🏠 首頁')
        st.info(f"📍 當前頁面: {current_page_label}")


def render_system_status_sidebar() -> None:
    """系統狀態側邊欄"""
    with st.sidebar:
        st.markdown("## 🔧 系統狀態")
        
        # API 連接狀態
        if st.session_state.api_connected:
            st.success("✅ API 已連接")
        else:
            st.error("❌ API 未連接")
            if st.button("🔄 重新連接"):
                # 嘗試重新連接
                health_result = st.session_state.client.check_api_health()
                if health_result['success']:
                    st.session_state.api_connected = True
                    st.success("✅ 連接成功！")
                    st.rerun()
                else:
                    st.error(f"❌ 連接失敗: {health_result['error']}")
        
        # 用戶信息
        st.markdown("### 👤 用戶信息")
        st.write(f"用戶 ID: {st.session_state.user_id}")
        st.write(f"會話 ID: {st.session_state.current_session_id}")
        
        # 系統信息
        st.markdown("### 🖥️ 系統信息")
        st.write(f"API 地址: {st.session_state.client.api_url}")
        
        # 快速操作
        st.divider()
        st.markdown("### ⚡ 快速操作")
        if st.button("🧹 清空聊天歷史"):
            st.session_state.chat_history = []
            st.success("✅ 聊天歷史已清空")
        
        if st.button("📊 重新載入結果"):
            st.success("✅ 結果數據已刷新")
            st.rerun()
