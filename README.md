# 🚀 RAGFlow API FastAPI

基於 FastAPI 和 Streamlit 的 RAG (Retrieval-Augmented Generation) 評估系統，整合了 RAGFlow 和 DeepEval 技術。

![項目展示](image/截圖%202025-08-02%20下午6.22.30.png)

## ✨ 項目特色

- 🧪 **真實評估**: 使用真實 DeepEval 指標，非模擬分數
- 📊 **專業界面**: 側邊欄控制 + 主頁面展示的現代化界面
- 🔧 **雙模式支持**: 支持有/無 OpenAI API Key 的評估模式
- 📈 **完整流程**: 從問題生成到結果分析的完整評估流程
- 🛡️ **錯誤友好**: 完善的異常處理和用戶提示

## 🎯 核心應用

| 應用 | 端口 | 功能 | 推薦場景 |
|------|------|------|----------|
| **rag_evaluation.py** | 8502 | RAG 評估系統 ⭐ | 生產環境評估 |
| **streamlit_app.py** | 8501 | 基礎聊天界面 | 功能測試 |
| **deepeval_dashboard.py** | 8503 | 結果分析儀表板 | 數據分析 |
| **fastapi_server.py** | 8000 | 後端 API 服務 | API 接口 |

## 🚀 快速開始

### 1. **RAG 評估系統** (推薦)
```bash
# 設置 OpenAI API Key (可選)
export OPENAI_API_KEY="your-openai-api-key"

# 啟動評估系統
streamlit run rag_evaluation.py --server.port 8502

# 訪問 http://localhost:8502
```

### 2. **基礎聊天功能**
```bash
# 啟動後端服務
python3 fastapi_server.py

# 啟動聊天界面
streamlit run streamlit_app.py --server.port 8501
```

### 3. **評估結果分析**
```bash
# 啟動儀表板
streamlit run deepeval_dashboard.py --server.port 8503
```

## 🧪 評估指標

### 真實 DeepEval 指標
- **Answer Relevancy**: 回答與問題的相關性
- **Faithfulness**: 回答對檢索內容的忠實度
- **Contextual Precision**: 檢索內容的精確度
- **Contextual Recall**: 檢索內容的完整性
- **Hallucination**: 虛假信息檢測
- **Bias**: 偏見檢測

## 📁 項目結構

```
ragflow_api_fastapi/
├── 🚀 核心應用
│   ├── rag_evaluation.py          # RAG 評估系統 ⭐
│   ├── streamlit_app.py           # 基礎聊天界面
│   ├── deepeval_dashboard.py      # 結果分析儀表板
│   └── fastapi_server.py          # 後端 API 服務
├── 🔧 核心模組
│   ├── ragflow_chatbot.py         # RAGFlow 客戶端
│   ├── deepeval_integration.py    # DeepEval 整合
│   └── config.py                  # 配置管理
├── 🧪 test/                       # 測試文件
├── 📚 docs/                       # 詳細文檔
└── 📋 使用指南
    ├── USAGE_GUIDE.md             # 使用指南
    ├── PROJECT_STRUCTURE.md       # 項目結構
    └── FIXED_EVALUATION_GUIDE.md  # 評估系統指南
```

## 🛠️ 安裝和配置

### 1. 環境準備
```bash
# 克隆項目
git clone <repository-url>
cd ragflow_api_fastapi

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置設置
```bash
# 複製環境變量模板
cp .env.example .env

# 編輯配置文件
vim .env
```

### 3. 啟動服務
```bash
# 啟動 RAG 評估系統
streamlit run rag_evaluation.py --server.port 8502
```

## 📊 使用流程

### RAG 評估完整流程

1. **選擇數據集** - 在側邊欄選擇要評估的知識庫
2. **配置參數** - 設定測試問題數量和評估閾值
3. **生成問題** - 自動生成針對性測試問題
4. **執行評估** - 運行真實的 DeepEval 評估
5. **分析結果** - 查看詳細結果和改進建議

## 🔧 故障排除

### 常見問題
- **模組導入錯誤**: 確保在虛擬環境中運行
- **端口衝突**: 使用不同端口啟動應用
- **API 連接失敗**: 檢查後端服務是否運行
- **OpenAI API 問題**: 驗證 API Key 設置

詳細解決方案請參考 [USAGE_GUIDE.md](USAGE_GUIDE.md)

## 📚 文檔

- [使用指南](USAGE_GUIDE.md) - 完整的使用說明
- [項目結構](PROJECT_STRUCTURE.md) - 詳細的項目結構說明
- [評估系統指南](FIXED_EVALUATION_GUIDE.md) - RAG 評估系統專門指南
- [API 文檔](docs/FASTAPI_GUIDE.md) - FastAPI 接口說明
- [Streamlit 指南](docs/STREAMLIT_GUIDE.md) - Streamlit 應用說明

## 🎯 核心特色

### 🧪 真實評估
- 使用官方 DeepEval 指標
- 真實的 LLMTestCase 評估
- 非模擬分數，確保評估準確性

### 📊 專業界面
- 側邊欄控制面板
- 主頁面結果展示
- 響應式設計

### 🔧 靈活配置
- 支持有/無 OpenAI API Key
- 可調整評估閾值
- 多種數據集支持

### 🛡️ 錯誤處理
- 完善的異常處理機制
- 用戶友好的錯誤提示
- 自動降級功能

## 🏆 最佳實踐

1. **開發階段**: 使用基礎聊天界面測試功能
2. **評估階段**: 使用 RAG 評估系統進行全面評估
3. **分析階段**: 使用儀表板分析評估結果
4. **優化階段**: 根據評估建議優化系統

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 許可證

MIT License

---

**立即開始使用:**
```bash
streamlit run rag_evaluation.py --server.port 8502
```

🎉 **享受專業的 RAG 評估體驗！**