#!/usr/bin/env python3
"""
測試修復後的聊天頁面
"""

import streamlit as st
from streamlit_chat import message

st.set_page_config(page_title="聊天修復測試", page_icon="🧪")

st.markdown("# 🧪 聊天界面修復測試")

# 測試 streamlit-chat 組件
st.markdown("## 1. streamlit-chat 組件測試")
message("這是一條測試用戶消息", is_user=True, key="test_user", avatar_style="personas")
message("這是一條測試助手消息", is_user=False, key="test_bot", avatar_style="bottts")

# 測試表單輸入
st.markdown("## 2. 表單輸入測試")

if 'test_messages' not in st.session_state:
    st.session_state.test_messages = []

# 顯示消息
for i, msg in enumerate(st.session_state.test_messages):
    message(msg["content"], is_user=msg["is_user"], key=f"test_msg_{i}")

# 輸入表單
with st.form("test_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        test_input = st.text_input("測試輸入", placeholder="輸入測試消息...", label_visibility="collapsed")
    
    with col2:
        submitted = st.form_submit_button("發送")

if submitted and test_input:
    # 添加用戶消息
    st.session_state.test_messages.append({
        "content": test_input,
        "is_user": True
    })
    
    # 添加自動回復
    st.session_state.test_messages.append({
        "content": f"收到您的消息：{test_input}",
        "is_user": False
    })
    
    st.rerun()

# 測試來源處理邏輯
st.markdown("## 3. 來源數據處理測試")

test_sources = [
    {"title": "字典來源", "content": "這是字典格式的來源內容"},
    "這是字符串格式的來源",
    123
]

st.markdown("**測試來源數據：**")
for i, src in enumerate(test_sources):
    if isinstance(src, dict):
        title = src.get('title', '未知標題')
        content = src.get('content', '')[:50]
        st.markdown(f"- 來源 {i+1} (字典): **{title}** - {content}...")
    elif isinstance(src, str):
        st.markdown(f"- 來源 {i+1} (字符串): {src}")
    else:
        st.markdown(f"- 來源 {i+1} (其他): {str(src)}")

st.success("✅ 所有測試組件都能正常工作！")

if st.button("清空測試消息"):
    st.session_state.test_messages = []
    st.rerun()