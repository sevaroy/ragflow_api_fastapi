# 測試和評估系統

## 🧪 測試文件說明

### 基本測試
- `ragflow_test.py` - RAGFlow API 連接測試
- `test_api_endpoints.py` - API 端點功能測試
- `run_all_tests.py` - 執行所有基本測試

### DeepEval 評估系統
- `deepeval_demo.py` - 快速演示 DeepEval 功能
- `run_deepeval_test.py` - 完整的評估測試流程

### 演示程序
- `final_demo.py` - 完整功能演示
- `demo.py` - 基本功能演示

## 🚀 快速開始

### 1. 基本測試
```bash
# 測試 RAGFlow 連接
python3 test/ragflow_test.py

# 測試所有 API 端點
python3 test/test_api_endpoints.py

# 運行所有基本測試
python3 test/run_all_tests.py
```

### 2. DeepEval 評估
```bash
# 設置 DeepEval 環境
python3 setup_deepeval.py

# 快速演示
python3 test/deepeval_demo.py

# 完整評估
python3 test/run_deepeval_test.py
```

## 📊 評估系統特色

### 自動問答數據生成
- 基於數據集內容自動生成測試問題
- 支援法律、技術等專業領域
- 可自定義問題數量和難度

### 多維度評估指標
- 回答相關性 (Answer Relevancy)
- 回答忠實度 (Faithfulness)
- 上下文精確度 (Contextual Precision)
- 上下文召回率 (Contextual Recall)
- 幻覺檢測 (Hallucination)
- 偏見檢測 (Bias)

### 詳細評估報告
- 整體統計數據
- 各項指標詳情
- 失敗案例分析
- 改進建議

## 🔧 配置說明

### 環境變數
```bash
# RAGFlow API (必需)
export RAGFLOW_API_URL="http://your-ragflow-server:8080"
export RAGFLOW_API_KEY="your-api-key"

# OpenAI API (可選，用於高級評估)
export OPENAI_API_KEY="your-openai-key"
```

### 評估參數
- 預設問題數量: 10
- 最大問題數量: 50
- 評估指標閾值: 可在 `deepeval_config.py` 中調整

## 📝 使用示例

### 基本評估流程
```python
from deepeval_integration import RAGFlowEvaluator

# 創建評估器
evaluator = RAGFlowEvaluator()

# 設置數據集
evaluator.setup_chatbot("dataset-id", "數據集名稱")

# 生成測試數據
test_data = evaluator.generate_test_data_from_documents("dataset-id", 5)

# 執行評估
results = evaluator.evaluate_test_cases(test_data)

# 生成報告
report = evaluator.generate_report(results)
print(report)
```

### 自定義測試數據
```python
custom_test_data = [
    {
        'id': 'test_1',
        'question': '什麼是人工智能？',
        'expected_answer': 'AI 是模擬人類智能的技術',
        'context': '人工智能相關內容',
        'source': 'manual'
    }
]

results = evaluator.evaluate_test_cases(custom_test_data)
```

## 🎯 評估結果解讀

### 分數範圍
- **0.8-1.0**: 優秀
- **0.6-0.8**: 良好
- **0.4-0.6**: 一般
- **0.0-0.4**: 需要改進

### 通過標準
- 單項指標達到設定閾值
- 整體分數 ≥ 0.6
- 通過率 ≥ 60%

## 🔍 故障排除

### 常見問題
1. **連接失敗**: 檢查 RAGFlow API 配置
2. **評估錯誤**: 確認 OpenAI API 密鑰設置
3. **數據生成失敗**: 檢查數據集是否存在
4. **內存不足**: 減少測試問題數量

### 調試模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 相關文檔

- [DeepEval 使用指南](../DEEPEVAL_GUIDE.md)
- [項目總結](../PROJECT_SUMMARY.md)
- [RAGFlow API 文檔](https://ragflow.io/docs/dev/python_api_reference)

---

**更新時間**: 2025年8月3日  
**版本**: v1.0.0