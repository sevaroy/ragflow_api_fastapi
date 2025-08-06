"""
首頁儀表板頁面
"""
import streamlit as st


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
