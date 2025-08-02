"""
RAGFlow API 配置文件
"""

import os

# RAGFlow API 配置
RAGFLOW_API_URL = os.getenv('RAGFLOW_API_URL', 'http://192.168.50.123')
RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY', 'ragflow-Y2YWUxOTY4MDIwNzExZjBhMTgzMDI0Mm')

# API 端點
ENDPOINTS = {
    'health': '/api/v1/health',
    'datasets': '/api/v1/datasets',
    'documents': '/api/v1/documents',
    'chat': '/api/v1/chat'
}

# 請求設定
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3