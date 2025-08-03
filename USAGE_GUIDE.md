# 🚀 RAGFlow API FastAPI 使用指南

## 🎯 快速開始

### 1. **基礎聊天功能**
```bash
# 1. 啟動後端服務
python3 fastapi_server.py

# 2. 啟動聊天界面
streamlit run streamlit_app.py --server.port 8501

# 3. 訪問 http://localhost:8501
```

### 2. **RAG 評估系統** ⭐ (推薦)
```bash
# 1. 設置 OpenAI API Key (可選，但推薦)
export OPENAI_API_KEY="your-openai-api-key"

# 2. 啟動評估系統
streamlit run rag_evaluation.py --server.port 8502

# 3. 訪問 http://localhost:8502
```

### 3. **評估結果分析**
```bash
# 啟動儀表板
streamlit run deepeval_dashboard.py --server.port 8503

# 訪問 http://localhost:8503
```

## 🎨 應用功能對比

| 應用 | 端口 | 主要功能 | 推薦使用場景 |
|------|------|----------|--------------|
| `streamlit_app.py` | 8501 | 基礎聊天界面 | 測試 RAG 系統功能 |
| `rag_evaluation.py` | 8502 | **RAG 評估系統** | **生產環境評估** ⭐ |
| `deepeval_dashboard.py` | 8503 | 結果分析儀表板 | 評估結果視覺化 |
| `fastapi_server.py` | 8000 | 後端 API 服務 | 提供 API 接口 |

## 🧪 RAG 評估系統使用步驟

### 📋 完整評估流程

1. **啟動系統**:
```bash
streamlit run rag_evaluation.py --server.port 8502
```

2. **配置評估**:
   - 👈 在左側邊欄選擇數據集
   - 🎯 設定測試問題數量 (1-10)
   - 📊 調整評估閾值 (可選)

3. **生成測試問題**:
   - 📝 點擊「生成測試問題」
   - 🔍 預覽生成的問題

4. **執行評估**:
   - 🧪 點擊「開始評估」
   - ⏳ 等待評估完成

5. **查看結果**:
   - 📊 查看整體統計
   - 📋 查看詳細結果
   - 💾 導出評估報告

### 🔧 評估模式

#### **真實評估模式** (推薦)
```bash
# 需要 OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"
streamlit run rag_evaluation.py --server.port 8502
```

**特色:**
- 🧪 使用真實 DeepEval 指標
- 📊 Answer Relevancy, Faithfulness 等
- 💡 基於真實結果的改進建議

#### **基礎評估模式**
```bash
# 無需 OpenAI API Key
streamlit run rag_evaluation.py --server.port 8502
```

**特色:**
- 📊 基礎相關性評估
- 🔍 回答質量分析
- 📈 上下文匹配度

## 📊 評估指標說明

### 🧪 真實 DeepEval 指標
- **Answer Relevancy**: 回答與問題的相關性 (0-1, 越高越好)
- **Faithfulness**: 回答對檢索內容的忠實度 (0-1, 越高越好)
- **Contextual Precision**: 檢索內容的精確度 (0-1, 越高越好)
- **Contextual Recall**: 檢索內容的完整性 (0-1, 越高越好)
- **Hallucination**: 虛假信息檢測 (0-1, 越低越好)
- **Bias**: 偏見檢測 (0-1, 越低越好)

### 📈 評估閾值建議

| 指標 | 開發階段 | 生產環境 | 法律專業 |
|------|----------|----------|----------|
| Answer Relevancy | ≥ 0.6 | ≥ 0.8 | ≥ 0.8 |
| Faithfulness | ≥ 0.6 | ≥ 0.8 | ≥ 0.9 |
| Contextual Precision | ≥ 0.6 | ≥ 0.8 | ≥ 0.8 |
| Contextual Recall | ≥ 0.6 | ≥ 0.7 | ≥ 0.7 |
| Hallucination | ≤ 0.4 | ≤ 0.2 | ≤ 0.1 |
| Bias | ≤ 0.6 | ≤ 0.3 | ≤ 0.2 |

## 🛠️ 故障排除

### 常見問題解決

1. **模組導入錯誤**:
```bash
# 確保在虛擬環境中
source venv/bin/activate
pip install -r requirements.txt
```

2. **端口衝突**:
```bash
# 使用不同端口
streamlit run rag_evaluation.py --server.port 8504
```

3. **API 連接失敗**:
```bash
# 檢查後端服務
python3 fastapi_server.py
curl http://localhost:8000/
```

4. **OpenAI API 問題**:
```bash
# 檢查 API Key
echo $OPENAI_API_KEY

# 測試 API 連接
python3 -c "import openai; print('API Key 有效')"
```

## 📁 項目結構

```
ragflow_api_fastapi/
├── 🚀 核心應用
│   ├── fastapi_server.py          # 後端服務
│   ├── streamlit_app.py           # 聊天界面
│   ├── rag_evaluation.py          # 評估系統 ⭐
│   └── deepeval_dashboard.py      # 結果儀表板
├── 🔧 核心模組
│   ├── ragflow_chatbot.py         # RAGFlow 客戶端
│   ├── deepeval_integration.py    # DeepEval 整合
│   └── config.py                  # 配置管理
├── 🧪 test/                       # 測試文件
├── 📚 docs/                       # 文檔
└── 📋 項目文檔
```

## 🎯 最佳實踐

### 🥇 推薦工作流程

1. **開發階段**:
```bash
# 1. 基礎功能測試
streamlit run streamlit_app.py --server.port 8501

# 2. 評估系統測試
streamlit run rag_evaluation.py --server.port 8502
```

2. **生產環境**:
```bash
# 1. 設置 API Key
export OPENAI_API_KEY="your-api-key"

# 2. 執行完整評估
streamlit run rag_evaluation.py --server.port 8502

# 3. 分析評估結果
streamlit run deepeval_dashboard.py --server.port 8503
```

### 📊 評估建議

- **測試問題數量**: 開發階段 3-5 個，生產環境 10-20 個
- **評估頻率**: 每次模型更新後進行評估
- **閾值調整**: 根據業務需求調整評估標準
- **結果分析**: 重點關注失敗案例的改進建議

## 🏆 總結

**RAG 評估系統** (`rag_evaluation.py`) 是項目的核心功能：

- ✅ **功能完整**: 問題生成 → 評估執行 → 結果分析
- ✅ **界面友好**: 側邊欄控制 + 主頁面展示
- ✅ **雙模式支持**: 有/無 OpenAI API Key 都能運行
- ✅ **錯誤處理**: 完善的異常處理機制
- ✅ **專業評估**: 使用真實 DeepEval 指標

**立即開始使用:**
```bash
streamlit run rag_evaluation.py --server.port 8502
```

**訪問地址:**
```
http://localhost:8502
```

🎉 **現在你有一個完整、穩定、專業的 RAG 評估系統了！**