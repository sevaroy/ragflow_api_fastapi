"""
結果分析頁面
"""
import streamlit as st
import json
import glob


def render_results_page():
    """結果分析頁面"""
    st.markdown("## 📈 結果分析")
    
    # 載入可用的評估結果
    available_results = load_available_results()
    
    if not available_results:
        render_no_results_message()
        return
    
    # 控制面板
    from components.results import render_results_control_panel
    render_results_control_panel(available_results)
    
    # 如果有選中的結果，顯示分析
    if hasattr(st.session_state, 'selected_result_data'):
        from components.results import render_results_dashboard
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
