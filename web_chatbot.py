#!/usr/bin/env python3
"""
RAGFlow Web 聊天機器人
基於 Flask 的 Web 界面聊天機器人
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import json
import uuid
from config import RAGFLOW_API_URL, RAGFLOW_API_KEY

app = Flask(__name__)
app.secret_key = 'ragflow-chatbot-secret-key'

class WebRAGChatbot:
    def __init__(self):
        self.api_url = RAGFLOW_API_URL.rstrip('/')
        self.api_key = RAGFLOW_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_knowledge_bases(self):
        """獲取知識庫列表"""
        try:
            response = requests.get(
                f'{self.api_url}/api/v1/datasets',
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            return []
        except:
            return []
    
    def create_chat_session(self, kb_id: str):
        """創建聊天會話"""
        import uuid
        
        chat_data = {
            'name': f'Web聊天機器人_{uuid.uuid4().hex[:8]}',
            'dataset_ids': [kb_id]
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/api/v1/chats',
                headers=self.headers,
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result['data']['id']
            return None
        except:
            return None
    
    def create_session(self, chat_id: str):
        """創建會話"""
        try:
            response = requests.post(
                f'{self.api_url}/api/v1/chats/{chat_id}/sessions',
                headers=self.headers,
                json={},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return result['data']['id']
            return None
        except:
            return None
    
    def chat(self, question: str, kb_id: str):
        """發送聊天請求"""
        # 創建聊天助手
        chat_id = self.create_chat_session(kb_id)
        if not chat_id:
            return {
                'success': False,
                'error': '無法創建聊天助手'
            }
        
        # 創建會話
        session_id = self.create_session(chat_id)
        if not session_id:
            return {
                'success': False,
                'error': '無法創建會話'
            }
        
        # 發送消息
        completion_data = {
            'question': question,
            'quote': True,
            'stream': False,
            'session_id': session_id
        }
        
        try:
            response = requests.post(
                f'{self.api_url}/api/v1/chats/{chat_id}/completions',
                headers=self.headers,
                json=completion_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    data = result['data']
                    return {
                        'success': True,
                        'answer': data.get('answer', ''),
                        'sources': data.get('reference', [])
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('message', '未知錯誤')
                    }
            else:
                return {
                    'success': False,
                    'error': f'API 錯誤: {response.status_code}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'請求失敗: {str(e)}'
            }

# 創建聊天機器人實例
chatbot = WebRAGChatbot()

@app.route('/')
def index():
    """主頁面"""
    knowledge_bases = chatbot.get_knowledge_bases()
    return render_template('index.html', knowledge_bases=knowledge_bases)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """聊天 API 端點"""
    data = request.get_json()
    question = data.get('question', '').strip()
    kb_id = data.get('kb_id', '')
    
    if not question:
        return jsonify({
            'success': False,
            'error': '問題不能為空'
        })
    
    if not kb_id:
        return jsonify({
            'success': False,
            'error': '請選擇知識庫'
        })
    
    # 發送聊天請求
    result = chatbot.chat(question, kb_id)
    
    # 保存到會話歷史
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({
        'id': str(uuid.uuid4()),
        'question': question,
        'answer': result.get('answer', ''),
        'success': result['success'],
        'sources': result.get('sources', []),
        'kb_id': kb_id
    })
    
    return jsonify(result)

@app.route('/api/history')
def api_history():
    """獲取聊天歷史"""
    return jsonify({
        'history': session.get('chat_history', [])
    })

@app.route('/api/clear_history', methods=['POST'])
def api_clear_history():
    """清除聊天歷史"""
    session['chat_history'] = []
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🌐 啟動 RAGFlow Web 聊天機器人...")
    print(f"📡 API URL: {RAGFLOW_API_URL}")
    print("🔗 訪問: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)