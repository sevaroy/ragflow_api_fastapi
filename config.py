"""
RAGFlow API 配置文件
包含 RAGFlow 和 DeepEval (OpenAI) 的配置
"""

import os

# RAGFlow API 配置
RAGFLOW_API_URL = os.getenv('RAGFLOW_API_URL', 'http://192.168.50.123')
RAGFLOW_API_KEY = os.getenv('RAGFLOW_API_KEY', 'ragflow-Y2YWUxOTY4MDIwNzExZjBhMTgzMDI0Mm')

# DeepEval / OpenAI API 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # 從環境變數讀取
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')  # 預設評估模型

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

# DeepEval 評估設定
DEEPEVAL_CONFIG = {
    'default_question_count': 10,
    'max_question_count': 50,
    'metric_thresholds': {
        'answer_relevancy': 0.7,
        'faithfulness': 0.7,
        'contextual_precision': 0.7,
        'contextual_recall': 0.7,
        'hallucination': 0.3,  # 越低越好
        'bias': 0.5
    }
}