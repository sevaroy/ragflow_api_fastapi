# OpenAI API Key 配置指南

## 🔑 OpenAI API Key 配置方式

### 方式 1: 環境變數 (推薦)

#### macOS/Linux
```bash
# 臨時設置 (當前終端會話有效)
export OPENAI_API_KEY="your-openai-api-key-here"
export OPENAI_MODEL="gpt-3.5-turbo"  # 可選，預設就是這個

# 永久設置 - 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

#### Windows
```cmd
# 臨時設置
set OPENAI_API_KEY=your-openai-api-key-here
set OPENAI_MODEL=gpt-3.5-turbo

# 永久設置 (PowerShell)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-openai-api-key-here", "User")
```

### 方式 2: .env 文件

創建 `.env` 文件在項目根目錄：
```bash
# .env 文件內容
RAGFLOW_API_URL=http://192.168.50.123
RAGFLOW_API_KEY=ragflow-Y2YWUxOTY4MDIwNzExZjBhMTgzMDI0Mm
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

然後安裝 python-dotenv：
```bash
pip install python-dotenv
```

### 方式 3: 直接修改 config.py (不推薦)

⚠️ **注意**: 這種方式會將 API Key 暴露在代碼中，不安全！

```python
# 在 config.py 中直接設置 (僅用於測試)
OPENAI_API_KEY = "your-openai-api-key-here"  # 不推薦！
```

## 🎯 推薦配置流程

### 步驟 1: 獲取 OpenAI API Key
1. 訪問 [OpenAI Platform](https://platform.openai.com/)
2. 登入或註冊帳號
3. 前往 [API Keys 頁面](https://platform.openai.com/api-keys)
4. 點擊 "Create new secret key"
5. 複製生成的 API Key

### 步驟 2: 設置環境變數
```bash
# 設置 API Key
export OPENAI_API_KEY="sk-your-actual-api-key-here"

# 驗證設置
echo $OPENAI_API_KEY
```

### 步驟 3: 測試配置
```bash
# 檢查配置狀態
python3 deepeval_config.py

# 運行快速測試
python3 test/deepeval_demo.py
```

## 🔧 配置驗證

### 檢查配置腳本
```python
#!/usr/bin/env python3
"""檢查 OpenAI API 配置"""

import os
from config import OPENAI_API_KEY, OPENAI_MODEL

def check_openai_config():
    print("🔍 檢查 OpenAI API 配置...")
    
    if OPENAI_API_KEY:
        # 隱藏大部分 key 內容，只顯示前後幾位
        masked_key = f"{OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}"
        print(f"✅ OpenAI API Key: {masked_key}")
        print(f"✅ OpenAI Model: {OPENAI_MODEL}")
        
        # 測試 API 連接
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            # 簡單的 API 測試
            response = openai.models.list()
            print("✅ OpenAI API 連接成功")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI API 連接失敗: {e}")
            return False
    else:
        print("⚠️  OpenAI API Key 未設置")
        print("   某些 DeepEval 功能將無法使用")
        return False

if __name__ == "__main__":
    check_openai_config()
```

### 自動配置檢查
```bash
# 運行配置檢查
python3 -c "
import os
from config import OPENAI_API_KEY, OPENAI_MODEL
print('OpenAI API Key:', '已設置' if OPENAI_API_KEY else '未設置')
print('OpenAI Model:', OPENAI_MODEL)
"
```

## 💰 API 使用成本

### 模型價格 (2024年價格)
| 模型 | 輸入價格 | 輸出價格 | 適用場景 |
|------|----------|----------|----------|
| `gpt-3.5-turbo` | $0.0015/1K tokens | $0.002/1K tokens | 日常評估 |
| `gpt-4` | $0.03/1K tokens | $0.06/1K tokens | 高精度評估 |
| `gpt-4-turbo` | $0.01/1K tokens | $0.03/1K tokens | 平衡選擇 |

### 成本估算
```python
# 評估 10 個問題的大概成本
def estimate_cost(num_questions=10, model="gpt-3.5-turbo"):
    # 每個問題大約使用 500-1000 tokens
    avg_tokens_per_question = 750
    total_tokens = num_questions * avg_tokens_per_question
    
    costs = {
        "gpt-3.5-turbo": (0.0015 + 0.002) / 1000,  # $0.0035 per 1K tokens
        "gpt-4": (0.03 + 0.06) / 1000,             # $0.09 per 1K tokens
        "gpt-4-turbo": (0.01 + 0.03) / 1000        # $0.04 per 1K tokens
    }
    
    cost_per_token = costs.get(model, costs["gpt-3.5-turbo"])
    estimated_cost = total_tokens * cost_per_token
    
    print(f"評估 {num_questions} 個問題 ({model}):")
    print(f"預估 tokens: {total_tokens}")
    print(f"預估成本: ${estimated_cost:.4f}")
    
    return estimated_cost

# 使用示例
estimate_cost(10, "gpt-3.5-turbo")  # 約 $0.026
estimate_cost(10, "gpt-4")          # 約 $0.675
```

## 🔒 安全最佳實踐

### 1. 環境變數管理
```bash
# 使用 .env 文件但不要提交到 git
echo ".env" >> .gitignore

# 創建 .env.example 作為模板
cat > .env.example << EOF
# OpenAI API 配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# RAGFlow API 配置
RAGFLOW_API_URL=http://your-ragflow-server:8080
RAGFLOW_API_KEY=your-ragflow-api-key
EOF
```

### 2. API Key 輪換
```python
# 支援多個 API Key 輪換使用
OPENAI_API_KEYS = [
    os.getenv('OPENAI_API_KEY_1'),
    os.getenv('OPENAI_API_KEY_2'),
    os.getenv('OPENAI_API_KEY_3')
]

def get_available_api_key():
    """獲取可用的 API Key"""
    for key in OPENAI_API_KEYS:
        if key and test_api_key(key):
            return key
    return None
```

### 3. 使用限制
```python
# 設置使用限制避免意外高費用
MAX_DAILY_REQUESTS = 100
MAX_TOKENS_PER_REQUEST = 2000

def check_usage_limits():
    """檢查使用限制"""
    # 實現使用量追蹤邏輯
    pass
```

## 🚀 快速開始

### 一鍵配置腳本
```bash
#!/bin/bash
# setup_openai.sh

echo "🔧 OpenAI API 配置助手"
echo "====================="

# 檢查是否已有配置
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ 已檢測到 OpenAI API Key"
else
    echo "請輸入你的 OpenAI API Key:"
    read -s api_key
    export OPENAI_API_KEY="$api_key"
    echo "✅ API Key 已設置"
fi

# 選擇模型
echo "選擇評估模型:"
echo "1. gpt-3.5-turbo (推薦，成本低)"
echo "2. gpt-4 (高精度，成本高)"
echo "3. gpt-4-turbo (平衡選擇)"

read -p "請選擇 [1-3]: " choice

case $choice in
    1) export OPENAI_MODEL="gpt-3.5-turbo" ;;
    2) export OPENAI_MODEL="gpt-4" ;;
    3) export OPENAI_MODEL="gpt-4-turbo" ;;
    *) export OPENAI_MODEL="gpt-3.5-turbo" ;;
esac

echo "✅ 模型設置為: $OPENAI_MODEL"

# 測試配置
echo "🧪 測試配置..."
python3 -c "
from deepeval_integration import RAGFlowEvaluator
evaluator = RAGFlowEvaluator()
print('✅ DeepEval 配置成功')
"

echo "🎉 配置完成！現在可以運行評估了："
echo "python3 test/deepeval_demo.py"
```

### 使用配置腳本
```bash
# 給腳本執行權限
chmod +x setup_openai.sh

# 運行配置
./setup_openai.sh
```

## 🔍 故障排除

### 常見問題

#### 1. API Key 無效
```
錯誤: Invalid API key provided
解決: 檢查 API Key 是否正確，是否有效期內
```

#### 2. 配額超限
```
錯誤: You exceeded your current quota
解決: 檢查 OpenAI 帳戶餘額，或等待配額重置
```

#### 3. 網絡連接問題
```
錯誤: Connection timeout
解決: 檢查網絡連接，或使用代理
```

#### 4. 環境變數未生效
```bash
# 檢查環境變數
env | grep OPENAI

# 重新載入環境變數
source ~/.zshrc  # 或 ~/.bashrc
```

## 📚 相關資源

- [OpenAI API 文檔](https://platform.openai.com/docs)
- [OpenAI API Keys 管理](https://platform.openai.com/api-keys)
- [OpenAI 價格頁面](https://openai.com/pricing)
- [DeepEval 官方文檔](https://docs.confident-ai.com/)

---

**更新時間**: 2025年8月3日  
**版本**: v1.0.0