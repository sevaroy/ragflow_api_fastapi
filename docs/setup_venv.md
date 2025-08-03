# 虛擬環境設置指南

## 🐍 Python 虛擬環境設置

### 1. 創建虛擬環境
```bash
# 創建名為 venv 的虛擬環境
python3 -m venv venv
```

### 2. 啟動虛擬環境

#### macOS/Linux
```bash
# 啟動虛擬環境
source venv/bin/activate

# 你會看到命令提示符前面出現 (venv)
(venv) $ 
```

#### Windows
```cmd
# 啟動虛擬環境
venv\Scripts\activate

# 你會看到命令提示符前面出現 (venv)
(venv) C:\path\to\project>
```

### 3. 安裝依賴
```bash
# 確保在虛擬環境中 (看到 (venv) 前綴)
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```

### 4. 驗證安裝
```bash
# 檢查已安裝的包
(venv) $ pip list

# 檢查 DeepEval 相關包
(venv) $ pip show deepeval pandas openai
```

### 5. 運行 DeepEval 演示
```bash
# 在虛擬環境中運行
(venv) $ python3 test/deepeval_demo.py
```

### 6. 退出虛擬環境
```bash
# 當你完成工作後
(venv) $ deactivate
```

## 🔧 一鍵設置腳本

創建 `setup_env.sh` 腳本：
```bash
#!/bin/bash
echo "🐍 設置 Python 虛擬環境..."

# 檢查是否已存在虛擬環境
if [ -d "venv" ]; then
    echo "✅ 虛擬環境已存在"
else
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "🚀 啟動虛擬環境..."
source venv/bin/activate

# 升級 pip
echo "⬆️  升級 pip..."
pip install --upgrade pip

# 安裝依賴
echo "📚 安裝依賴..."
pip install -r requirements.txt

# 檢查配置
echo "🔍 檢查配置..."
python3 check_config.py

echo "🎉 環境設置完成！"
echo "現在你可以運行："
echo "  python3 test/deepeval_demo.py"
```

使用方法：
```bash
chmod +x setup_env.sh
./setup_env.sh
```

## 📋 手動步驟總結

如果你需要手動執行，請按以下順序：

1. **創建虛擬環境**：
   ```bash
   python3 -m venv venv
   ```

2. **啟動虛擬環境**：
   ```bash
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安裝依賴**：
   ```bash
   pip install -r requirements.txt
   ```

4. **運行演示**：
   ```bash
   python3 test/deepeval_demo.py
   ```

## 🔍 故障排除

### 問題1: python3 命令不存在
```bash
# 嘗試使用 python
python -m venv venv
```

### 問題2: 虛擬環境啟動失敗
```bash
# 檢查虛擬環境是否正確創建
ls -la venv/

# 重新創建虛擬環境
rm -rf venv
python3 -m venv venv
```

### 問題3: 依賴安裝失敗
```bash
# 升級 pip
pip install --upgrade pip

# 逐個安裝依賴
pip install requests
pip install deepeval
pip install openai
pip install pandas
```

## ✅ 驗證環境

運行以下命令確認環境正確：
```bash
# 檢查 Python 版本
python --version

# 檢查虛擬環境
which python

# 檢查已安裝包
pip list | grep -E "(deepeval|pandas|openai|requests)"
```

預期輸出：
```
deepeval    0.21.x
pandas      2.x.x
openai      1.x.x
requests    2.x.x
```