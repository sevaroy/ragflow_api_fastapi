#!/usr/bin/env python3
"""
RAGFlow 整合平台頁面模組
包含聊天、評估、儀表板和設置功能
"""

__version__ = "1.0.0"
__author__ = "RAGFlow Team"

# 導入所有頁面模組
from . import chat
from . import evaluation
from . import dashboard
from . import settings

__all__ = [
    'chat',
    'evaluation', 
    'dashboard',
    'settings'
]