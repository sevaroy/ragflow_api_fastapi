#!/bin/bash

# RAGFlow API 測試啟動腳本

echo "🚀 準備運行 RAGFlow API 測試..."

# 檢查虛擬環境是否存在
if [ ! -d "venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 激活虛擬環境並安裝依賴
echo "📥 安裝依賴..."
source venv/bin/activate
pip install -q requests

echo "🔧 選擇測試腳本:"
echo "1) 簡單測試 (ragflow_test.py)"
echo "2) 完整客戶端 (ragflow_client.py)"
echo -n "請選擇 [1-2]: "

read choice

case $choice in
    1)
        echo "🏃 運行簡單測試..."
        python3 ragflow_test.py
        ;;
    2)
        echo "🏃 運行完整客戶端..."
        python3 ragflow_client.py
        ;;
    *)
        echo "❌ 無效選擇，運行簡單測試..."
        python3 ragflow_test.py
        ;;
esac

echo "✅ 測試完成！"