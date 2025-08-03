# DeepEval 模型配置說明

## 🤖 目前的模型設定

### 預設評估模型
- **模型**: `gpt-3.5-turbo`
- **用途**: DeepEval 評估指標計算
- **成本**: 相對較低
- **性能**: 適合大多數評估任務

### 模型使用架構
```
你的問題 → RAGFlow系統 → 回答 → DeepEval評估 → 評估結果
           (你的模型)      ↗️        (gpt-3.5-turbo)
```

## ⚙️ 如何更改評估模型

### 方法1: 環境變數
```bash
# 使用更強的模型
export OPENAI_MODEL="gpt-4"

# 使用更便宜的模型  
export OPENAI_MODEL="gpt-3.5-turbo"

# 使用最新模型
export OPENAI_MODEL="gpt-4-turbo-preview"
```

### 方法2: 程式碼配置
```python
from deepeval_config import DeepEvalConfig

# 臨時更改模型
DeepEvalConfig.OPENAI_MODEL = "gpt-4"

# 或在初始化時指定
evaluator = RAGFlowEvaluator()
# 評估指標會使用指定的模型
```

### 方法3: 個別指標自定義
```python
from deepeval.metrics import AnswerRelevancyMetric

# 為特定指標使用不同模型
custom_metric = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-4",  # 使用 GPT-4 進行相關性評估
    include_reason=True
)

evaluator.metrics['answer_relevancy'] = custom_metric
```

## 💰 模型成本比較

| 模型 | 輸入成本 | 輸出成本 | 適用場景 |
|------|----------|----------|----------|
| `gpt-3.5-turbo` | $0.0015/1K tokens | $0.002/1K tokens | 日常評估 |
| `gpt-4` | $0.03/1K tokens | $0.06/1K tokens | 高精度評估 |
| `gpt-4-turbo` | $0.01/1K tokens | $0.03/1K tokens | 平衡選擇 |

## 🎯 模型選擇建議

### 開發階段
- **推薦**: `gpt-3.5-turbo`
- **原因**: 成本低，速度快，適合大量測試

### 生產評估
- **推薦**: `gpt-4` 或 `gpt-4-turbo`
- **原因**: 評估精度更高，更可靠

### 法律專業評估
- **推薦**: `gpt-4`
- **原因**: 對專業術語理解更準確

## 🔍 無 OpenAI API 的情況

如果沒有設置 `OPENAI_API_KEY`，系統會：

1. **跳過 AI 評估指標**: 如 Answer Relevancy, Faithfulness
2. **使用基礎評估**: 基於規則的簡單評估
3. **仍可正常運行**: 基本功能不受影響

```python
# 無 API 時的評估邏輯
if not self.openai_api_key:
    # 使用簡單的評估方法
    score = len(actual_output) > 10 ? 0.7 : 0.3
    passed = score >= 0.6
```

## 🛠️ 實際配置示例

### 完整配置
```bash
# .env 文件
RAGFLOW_API_URL=http://your-ragflow-server:8080
RAGFLOW_API_KEY=your-ragflow-api-key
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

### 檢查當前配置
```python
python3 deepeval_config.py
```

輸出示例:
```
⚙️  DeepEval 配置狀態
------------------------------
✅ 配置驗證通過

📊 評估設置:
   - 預設問題數量: 10
   - 最大問題數量: 50
   - OpenAI 模型: gpt-3.5-turbo

🎯 指標閾值:
   - answer_relevancy: 0.7
   - faithfulness: 0.7
   - hallucination: 0.3
```