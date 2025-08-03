# DeepEval 評估指標詳解

## 📊 評估指標說明

### 1. 🎯 Answer Relevancy (回答相關性) - 閾值: 0.7

**含義**: 評估回答是否直接回應了用戶的問題

**評分標準**:
- **0.9-1.0**: 完美回應問題核心
- **0.7-0.9**: 基本回應問題，略有偏離
- **0.5-0.7**: 部分回應問題
- **0.0-0.5**: 回答與問題不相關

**法律領域示例**:
```
問題: "什麼是憲法第7條的平等原則？"
高分回答: "憲法第7條規定中華民國人民，無分男女、宗教、種族、階級、黨派，在法律上一律平等..."
低分回答: "憲法有很多條文，都很重要..." (太籠統)
```

**調整建議**:
- **嚴格標準**: 0.8 (適合正式評估)
- **寬鬆標準**: 0.6 (適合開發測試)

### 2. 🔍 Faithfulness (回答忠實度) - 閾值: 0.7

**含義**: 評估回答是否基於檢索到的上下文，沒有憑空捏造

**評分標準**:
- **0.9-1.0**: 完全基於檢索內容
- **0.7-0.9**: 主要基於檢索內容，少量推理
- **0.5-0.7**: 部分基於檢索內容
- **0.0-0.5**: 大量憑空捏造內容

**法律領域示例**:
```
檢索內容: "民法第1條：民事，法律所未規定者，依習慣；無習慣者，依法理。"
高分回答: "根據民法第1條，民事法源順序為法律、習慣、法理..."
低分回答: "民法第1條還規定了契約自由原則..." (憑空添加)
```

**調整建議**:
- **法律專業**: 0.8 (法律回答必須準確)
- **一般領域**: 0.6 (允許適度推理)

### 3. 🎯 Contextual Precision (上下文精確度) - 閾值: 0.7

**含義**: 評估檢索到的上下文是否與問題相關

**評分標準**:
- **0.9-1.0**: 檢索內容高度相關
- **0.7-0.9**: 檢索內容基本相關
- **0.5-0.7**: 檢索內容部分相關
- **0.0-0.5**: 檢索內容不相關

**影響因素**:
- 檢索算法的精確度
- 知識庫的組織結構
- 問題的表達清晰度

**調整建議**:
- **高質量知識庫**: 0.8
- **混合內容知識庫**: 0.6

### 4. 📚 Contextual Recall (上下文召回率) - 閾值: 0.7

**含義**: 評估是否檢索到了所有相關的上下文

**評分標準**:
- **0.9-1.0**: 檢索到所有相關內容
- **0.7-0.9**: 檢索到大部分相關內容
- **0.5-0.7**: 檢索到部分相關內容
- **0.0-0.5**: 遺漏大量相關內容

**法律領域示例**:
```
問題: "契約的成立要件"
應檢索: 要約、承諾、合意、對價等所有相關概念
高召回: 檢索到所有要件
低召回: 只檢索到要約和承諾
```

**調整建議**:
- **複雜主題**: 0.8 (需要全面檢索)
- **簡單主題**: 0.6 (基本檢索即可)

### 5. 🚫 Hallucination (幻覺檢測) - 閾值: 0.3

**含義**: 檢測回答中的虛假或憑空捏造的信息 (越低越好)

**評分標準**:
- **0.0-0.2**: 幾乎無幻覺，高度可信
- **0.2-0.3**: 輕微幻覺，基本可信
- **0.3-0.5**: 中等幻覺，需要注意
- **0.5-1.0**: 嚴重幻覺，不可信

**法律領域示例**:
```
問題: "民法第184條的內容"
正確: "因故意或過失，不法侵害他人之權利者，負損害賠償責任"
幻覺: "民法第184條規定契約自由原則" (完全錯誤)
```

**調整建議**:
- **法律/醫療**: 0.2 (零容忍錯誤)
- **一般知識**: 0.4 (允許輕微錯誤)

### 6. ⚖️ Bias (偏見檢測) - 閾值: 0.5

**含義**: 檢測回答中的偏見或不公平內容 (越低越好)

**評分標準**:
- **0.0-0.3**: 無明顯偏見，公正客觀
- **0.3-0.5**: 輕微偏見，基本公正
- **0.5-0.7**: 中等偏見，需要改進
- **0.7-1.0**: 嚴重偏見，不可接受

**偏見類型**:
- 性別偏見
- 種族偏見
- 宗教偏見
- 政治偏見
- 社會階層偏見

**調整建議**:
- **公共服務**: 0.3 (嚴格要求)
- **內部工具**: 0.6 (相對寬鬆)

## 🎯 不同場景的閾值建議

### 開發測試階段
```python
DEVELOPMENT_THRESHOLDS = {
    'answer_relevancy': 0.6,      # 寬鬆一些，便於測試
    'faithfulness': 0.6,          
    'contextual_precision': 0.6,  
    'contextual_recall': 0.6,     
    'hallucination': 0.4,         # 允許更多錯誤
    'bias': 0.6                   
}
```

### 生產環境
```python
PRODUCTION_THRESHOLDS = {
    'answer_relevancy': 0.8,      # 更嚴格的標準
    'faithfulness': 0.8,          
    'contextual_precision': 0.8,  
    'contextual_recall': 0.7,     
    'hallucination': 0.2,         # 幾乎零容忍
    'bias': 0.3                   
}
```

### 法律專業領域
```python
LEGAL_THRESHOLDS = {
    'answer_relevancy': 0.8,      # 必須切題
    'faithfulness': 0.9,          # 必須基於法條
    'contextual_precision': 0.8,  # 檢索必須精準
    'contextual_recall': 0.7,     # 不能遺漏重要法條
    'hallucination': 0.1,         # 法律錯誤不可接受
    'bias': 0.2                   # 法律必須公正
}
```

## 🔧 如何調整閾值

### 方法1: 修改配置文件
```python
# 在 deepeval_config.py 中修改
METRIC_THRESHOLDS = {
    'answer_relevancy': 0.8,  # 提高標準
    'faithfulness': 0.8,
    'hallucination': 0.2,     # 降低容忍度
    # ... 其他指標
}
```

### 方法2: 環境變數
```bash
export ANSWER_RELEVANCY_THRESHOLD=0.8
export FAITHFULNESS_THRESHOLD=0.8
export HALLUCINATION_THRESHOLD=0.2
```

### 方法3: 程式化調整
```python
from deepeval_integration import RAGFlowEvaluator

evaluator = RAGFlowEvaluator()

# 調整特定指標的閾值
evaluator.metrics['answer_relevancy'].threshold = 0.8
evaluator.metrics['hallucination'].threshold = 0.2
```

## 📊 閾值調整策略

### 1. 漸進式調整
```python
# 第一階段：寬鬆標準，快速迭代
PHASE_1_THRESHOLDS = {threshold: 0.6 for threshold in metrics}

# 第二階段：中等標準，穩定開發
PHASE_2_THRESHOLDS = {threshold: 0.7 for threshold in metrics}

# 第三階段：嚴格標準，生產就緒
PHASE_3_THRESHOLDS = {threshold: 0.8 for threshold in metrics}
```

### 2. 基於數據調整
```python
def analyze_performance_and_adjust():
    """基於歷史性能數據調整閾值"""
    
    # 分析過去100次評估的結果
    historical_scores = get_historical_scores()
    
    # 計算各指標的平均分數
    avg_scores = calculate_average_scores(historical_scores)
    
    # 設置閾值為平均分數的90%
    adjusted_thresholds = {
        metric: score * 0.9 
        for metric, score in avg_scores.items()
    }
    
    return adjusted_thresholds
```

### 3. A/B 測試
```python
def ab_test_thresholds():
    """A/B 測試不同閾值設置的效果"""
    
    # 測試組A：當前閾值
    group_a_results = evaluate_with_thresholds(CURRENT_THRESHOLDS)
    
    # 測試組B：調整後閾值
    group_b_results = evaluate_with_thresholds(ADJUSTED_THRESHOLDS)
    
    # 比較結果
    return compare_results(group_a_results, group_b_results)
```

## 💡 最佳實踐建議

### 1. 根據用途調整
- **研發階段**: 使用較寬鬆的閾值 (0.6-0.7)
- **測試階段**: 使用中等閾值 (0.7-0.8)
- **生產階段**: 使用嚴格閾值 (0.8-0.9)

### 2. 考慮領域特性
- **法律/醫療**: 對準確性要求極高
- **教育**: 平衡準確性和可理解性
- **娛樂**: 相對寬鬆，注重創意

### 3. 持續監控和調整
- 定期檢查評估結果
- 根據用戶反饋調整
- 考慮業務需求變化

### 4. 文檔化決策
- 記錄閾值調整的原因
- 追蹤調整後的效果
- 建立調整的標準流程