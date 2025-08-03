# 📁 RAGFlow API FastAPI 項目結構

## 🎯 項目概述
這是一個基於 FastAPI 和 Streamlit 的 RAG (Retrieval-Augmented Generation) 評估系統，整合了 RAGFlow 和 DeepEval 技術。

## 📂 目錄結構

```
ragflow_api_fastapi/
├── 🚀 核心應用
│   ├── fastapi_server.py          # FastAPI 後端服務器
│   ├── streamlit_app.py           # 主聊天界面
│   ├── rag_evaluation.py          # RAG 評估系統 (最終版本)
│   └── deepeval_dashboard.py      # 評估結果儀表板
│
├── 🔧 核心模組
│   ├── config.py                  # 配置管理
│   ├── ragflow_chatbot.py         # RAGFlow 聊天機器人客戶端
│   ├── deepeval_integration.py    # DeepEval 整合模組
│   └── deepeval_config.py         # DeepEval 配置
│
├── 🧪 測試文件
│   ├── test/
│   │   ├── run_all_tests.py       # 運行所有測試
│   │   ├── run_deepeval_test.py   # DeepEval 測試
│   │   ├── deepeval_demo.py       # DeepEval 演示
│   │   ├── test_simple_evaluation.py # 簡單評估測試
│   │   ├── demo_method2_workflow.py # 工作流程演示
│   │   ├── generate_sample_data.py # 生成示例數據
│   │   ├── adjust_thresholds.py   # 閾值調整工具
│   │   ├── check_config.py        # 配置檢查工具
│   │   ├── setup_deepeval.py      # DeepEval 設置
│   │   └── result_analyzer.py     # 結果分析工具
│
├── 📚 文檔
│   ├── docs/
│   │   ├── FASTAPI_GUIDE.md       # FastAPI 使用指南
│   │   ├── STREAMLIT_GUIDE.md     # Streamlit 使用指南
│   │   ├── DEEPEVAL_GUIDE.md      # DeepEval 使用指南
│   │   ├── DASHBOARD_GUIDE.md     # 儀表板使用指南
│   │   ├── COMPLETE_APP_GUIDE.md  # 完整應用指南
│   │   ├── OPENAI_CONFIG_GUIDE.md # OpenAI 配置指南
│   │   ├── metrics_explanation.md # 指標說明
│   │   ├── why_thresholds_matter.md # 閾值重要性
│   │   ├── method2_workflow_explanation.md # 工作流程說明
│   │   ├── deepeval_note.md       # DeepEval 筆記
│   │   ├── model_config_info.md   # 模型配置信息
│   │   ├── setup_venv.md          # 虛擬環境設置
│   │   ├── VIRTUAL_ENV_SETUP.md   # 虛擬環境設置指南
│   │   └── streamlit_apps_overview.md # Streamlit 應用概覽
│
├── 🎨 前端資源
│   ├── .streamlit/
│   │   └── config.toml            # Streamlit 配置
│   ├── templates/
│   │   └── index.html             # HTML 模板
│   └── image/                     # 圖片資源
│
├── 🐳 部署配置
│   ├── Dockerfile                 # Docker 配置
│   ├── docker-compose.yml         # Docker Compose 配置
│   ├── requirements.txt           # Python 依賴
│   └── setup_env.sh              # 環境設置腳本
│
├── 🔧 工具腳本
│   ├── run_full_stack.py          # 全棧運行腳本
│   └── start.py                   # 啟動腳本
│
├── 📋 項目文檔
│   ├── README.md                  # 項目說明
│   ├── PROJECT_SUMMARY.md         # 項目總結
│   ├── FIXED_EVALUATION_GUIDE.md  # 修復版評估指南
│   └── PROJECT_STRUCTURE.md       # 項目結構 (本文件)
│
└── ⚙️ 配置文件
    ├── .env.example               # 環境變量示例
    ├── .gitignore                 # Git 忽略文件
    └── venv/                      # Python 虛擬環境
```

## 🚀 核心應用說明

### 1. **fastapi_server.py** - 後端 API 服務
- 提供 RESTful API 接口
- 處理 RAGFlow 聊天請求
- 管理數據集和會話

### 2. **streamlit_app.py** - 主聊天界面
- 用戶友好的聊天界面
- 支持會話管理
- 實時問答功能

### 3. **rag_evaluation.py** - RAG 評估系統 ⭐
- **最終版本的 RAG 評估系統**
- 支持真實 DeepEval 指標評估
- 側邊欄控制，主頁面展示
- 完善的錯誤處理

### 4. **deepeval_dashboard.py** - 評估結果儀表板
- 專業的數據視覺化
- 支持多種圖表類型
- 結果導出功能

## 🔧 核心模組說明

### 1. **ragflow_chatbot.py**
- RAGFlow API 客戶端
- 聊天機器人實現
- 數據集管理

### 2. **deepeval_integration.py**
- DeepEval 整合邏輯
- 評估指標實現
- 測試數據生成

### 3. **config.py**
- 統一配置管理
- 環境變量處理
- API 密鑰管理

## 🎯 推薦使用流程

### 1. **基礎聊天測試**
```bash
# 1. 啟動後端服務
python3 fastapi_server.py

# 2. 啟動聊天界面
streamlit run streamlit_app.py --server.port 8501
```

### 2. **RAG 評估** (推薦)
```bash
# 1. 設置 OpenAI API Key (可選)
export OPENAI_API_KEY="your-api-key"

# 2. 啟動評估系統
streamlit run rag_evaluation.py --server.port 8502

# 3. 訪問 http://localhost:8502
```

### 3. **結果分析**
```bash
# 啟動儀表板
streamlit run deepeval_dashboard.py --server.port 8503
```

## 📊 端口分配

| 服務 | 端口 | 用途 |
|------|------|------|
| FastAPI 後端 | 8000 | API 服務 |
| 主聊天界面 | 8501 | 基礎聊天功能 |
| RAG 評估系統 | 8502 | 評估功能 |
| 評估儀表板 | 8503 | 結果分析 |

## 🔍 文件清理說明

### ✅ 保留的核心文件
- **rag_evaluation.py** - 最終版評估系統
- **streamlit_app.py** - 主聊天界面
- **deepeval_dashboard.py** - 結果儀表板
- **fastapi_server.py** - 後端服務

### 🗑️ 已清理的文件
- 過時的評估版本 (real_rag_evaluation.py, simple_rag_evaluation.py)
- 實驗性功能 (knowledge_base_evaluator.py, targeted_kb_evaluation.py)
- 重複的運行腳本
- 過時的工具腳本

### 📁 重新組織
- **測試文件** → `test/` 目錄
- **文檔文件** → `docs/` 目錄
- **核心應用** → 根目錄

## 🎉 項目特色

- ✅ **結構清晰**: 按功能分類組織
- ✅ **文檔完整**: 詳細的使用指南
- ✅ **測試完善**: 全面的測試覆蓋
- ✅ **部署就緒**: Docker 支持
- ✅ **功能完整**: 從聊天到評估的完整流程

**現在項目結構更加清晰和易於維護！** 🎯