#!/usr/bin/env python3
"""
RAGFlow 整合應用啟動腳本
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """檢查依賴項"""
    print("🔍 檢查依賴項...")
    
    required_packages = [
        'streamlit',
        'requests', 
        'pandas',
        'plotly',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安裝")
            missing_packages.append(package)
    
    # 檢查 RAGAS（可選）
    try:
        import ragas
        print("✅ ragas - 已安裝")
    except ImportError:
        print("❌ ragas - 未安裝（評估功能將不可用）")
        print("   安裝命令: pip install ragas")
    
    if missing_packages:
        print(f"\n❌ 缺少以下依賴項: {', '.join(missing_packages)}")
        print("請運行以下命令安裝:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ 所有核心依賴項已安裝")
    return True

def check_files():
    """檢查必要文件"""
    print("\n🔍 檢查必要文件...")
    
    required_files = [
        'integrated_ragflow_app.py',
        'ragas_evaluator.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 文件不存在")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少以下文件: {', '.join(missing_files)}")
        return False
    
    print("\n✅ 所有必要文件存在")
    return True

def start_fastapi_server():
    """啟動 FastAPI 服務器（如果存在）"""
    if os.path.exists('fastapi_server.py'):
        print("\n🚀 嘗試啟動 FastAPI 服務器...")
        try:
            # 在後台啟動 FastAPI 服務器
            subprocess.Popen([
                sys.executable, 'fastapi_server.py'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ FastAPI 服務器已在後台啟動")
            return True
        except Exception as e:
            print(f"⚠️ 無法啟動 FastAPI 服務器: {e}")
            print("請手動運行: python fastapi_server.py")
            return False
    else:
        print("⚠️ 未找到 fastapi_server.py，請確保 FastAPI 服務器正在運行")
        return False

def start_streamlit_app():
    """啟動 Streamlit 應用"""
    print("\n🚀 啟動 RAGFlow 整合應用...")
    
    try:
        # 設置 Streamlit 配置
        env = os.environ.copy()
        env['STREAMLIT_SERVER_PORT'] = '8501'
        env['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
        
        # 啟動 Streamlit 應用
        cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'integrated_ragflow_app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0',
            '--theme.primaryColor', '#667eea'
        ]
        
        print("📱 應用將在 http://localhost:8501 啟動")
        print("🔗 FastAPI 文檔: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止應用")
        
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n👋 應用已停止")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")

def show_help():
    """顯示幫助信息"""
    print("""
🤖 RAGFlow 整合應用啟動器

用法:
    python run_integrated_app.py [選項]

選項:
    --help, -h          顯示此幫助信息
    --check-only        僅檢查依賴項和文件，不啟動應用
    --no-fastapi        不嘗試啟動 FastAPI 服務器
    --port PORT         指定 Streamlit 端口 (預設: 8501)

功能說明:
    📱 整合聊天界面    - 與 RAGFlow 後端進行對話
    📊 RAGAS 評估     - 系統性能評估和分析  
    📈 結果分析       - 評估結果視覺化
    ⚙️ 系統設置       - 配置和管理

注意事項:
    1. 確保 FastAPI 服務器在 http://localhost:8000 運行
    2. 如需使用真實 RAGAS 評估，請安裝: pip install ragas
    3. 建議在虛擬環境中運行此應用

更多信息請查看 README.md 或項目文檔。
""")

def main():
    """主函數"""
    # 解析命令行參數
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    print("🤖 RAGFlow 整合應用啟動器")
    print("=" * 50)
    
    # 檢查依賴項
    if not check_dependencies():
        print("\n❌ 依賴項檢查失敗，請安裝缺少的包後重試")
        return
    
    # 檢查文件
    if not check_files():
        print("\n❌ 文件檢查失敗，請確保所有必要文件存在")
        return
    
    if '--check-only' in args:
        print("\n✅ 檢查完成，所有依賴項和文件都已就緒")
        return
    
    # 啟動 FastAPI 服務器（如果需要）
    if '--no-fastapi' not in args:
        start_fastapi_server()
        
        # 等待服務器啟動
        import time
        print("⏳ 等待 FastAPI 服務器啟動...")
        time.sleep(3)
    
    # 啟動 Streamlit 應用
    start_streamlit_app()

if __name__ == "__main__":
    main()