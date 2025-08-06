.PHONY: install dev-install pre-commit pre-commit-install format check-types test test-cov clean

# 安裝依賴
install:
	pip install -r requirements.txt

# 安裝開發依賴並設置 pre-commit
dev-install:
	pip install -r requirements.txt
	pre-commit install

# 運行 pre-commit 檢查
pre-commit:
	pre-commit run --all-files

# 安裝 pre-commit 鉤子
pre-commit-install:
	pre-commit install

# 格式化代碼
format:
	black .
	isort .

# 檢查代碼風格
lint:
	ruff check .

# 檢查類型
check-types:
	mypy .

# 運行測試
test:
	pytest

# 運行測試並生成覆蓋率報告
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

# 清理臨時文件
clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf __pycache__
	rm -rf *.egg-info
