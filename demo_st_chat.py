#!/usr/bin/env python3
"""
streamlit-chat 組件演示
展示新聊天界面的功能特色
"""

import streamlit as st
from streamlit_chat import message

# 設置頁面
st.set_page_config(
    page_title="ST-Chat 演示",
    page_icon="💬",
    layout="wide"
)

st.markdown("# 🎨 streamlit-chat 組件演示")
st.markdown("展示新聊天界面的專業功能")

# 演示不同的消息樣式
st.markdown("## 📱 消息樣式展示")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 用戶消息")
    message("你好！我想了解一下作文寫作技巧", is_user=True, key="demo_user1", avatar_style="personas")
    
    st.markdown("### 助手消息")
    message("您好！我很樂意為您介紹作文寫作技巧。寫好作文的關鍵包括：\n\n1. 明確主題和立意\n2. 合理安排結構\n3. 使用生動的語言\n4. 注意邏輯連貫性", 
            is_user=False, key="demo_bot1", avatar_style="bottts")

with col2:
    st.markdown("### 不同頭像樣式")
    
    # 展示不同的頭像樣式
    avatar_styles = ["bottts", "avataaars", "initials", "thumbs", "personas", "gridy"]
    
    for i, style in enumerate(avatar_styles):
        message(f"頭像樣式: {style}", 
                is_user=False, 
                key=f"demo_avatar_{i}", 
                avatar_style=style)

st.markdown("---")

# 互動演示
st.markdown("## 🔄 互動演示")

if 'demo_messages' not in st.session_state:
    st.session_state.demo_messages = [
        {"role": "assistant", "content": "歡迎使用新的聊天界面！我是您的智能助手。"},
        {"role": "user", "content": "這個界面看起來很棒！"},
        {"role": "assistant", "content": "謝謝！這是使用 streamlit-chat 組件打造的專業聊天界面，具有以下特色：\n\n✨ 美觀的消息氣泡\n🤖 多樣化的頭像樣式\n📱 類似手機聊天的體驗\n🎨 更好的視覺效果"}
    ]

# 顯示聊天歷史
for i, msg in enumerate(st.session_state.demo_messages):
    message(
        msg["content"],
        is_user=(msg["role"] == "user"),
        key=f"demo_msg_{i}",
        avatar_style="personas" if msg["role"] == "user" else "bottts"
    )

# 輸入新消息
with st.form("demo_form"):
    user_input = st.text_input("輸入消息:", placeholder="試試看發送一條消息...")
    submitted = st.form_submit_button("📤 發送")
    
    if submitted and user_input:
        # 添加用戶消息
        st.session_state.demo_messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # 添加機器人回應
        st.session_state.demo_messages.append({
            "role": "assistant",
            "content": f"我收到了您的消息：「{user_input}」\n\n這就是新聊天界面的效果！比原來的更美觀、更專業。🎉"
        })
        
        st.rerun()

st.markdown("---")

# 特色功能說明
st.markdown("## 🌟 新聊天界面特色")

feature_cols = st.columns(3)

with feature_cols[0]:
    st.markdown("""
    ### 🎨 視覺升級
    - 專業的聊天氣泡設計
    - 美觀的頭像系統
    - 更好的視覺層次
    - 類似現代聊天應用
    """)

with feature_cols[1]:
    st.markdown("""
    ### 🚀 功能增強
    - 多種頭像樣式選擇
    - 更好的消息排版
    - 智能來源引用顯示
    - 實時統計和工具
    """)

with feature_cols[2]:
    st.markdown("""
    ### 💡 用戶體驗
    - 直觀的操作界面
    - 快速響應交互
    - 完整的對話管理
    - 無縫的工作流程
    """)

st.markdown("---")
st.markdown("### 🎯 準備好體驗新的聊天界面了嗎？")
st.markdown("**刷新主應用並前往 '💬 智能聊天 (Pro版)' 標籤頁！**")

if __name__ == "__main__":
    pass