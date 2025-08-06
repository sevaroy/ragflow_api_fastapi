# TODO List – 功能與程式碼優化

> 本清單依照各個 app / 模組檢視結果彙整，供後續優化參考。

---

## components
- [ ] 抽出 `styles.py`／`constants.py` 統一管理顏色、CSS、文字。
- [ ] 將運算密集或 I/O 操作改為非同步，或使用 `st.spinner` / `st.cache_data`。
- [ ] 導入 `pydantic.BaseModel` 驗證元件輸入資料。
- [ ] 補充 docstring、型別註解，並撰寫 pytest snapshot 測試。

## services
- [ ] 將 `requests` 改為 `httpx.AsyncClient`，並整合 `tenacity` 重試機制。
- [ ] 抽出 `settings.py` (`pydantic.BaseSettings`) 管理 API_URL、TIMEOUT 等常數。
- [ ] 實作依賴注入方便 mock (`fastapi.Depends` 或自訂 DI pattern)。
- [ ] utils 函式加型別註解及單元測試。

## pages (Streamlit)
- [ ] 建立共用 `layout.py` 封裝 header / sidebar / footer。
- [ ] 將商業邏輯搬至 `controllers/` 以降低 UI 耦合。
- [ ] 使用 `st.experimental_memo` / `st.cache_resource` 快取模型與連線。
- [ ] 加入 `st.session_state` key 檢查避免例外。

## FastAPI / Backend
- [ ] 將 `integrated_ragflow_app.py` 拆分至 `routers/`、`services/` 等子模組。
- [ ] 改寫路由為 `async def` 搭配非同步 I/O。
- [ ] 為路由加入 `response_model`、`status_code`，開啟自動 OpenAPI 文件。
- [ ] 新增中介層 (logging, rate limiting, CORS)。





## 測試與 CI/CD
- [ ] 於 `pyproject.toml` 設定 coverage、mypy、ruff。
- [ ] 建立 `.github/workflows/ci.yml`：格式化、型別檢查、單測、Docker build。
- [ ] Dockerfile 採多階段建構並區隔 runtime / dev requirements。

## 通用
- [ ] 使用 `pydantic` Settings 統一環境變數與設定檔。
- [ ] 統一 logging（`structlog` 或標準 logging）。
- [ ] 全面啟用型別註解與 `mypy --strict`。
- [ ] 補充 README：開發流程、測試指令、部署方式。
- [ ] 採用 `pip-tools` / `poetry` 管理依賴並鎖定版本。

---

> 更新清單時，請保持條目簡潔，並於完成後勾選 ☑︎。
