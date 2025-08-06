#!/usr/bin/env python3
"""
系統設置頁面模組
配置管理和系統參數設置
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, Any

def load_settings() -> Dict[str, Any]:
    """載入系統設置"""
    default_settings = {
        'ragflow_api_url': os.getenv('RAGFLOW_API_URL', 'http://localhost:8080'),
        'ragflow_api_key': os.getenv('RAGFLOW_API_KEY', ''),
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'evaluation_threshold': 0.7,
        'default_test_cases': 10,
        'auto_evaluation': True,
        'default_metrics': ['faithfulness', 'answer_relevancy'],
        'ui_theme': 'light',
        'language': 'zh-TW'
    }
    
    # 嘗試從文件載入設置
    settings_file = 'data/settings.json'
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                saved_settings = json.load(f)
                default_settings.update(saved_settings)
        except Exception as e:
            st.warning(f"載入設置文件失敗: {e}")
    
    return default_settings

def save_settings(settings: Dict[str, Any]) -> bool:
    """保存系統設置"""
    try:
        os.makedirs('data', exist_ok=True)
        settings_file = 'data/settings.json'
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"保存設置失敗: {e}")
        return False

def test_ragflow_connection(api_url: str, api_key: str) -> Dict[str, Any]:
    """測試 RAGFlow 連接"""
    try:
        from ragflow_chatbot import RAGFlowOfficialClient
        
        # 臨時設置環境變數
        original_url = os.getenv('RAGFLOW_API_URL')
        original_key = os.getenv('RAGFLOW_API_KEY')
        
        os.environ['RAGFLOW_API_URL'] = api_url
        os.environ['RAGFLOW_API_KEY'] = api_key
        
        try:
            client = RAGFlowOfficialClient()
            result = client.list_datasets()
            
            if result.get('success'):
                return {
                    'success': True,
                    'message': '連接成功',
                    'datasets_count': len(result.get('data', []))
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '連接失敗')
                }
        finally:
            # 恢復原始環境變數
            if original_url:
                os.environ['RAGFLOW_API_URL'] = original_url
            if original_key:
                os.environ['RAGFLOW_API_KEY'] = original_key
                
    except ImportError:
        return {
            'success': False,
            'message': 'RAGFlow 客戶端不可用'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'連接測試失敗: {str(e)}'
        }

def show_settings_page():
    """顯示設置頁面"""
    st.markdown("## ⚙️ 系統設置")
    st.markdown("配置 RAGFlow 連接和評估參數")
    
    # 載入當前設置
    settings = load_settings()
    
    # API 連接設置
    st.markdown("### 🔌 API 連接設置")
    
    with st.form("api_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            ragflow_url = st.text_input(
                "RAGFlow API URL",
                value=settings.get('ragflow_api_url', ''),
                help="RAGFlow 服務的 API 地址"
            )
            
            ragflow_key = st.text_input(
                "RAGFlow API Key",
                value=settings.get('ragflow_api_key', ''),
                type="password",
                help="RAGFlow 服務的 API 密鑰"
            )
        
        with col2:
            openai_key = st.text_input(
                "OpenAI API Key (可選)",
                value=settings.get('openai_api_key', ''),
                type="password",
                help="用於 RAGAS 評估的 OpenAI API 密鑰"
            )
            
            # 測試連接按鈕
            test_connection = st.form_submit_button("🔍 測試連接")
            
            if test_connection and ragflow_url and ragflow_key:
                with st.spinner("測試連接中..."):
                    result = test_ragflow_connection(ragflow_url, ragflow_key)
                    
                if result['success']:
                    st.success(f"✅ {result['message']} (找到 {result.get('datasets_count', 0)} 個數據集)")
                else:
                    st.error(f"❌ {result['message']}")
        
        api_submitted = st.form_submit_button("💾 保存 API 設置", type="primary")
        
        if api_submitted:
            # 更新設置
            settings['ragflow_api_url'] = ragflow_url
            settings['ragflow_api_key'] = ragflow_key
            settings['openai_api_key'] = openai_key
            
            # 保存到文件
            if save_settings(settings):
                # 更新環境變數
                os.environ['RAGFLOW_API_URL'] = ragflow_url
                os.environ['RAGFLOW_API_KEY'] = ragflow_key
                if openai_key:
                    os.environ['OPENAI_API_KEY'] = openai_key
                
                st.success("✅ API 設置已保存")
                st.rerun()
    
    st.markdown("---")
    
    # 評估設置
    st.markdown("### 📊 評估設置")
    
    with st.form("evaluation_settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📏 評估參數")
            
            evaluation_threshold = st.slider(
                "評估閾值",
                min_value=0.0,
                max_value=1.0,
                value=settings.get('evaluation_threshold', 0.7),
                step=0.05,
                help="低於此閾值的指標將被標記為需要改進"
            )
            
            default_test_cases = st.number_input(
                "默認測試案例數量",
                min_value=1,
                max_value=100,
                value=settings.get('default_test_cases', 10),
                help="生成測試案例時的默認數量"
            )
            
            auto_evaluation = st.checkbox(
                "啟用自動評估",
                value=settings.get('auto_evaluation', True),
                help="聊天後自動準備評估案例"
            )
        
        with col2:
            st.markdown("#### 📊 默認評估指標")
            
            available_metrics = {
                'faithfulness': '忠實度',
                'answer_relevancy': '答案相關性',
                'context_precision': '上下文精確度',
                'context_recall': '上下文召回率',
                'answer_similarity': '答案相似度',
                'answer_correctness': '答案正確性'
            }
            
            current_default_metrics = settings.get('default_metrics', ['faithfulness', 'answer_relevancy'])
            
            selected_metrics = []
            for metric_key, metric_name in available_metrics.items():
                if st.checkbox(
                    metric_name,
                    value=metric_key in current_default_metrics,
                    key=f"default_metric_{metric_key}"
                ):
                    selected_metrics.append(metric_key)
        
        eval_submitted = st.form_submit_button("💾 保存評估設置", type="primary")
        
        if eval_submitted:
            settings['evaluation_threshold'] = evaluation_threshold
            settings['default_test_cases'] = default_test_cases
            settings['auto_evaluation'] = auto_evaluation
            settings['default_metrics'] = selected_metrics
            
            if save_settings(settings):
                st.success("✅ 評估設置已保存")
                st.rerun()
    
    st.markdown("---")
    
    # 系統信息
    st.markdown("### 📋 系統信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 環境狀態")
        
        # 檢查各個組件狀態
        ragflow_status = "✅ 已配置" if settings.get('ragflow_api_key') else "❌ 未配置"
        st.markdown(f"**RAGFlow API**: {ragflow_status}")
        
        openai_status = "✅ 已配置" if settings.get('openai_api_key') else "⚠️ 未配置"
        st.markdown(f"**OpenAI API**: {openai_status}")
        
        # 檢查依賴
        try:
            import ragas
            ragas_status = f"✅ 已安裝 (v{ragas.__version__})"
        except ImportError:
            ragas_status = "❌ 未安裝"
        st.markdown(f"**RAGAS**: {ragas_status}")
        
        try:
            import plotly
            plotly_status = f"✅ 已安裝 (v{plotly.__version__})"
        except ImportError:
            plotly_status = "❌ 未安裝"
        st.markdown(f"**Plotly**: {plotly_status}")
    
    with col2:
        st.markdown("#### 📊 使用統計")
        
        # 統計信息
        chat_history_count = len(st.session_state.get('chat_history', []))
        evaluation_count = len(st.session_state.get('evaluation_results', []))
        
        st.metric("聊天消息數", chat_history_count)
        st.metric("評估次數", evaluation_count)
        
        if 'current_dataset' in st.session_state and st.session_state.current_dataset:
            st.info(f"**當前數據集**: {st.session_state.current_dataset.get('name', 'Unknown')}")
        else:
            st.warning("**當前數據集**: 未選擇")
    
    st.markdown("---")
    
    # 數據管理
    st.markdown("### 🗂️ 數據管理")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 導出設置", use_container_width=True):
            export_data = {
                'export_time': datetime.now().isoformat(),
                'settings': settings,
                'session_stats': {
                    'chat_history_count': len(st.session_state.get('chat_history', [])),
                    'evaluation_count': len(st.session_state.get('evaluation_results', []))
                }
            }
            
            st.download_button(
                label="💾 下載設置文件",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"ragflow_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 導入設置", type=['json'], key="import_settings")
        if uploaded_file:
            try:
                import_data = json.loads(uploaded_file.read().decode('utf-8'))
                imported_settings = import_data.get('settings', {})
                
                if save_settings(imported_settings):
                    st.success("✅ 設置已導入")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ 導入失敗: {e}")
    
    with col3:
        if st.button("🔄 重置設置", use_container_width=True):
            if st.session_state.get('confirm_reset', False):
                # 刪除設置文件
                settings_file = 'data/settings.json'
                if os.path.exists(settings_file):
                    os.remove(settings_file)
                
                st.success("✅ 設置已重置")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ 再次點擊確認重置所有設置")
    
    st.markdown("---")
    
    # 幫助信息
    with st.expander("❓ 幫助信息"):
        st.markdown("""
        ### 配置說明
        
        #### RAGFlow API 設置
        - **API URL**: RAGFlow 服務的完整地址，如 `http://localhost:8080`
        - **API Key**: 從 RAGFlow 服務獲取的認證密鑰
        
        #### OpenAI API 設置
        - **API Key**: 用於 RAGAS 評估指標計算，可選但建議配置
        - 沒有 OpenAI API Key 時，部分評估功能可能受限
        
        #### 評估參數
        - **評估閾值**: 用於判斷指標是否需要改進的基準線
        - **測試案例數量**: 自動生成測試問題時的默認數量
        - **默認指標**: 執行評估時預選的指標組合
        
        ### 故障排除
        - 如果連接測試失敗，請檢查 RAGFlow 服務是否正在運行
        - 確保 API URL 格式正確，包含 http:// 或 https://
        - API Key 區分大小寫，請確保輸入正確
        """)

# 兼容性函數
def render_settings_page():
    """兼容性函數，調用新的 show_settings_page"""
    show_settings_page()

if __name__ == "__main__":
    show_settings_page()
