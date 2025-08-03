#!/usr/bin/env python3
"""
DeepEval 設置和測試腳本
自動安裝依賴並運行基本測試
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """安裝必要的依賴"""
    print("📦 安裝 DeepEval 相關依賴...")
    
    try:
        # 安裝 requirements.txt 中的依賴
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依賴安裝成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依賴安裝失敗: {e}")
        return False

def check_environment():
    """檢查環境配置"""
    print("\n🔍 檢查環境配置...")
    
    issues = []
    warnings = []
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        issues.append("Python 版本需要 3.7 或更高")
    else:
        print(f"✅ Python 版本: {sys.version}")
    
    # 檢查 RAGFlow 配置
    try:
        from config import RAGFLOW_API_URL, RAGFLOW_API_KEY
        if not RAGFLOW_API_URL:
            issues.append("RAGFLOW_API_URL 未設置")
        else:
            print(f"✅ RAGFlow API URL: {RAGFLOW_API_URL}")
        
        if not RAGFLOW_API_KEY:
            issues.append("RAGFLOW_API_KEY 未設置")
        else:
            print("✅ RAGFlow API Key: 已設置")
    except ImportError:
        issues.append("無法導入 config.py")
    
    # 檢查 OpenAI API 密鑰
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        warnings.append("OPENAI_API_KEY 未設置，某些高級評估功能將無法使用")
        print("⚠️  OpenAI API Key: 未設置")
        print("   💡 設置方法: export OPENAI_API_KEY='your-api-key'")
        print("   📖 詳細指南: OPENAI_CONFIG_GUIDE.md")
    else:
        masked_key = f"{openai_key[:8]}...{openai_key[-4:]}"
        print(f"✅ OpenAI API Key: {masked_key}")
        
        # 檢查 OpenAI 模型設置
        openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        print(f"✅ OpenAI Model: {openai_model}")
    
    # 檢查必要文件
    required_files = [
        "deepeval_integration.py",
        "deepeval_config.py",
        "test/deepeval_demo.py",
        "test/run_deepeval_test.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"缺少必要文件: {file_path}")
        else:
            print(f"✅ 文件存在: {file_path}")
    
    return issues, warnings

def test_basic_functionality():
    """測試基本功能"""
    print("\n🧪 測試基本功能...")
    
    try:
        # 測試導入
        from deepeval_integration import RAGFlowEvaluator
        from deepeval_config import DeepEvalConfig
        print("✅ 模組導入成功")
        
        # 測試配置
        validation = DeepEvalConfig.validate_config()
        if validation['valid']:
            print("✅ 配置驗證通過")
        else:
            print("⚠️  配置存在問題:")
            for issue in validation['issues']:
                print(f"   - {issue}")
        
        # 測試 RAGFlow 連接
        evaluator = RAGFlowEvaluator()
        datasets_result = evaluator.client.list_datasets()
        
        if datasets_result['success']:
            datasets = datasets_result['data']
            print(f"✅ RAGFlow 連接成功，找到 {len(datasets)} 個數據集")
            
            if datasets:
                print("📚 可用數據集:")
                for i, dataset in enumerate(datasets[:3], 1):
                    print(f"   {i}. {dataset.get('name', 'N/A')}")
                if len(datasets) > 3:
                    print(f"   ... 還有 {len(datasets) - 3} 個數據集")
            else:
                print("⚠️  沒有可用的數據集")
        else:
            print(f"❌ RAGFlow 連接失敗: {datasets_result['message']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能測試失敗: {e}")
        return False

def run_quick_demo():
    """運行快速演示"""
    print("\n🚀 運行快速演示...")
    
    try:
        # 運行演示腳本
        result = subprocess.run([
            sys.executable, "test/deepeval_demo.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 快速演示運行成功")
            print("📋 演示輸出:")
            print(result.stdout)
            return True
        else:
            print("❌ 快速演示運行失敗")
            print("錯誤輸出:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 演示運行超時")
        return False
    except Exception as e:
        print(f"❌ 演示運行異常: {e}")
        return False

def create_sample_config():
    """創建示例配置文件"""
    print("\n📝 創建示例配置...")
    
    sample_env = """# DeepEval 環境配置示例
# 複製此文件為 .env 並填入實際值

# RAGFlow API 配置 (必需)
RAGFLOW_API_URL=http://your-ragflow-server:8080
RAGFLOW_API_KEY=your-ragflow-api-key

# OpenAI API 配置 (可選，用於高級評估功能)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# 評估配置
DEFAULT_QUESTION_COUNT=10
MAX_QUESTION_COUNT=50
"""
    
    try:
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(sample_env)
        print("✅ 示例配置文件已創建: .env.example")
        print("   請複製為 .env 並填入實際配置值")
        return True
    except Exception as e:
        print(f"❌ 創建配置文件失敗: {e}")
        return False

def main():
    """主函數"""
    print("🔧 DeepEval 設置和測試工具")
    print("=" * 50)
    
    # 安裝依賴
    if not install_dependencies():
        print("❌ 依賴安裝失敗，請手動安裝")
        return
    
    # 檢查環境
    issues, warnings = check_environment()
    
    if issues:
        print("\n❌ 發現以下問題:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n請解決這些問題後重新運行")
        return
    
    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"   - {warning}")
    
    # 測試基本功能
    if not test_basic_functionality():
        print("\n❌ 基本功能測試失敗")
        print("請檢查 RAGFlow API 配置")
        return
    
    # 創建示例配置
    create_sample_config()
    
    # 詢問是否運行演示
    try:
        run_demo = input("\n是否運行快速演示？[y/N]: ").strip().lower()
        if run_demo in ['y', 'yes']:
            run_quick_demo()
    except KeyboardInterrupt:
        print("\n👋 設置被中斷")
        return
    
    print("\n🎉 DeepEval 設置完成！")
    print("\n📚 接下來你可以:")
    print("   1. 運行快速演示: python3 test/deepeval_demo.py")
    print("   2. 運行完整評估: python3 test/run_deepeval_test.py")
    print("   3. 使用評估模組: python3 deepeval_integration.py")
    print("   4. 查看使用指南: cat DEEPEVAL_GUIDE.md")

if __name__ == "__main__":
    main()