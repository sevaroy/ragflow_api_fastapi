# 測試和開發工具

這個資料夾包含了開發過程中的測試案例、實驗性實現和開發工具。

## 📁 文件說明

### 測試工具
- `ragflow_test.py` - API 連線測試
- `test_api_endpoints.py` - API 端點測試
- `test_fastapi.py` - FastAPI 服務測試
- `test_streamlit.py` - Streamlit 應用測試
- `final_demo.py` - 完整演示程序
- `demo.py` - 基礎演示程序

### 實驗性實現
- `simple_chatbot.py` - 早期簡單實現
- `simple_chatbot_fixed.py` - 修復版實現
- `rag_chatbot.py` - 早期完整實現
- `ragflow_client.py` - 早期客戶端實現

### 開發工具
- `run_all_tests.py` - 統一測試啟動腳本 🚀
- `api_client_example.py` - API 客戶端示例
- `test_chatbots.py` - 聊天機器人測試工具
- `run_test.sh` - 一鍵測試腳本

## 🚀 使用方法

### 運行所有測試 (推薦)
```bash
python3 test/run_all_tests.py
```

### 運行 API 測試
```bash
python3 test/ragflow_test.py
```

### 測試 FastAPI 服務
```bash
python3 test/test_fastapi.py
```

### 測試 Streamlit 應用
```bash
python3 test/test_streamlit.py
```

### 運行完整演示
```bash
python3 test/final_demo.py
```

### 測試 API 端點
```bash
python3 test/test_api_endpoints.py
```

### API 客戶端示例
```bash
python3 test/api_client_example.py
```

## ⚠️ 注意事項

- 這些文件主要用於開發和測試目的
- 部分實現可能使用舊版 API 或實驗性功能
- 生產環境請使用根目錄下的最終版本

## 📚 開發歷程

這些文件記錄了從早期實驗到最終實現的完整開發過程：

1. **早期探索** - `simple_chatbot.py`
2. **API 調試** - `test_api_endpoints.py`
3. **功能完善** - `simple_chatbot_fixed.py`
4. **官方 API 適配** - 最終版本移至根目錄

## 🔄 版本演進

- v1.0: 基礎 API 調用實現
- v2.0: 錯誤處理和重試機制
- v3.0: 官方 API 標準化
- v4.0: 最終生產版本 (根目錄)