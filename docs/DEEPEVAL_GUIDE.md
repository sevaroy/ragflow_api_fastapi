# DeepEval 評估系統使用指南

## 🎯 概述

DeepEval 是一個專業的 LLM 評估框架，本項目將其整合到 RAGFlow 聊天機器人中，提供全面的 RAG 系統性能評估。

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 環境設置

```bash
# 可選：設置 OpenAI API 密鑰以使用高級評估功能
export OPENAI_API_KEY="your-openai-api-key"

# 確保 RAGFlow API 配置正確
# 編輯 config.py 文件
```

### 3. 快速演示

```bash
# 運行快速演示
python3 test/deepeval_demo.py
```

### 4. 完整評估

```bash
# 運行完整評估系統
python3 test/run_deepeval_test.py
```

## 📊 評估指標說明

### 核心指標

| 指標 | 說明 | 閾值 | 評估內容 |
|------|------|------|----------|
| **Answer Relevancy** | 回答相關性 | ≥0.7 | 回答是否直接回應問題 |
| **Faithfulness** | 回答忠實度 | ≥0.7 | 回答是否基於檢索到的上下文 |
| **Contextual Precision** | 上下文精確度 | ≥0.7 | 檢索到的上下文是否相關 |
| **Contextual Recall** | 上下文召回率 | ≥0.7 | 是否檢索到所有相關上下文 |
| **Hallucination** | 幻覺檢測 | ≤0.3 | 回答是否包含虛假信息 |
| **Bias** | 偏見檢測 | ≤0.5 | 回答是否存在偏見 |

### 法律專業指標

- **法條精確度**: 法條引用的準確性
- **判例相關性**: 相關判例的匹配程度
- **專業術語一致性**: 法律術語使用的正確性
- **考試導向性**: 回答對考試的實用性

## 🔧 使用方法

### 基本評估流程

```python
from deepeval_integration import RAGFlowEvaluator

# 1. 創建評估器
evaluator = RAGFlowEvaluator()

# 2. 設置數據集
dataset_id = "your-dataset-id"
evaluator.setup_chatbot(dataset_id, "數據集名稱")

# 3. 生成測試數據
test_data = evaluator.generate_test_data_from_documents(dataset_id, 10)

# 4. 執行評估
results = evaluator.evaluate_test_cases(test_data)

# 5. 生成報告
report = evaluator.generate_report(results)
print(report)

# 6. 保存結果
evaluator.save_results(results, "evaluation_results.json")
```

### 自定義測試數據

```python
# 手動創建測試數據
custom_test_data = [
    {
        'id': 'custom_1',
        'question': '什麼是憲法的基本原則？',
        'expected_answer': '憲法的基本原則包括人民主權、權力分立、基本人權保障等。',
        'context': '憲法相關內容',
        'source': 'manual'
    }
]

# 使用自定義數據評估
results = evaluator.evaluate_test_cases(custom_test_data)
```

### 配置自定義指標

```python
from deepeval.metrics import AnswerRelevancyMetric

# 創建自定義指標
custom_metric = AnswerRelevancyMetric(
    threshold=0.8,  # 提高閾值
    model="gpt-4",  # 使用更好的模型
    include_reason=True  # 包含評估理由
)

# 添加到評估器
evaluator.metrics['custom_relevancy'] = custom_metric
```

## 📝 問答數據生成

### 自動生成策略

1. **基於文檔內容**: 從數據集文檔中提取關鍵信息生成問題
2. **領域特化**: 根據數據集類型（法律、技術等）生成專業問題
3. **難度分級**: 生成不同難度級別的問題
4. **多樣化**: 確保問題類型的多樣性

### 法律領域問題生成

```python
# 法律專業問題模板
legal_templates = [
    "什麼是{concept}的基本原則？",
    "{law_area}中的{principle}如何理解？",
    "請解釋{legal_term}的定義和適用範圍",
    "{case_type}案件的處理程序是什麼？"
]

# 自動填充模板
concepts = ["憲法", "民法", "刑法", "行政法"]
questions = generate_from_templates(legal_templates, concepts)
```

### 技術領域問題生成

```python
# 技術專業問題模板
tech_templates = [
    "什麼是{technology}？",
    "如何實現{feature}功能？",
    "{framework}的主要特點是什麼？",
    "{concept}的工作原理是什麼？"
]

# 技術概念
technologies = ["API", "REST", "GraphQL", "微服務"]
questions = generate_from_templates(tech_templates, technologies)
```

## 📊 評估報告解讀

### 報告結構

```
📊 RAGFlow 系統評估報告
==================================================

📈 整體統計:
- 總測試案例: 10
- 通過案例: 8
- 通過率: 80.0%
- 平均分數: 0.756

📋 指標詳情:
- answer_relevancy: 平均 0.823 (範圍: 0.654 - 0.945)
- faithfulness: 平均 0.789 (範圍: 0.612 - 0.891)

🔍 詳細結果:
1. ✅ 通過 | 分數: 0.856 | 什麼是憲法的基本原則？...
2. ❌ 失敗 | 分數: 0.634 | 民法中的契約自由原則是什麼？...
```

### 分數解釋

- **0.8-1.0**: 優秀 - 系統表現非常好
- **0.6-0.8**: 良好 - 系統表現可接受，有改進空間
- **0.4-0.6**: 一般 - 系統需要優化
- **0.0-0.4**: 差 - 系統存在嚴重問題

### 改進建議

根據評估結果，可以考慮以下改進方向：

1. **低相關性分數**: 改進檢索算法或擴充知識庫
2. **低忠實度分數**: 優化回答生成邏輯，確保基於檢索內容
3. **高幻覺分數**: 加強事實檢查機制
4. **高偏見分數**: 審查訓練數據和回答模板

## 🛠️ 進階功能

### 批量評估

```python
# 評估多個數據集
datasets = evaluator.client.list_datasets()['data']

for dataset in datasets:
    evaluator.setup_chatbot(dataset['id'], dataset['name'])
    test_data = evaluator.generate_test_data_from_documents(dataset['id'], 5)
    results = evaluator.evaluate_test_cases(test_data)
    
    # 保存每個數據集的結果
    filename = f"eval_{dataset['name']}.json"
    evaluator.save_results(results, filename)
```

### 自定義評估流程

```python
class CustomEvaluator(RAGFlowEvaluator):
    def custom_evaluation_step(self, test_case, result):
        """自定義評估步驟"""
        # 添加特定領域的評估邏輯
        pass
    
    def generate_custom_report(self, results):
        """生成自定義報告"""
        # 實現特定的報告格式
        pass
```

### 持續評估

```python
import schedule
import time

def scheduled_evaluation():
    """定期評估任務"""
    evaluator = RAGFlowEvaluator()
    # 執行評估邏輯
    pass

# 每天執行一次評估
schedule.every().day.at("02:00").do(scheduled_evaluation)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 🔍 故障排除

### 常見問題

1. **OpenAI API 錯誤**
   ```
   解決方案: 檢查 API 密鑰設置和網絡連接
   export OPENAI_API_KEY="your-key"
   ```

2. **RAGFlow 連接失敗**
   ```
   解決方案: 檢查 config.py 中的 API 配置
   ```

3. **評估指標計算失敗**
   ```
   解決方案: 確保測試數據格式正確，檢查依賴版本
   ```

4. **內存不足**
   ```
   解決方案: 減少批量大小或使用更輕量的模型
   ```

### 調試模式

```python
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)

# 使用調試模式
evaluator = RAGFlowEvaluator()
evaluator.debug_mode = True
```

## 📚 參考資源

- [DeepEval 官方文檔](https://docs.confident-ai.com/)
- [RAGFlow API 文檔](https://ragflow.io/docs/dev/python_api_reference)
- [OpenAI API 文檔](https://platform.openai.com/docs)

## 🤝 貢獻指南

歡迎提交問題報告和功能請求：

1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 發起 Pull Request

## 📄 許可證

MIT License - 詳見 LICENSE 文件

---

**最後更新**: 2025年8月3日  
**版本**: v1.0.0  
**維護者**: Kiro AI Assistant