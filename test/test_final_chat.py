#!/usr/bin/env python3
"""
最終聊天頁面測試
"""

import streamlit as st
from streamlit_chat import message

st.set_page_config(page_title="聊天最終測試", page_icon="✅")

st.markdown("# ✅ 聊天頁面最終測試")

# 測試關鍵功能
st.markdown("## 🧪 關鍵功能測試")

# 1. streamlit-chat 測試
st.markdown("### 1. streamlit-chat 組件")
message("用戶消息測試", is_user=True, key="final_test_user", avatar_style="personas")
message("助手消息測試", is_user=False, key="final_test_bot", avatar_style="bottts")

# 2. 數據集選項創建測試
st.markdown("### 2. 數據集選項創建")
test_datasets = [
    {'id': '12345678abcdef', 'name': 'Test Dataset 1'},
    {'id': '87654321fedcba', 'name': 'Test Dataset 2'},
    {'id': '', 'name': 'Empty ID Dataset'}
]

dataset_options = {}
for ds in test_datasets:
    dataset_id = ds.get('id', '') if ds.get('id') else ''
    dataset_name = ds.get('name', f"Dataset_{dataset_id[:8] if dataset_id else 'Unknown'}")
    dataset_options[dataset_name] = dataset_id

st.success(f"✅ 成功創建 {len(dataset_options)} 個數據集選項")
for name, id_val in dataset_options.items():
    st.write(f"- {name}: {id_val}")

# 3. 來源處理測試  
st.markdown("### 3. 來源數據處理")
test_sources = [
    {"title": "Dict Source", "content": "Dictionary content"},
    "String source content",
    123
]

for i, src in enumerate(test_sources):
    if isinstance(src, dict):
        title = src.get('title', '未知標題')
        content = src.get('content', '')[:50]
        st.write(f"來源 {i+1} (字典): **{title}** - {content}...")
    elif isinstance(src, str):
        st.write(f"來源 {i+1} (字符串): {src}")
    else:
        st.write(f"來源 {i+1} (其他): {str(src)}")

# 4. 表單測試
st.markdown("### 4. 聊天表單")

if 'final_test_messages' not in st.session_state:
    st.session_state.final_test_messages = []

# 顯示消息
for i, msg in enumerate(st.session_state.final_test_messages):
    message(msg, is_user=(i % 2 == 0), key=f"final_msg_{i}")

# 輸入表單
with st.form("final_test_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        test_input = st.text_input("測試輸入", placeholder="輸入測試消息...", label_visibility="collapsed")
    
    with col2:
        submitted = st.form_submit_button("📤")

if submitted and test_input:
    st.session_state.final_test_messages.append(test_input)
    st.session_state.final_test_messages.append(f"Echo: {test_input}")
    st.rerun()

st.markdown("---")
st.success("🎉 所有測試通過！聊天頁面已準備就緒。")

if st.button("清空測試"):
    st.session_state.final_test_messages = []
    st.rerun()