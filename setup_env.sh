#!/bin/bash
echo "🐍 設置 Python 虛擬環境..."

# 檢查是否已存在虛擬環境
if [ -d "venv" ]; then
    echo "✅ 虛擬環境已存在"
else
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "🚀 啟動虛擬環境..."
source venv/bin/activate

# 升級 pip
echo "⬆️  升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo "📚 安裝依賴..."
pip install -r requirements.txt

# 檢查配置
echo "🔍 檢查配置..."
python3 check_config.py

echo "🎉 環境設置完成！"
echo ""
echo "🚀 現在你可以運行："
echo "  python3 test/deepeval_demo.py"
echo "  python3 test/run_deepeval_test.py"
echo "  python3 deepeval_integration.py"
echo ""
echo "💡 記住要先啟動虛擬環境："
echo "  source venv/bin/activate"