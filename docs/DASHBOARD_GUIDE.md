# DeepEval 儀表板使用指南

## 🎯 概述

DeepEval 儀表板是一個基於 Streamlit 的專業評估數據視覺化工具，幫你分析 RAG 系統的性能表現。

## 🚀 快速開始

### 方法1: 一鍵啟動 (推薦)
```bash
python3 run_dashboard.py
```

### 方法2: 直接啟動
```bash
streamlit run deepeval_dashboard.py
```

### 方法3: 生成示例數據測試
```bash
# 先生成示例數據
python3 generate_sample_data.py

# 然後啟動儀表板
python3 run_dashboard.py
```

## 📊 儀表板功能

### 1. 📈 整體表現摘要
- **總測試案例**: 顯示評估的總數量
- **通過案例**: 達到閾值標準的案例數
- **通過率**: 系統整體表現百分比
- **平均分數**: 所有案例的平均評估分數

### 2. 🎯 評估指標詳情
- **雷達圖**: 直觀顯示各項指標的平均表現
- **統計表**: 詳細的指標統計數據（平均值、最小值、最大值、標準差）

### 3. 📊 數據分析圖表
- **分數分布直方圖**: 顯示整體分數的分布情況
- **通過/失敗比例餅圖**: 視覺化通過率
- **指標相關性熱力圖**: 分析不同指標之間的關聯性

### 4. 📋 詳細評估結果
- **篩選功能**: 
  - 只顯示通過的案例
  - 只顯示失敗的案例
  - 按最低分數篩選
- **展開式詳情**: 查看每個測試案例的完整信息
  - 問題內容
  - 實際回答
  - 期望回答
  - 各項指標分數

### 5. 💾 導出功能
- **CSV 導出**: 將評估數據導出為 Excel 可讀的格式
- **摘要報告**: 生成 Markdown 格式的評估報告
- **JSON 導出**: 保存原始評估數據

## 📁 支援的數據格式

### 標準格式
```json
[
  {
    "test_case_id": "test_001",
    "question": "什麼是憲法第7條？",
    "actual_output": "憲法第7條規定平等原則...",
    "expected_output": "憲法第7條規定中華民國人民在法律上一律平等...",
    "overall_score": 0.756,
    "passed": true,
    "metrics_scores": {
      "answer_relevancy": 0.823,
      "faithfulness": 0.789,
      "contextual_precision": 0.734,
      "contextual_recall": 0.712,
      "hallucination": 0.234,
      "bias": 0.156
    }
  }
]
```

### 摘要格式
```json
{
  "timestamp": "2025-08-03T10:30:00",
  "total_cases": 20,
  "passed_cases": 16,
  "overall_pass_rate": 80.0,
  "overall_avg_score": 0.756,
  "dataset_results": [
    {
      "dataset_name": "法律考試數據集",
      "results": [...]
    }
  ]
}
```

## 🔧 使用技巧

### 1. 數據載入
- **現有文件**: 儀表板會自動掃描當前目錄的 JSON 文件
- **文件上傳**: 支援拖拽上傳評估結果文件
- **多種格式**: 自動識別不同的數據結構

### 2. 分析技巧
- **關注通過率**: 低於 80% 需要改進系統
- **查看分數分布**: 了解系統性能的一致性
- **分析失敗案例**: 找出系統的薄弱環節
- **指標相關性**: 理解不同指標之間的關係

### 3. 改進建議
- **低相關性**: 改進檢索算法或問題理解
- **低忠實度**: 加強基於檢索內容的回答生成
- **高幻覺率**: 實施更嚴格的事實檢查
- **高偏見**: 審查訓練數據和回答模板

## 📊 實際使用場景

### 場景1: 系統開發階段
```bash
# 1. 運行評估
python3 test/deepeval_demo.py

# 2. 啟動儀表板分析結果
python3 run_dashboard.py

# 3. 根據分析結果調整系統
python3 adjust_thresholds.py
```

### 場景2: 定期性能監控
```bash
# 1. 定期運行完整評估
python3 test/run_deepeval_test.py

# 2. 在儀表板中比較歷史數據
# 載入不同時間的評估結果文件

# 3. 追蹤性能變化趨勢
```

### 場景3: A/B 測試比較
```bash
# 1. 評估版本A
python3 test/run_deepeval_test.py  # 生成 evaluation_v1.json

# 2. 評估版本B  
python3 test/run_deepeval_test.py  # 生成 evaluation_v2.json

# 3. 在儀表板中分別載入比較
```

## 🎨 界面說明

### 主要區域
1. **標題欄**: 顯示當前載入的文件信息
2. **側邊欄**: 文件載入和上傳功能
3. **主內容區**: 分為多個標籤頁
   - 整體摘要
   - 指標詳情
   - 圖表分析
   - 詳細結果
   - 導出選項

### 互動功能
- **篩選器**: 動態篩選顯示的數據
- **展開面板**: 點擊查看詳細信息
- **下載按鈕**: 一鍵導出分析結果
- **圖表縮放**: 支援圖表的放大和縮小

## 🔍 故障排除

### 常見問題

#### 1. 儀表板無法啟動
```bash
# 檢查依賴
pip install streamlit plotly pandas

# 檢查端口
lsof -i :8501  # 查看端口是否被佔用
```

#### 2. 數據載入失敗
```bash
# 檢查 JSON 格式
python3 -c "import json; json.load(open('your_file.json'))"

# 檢查文件權限
ls -la your_file.json
```

#### 3. 圖表顯示異常
```bash
# 更新 plotly
pip install --upgrade plotly

# 清除瀏覽器緩存
```

#### 4. 性能問題
- 大文件 (>1000 案例) 可能載入較慢
- 建議分批處理或使用篩選功能
- 關閉不需要的瀏覽器標籤頁

## 💡 最佳實踐

### 1. 數據組織
- 使用有意義的文件名 (如: `evaluation_legal_20250803.json`)
- 定期備份評估結果
- 建立版本控制系統

### 2. 分析流程
1. 先查看整體摘要了解大局
2. 深入分析指標詳情找出問題
3. 檢查失敗案例了解具體問題
4. 導出報告用於團隊討論

### 3. 持續改進
- 設定定期評估計劃
- 追蹤關鍵指標趨勢
- 建立改進目標和里程碑
- 記錄改進措施的效果

## 🚀 進階功能

### 自定義分析
```python
# 在儀表板基礎上添加自定義分析
import streamlit as st
import pandas as pd

# 載入數據後進行自定義處理
if st.button("自定義分析"):
    # 你的分析邏輯
    pass
```

### 批量處理
```bash
# 批量處理多個評估文件
for file in evaluation_*.json; do
    echo "處理 $file"
    # 你的處理邏輯
done
```

## 📚 相關資源

- [Streamlit 官方文檔](https://docs.streamlit.io/)
- [Plotly 圖表庫](https://plotly.com/python/)
- [DeepEval 評估指南](DEEPEVAL_GUIDE.md)
- [評估指標說明](metrics_explanation.md)

---

**更新時間**: 2025年8月3日  
**版本**: v1.0.0  
**維護者**: Kiro AI Assistant