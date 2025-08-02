#!/usr/bin/env python3
"""
全棧啟動腳本
同時啟動 FastAPI 後端和 Streamlit 前端
"""

import subprocess
import sys
import time
import signal
import os
from threading import Thread
import requests

class FullStackRunner:
    def __init__(self):
        self.fastapi_process = None
        self.streamlit_process = None
        self.running = True
    
    def check_port(self, port: int, max_attempts: int = 30) -> bool:
        """檢查端口是否可用"""
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"http://localhost:{port}", timeout=1)
                return True
            except:
                time.sleep(1)
                print(f"等待端口 {port} 啟動... ({attempt + 1}/{max_attempts})")
        return False
    
    def start_fastapi(self):
        """啟動 FastAPI 後端"""
        print("🚀 啟動 FastAPI 後端服務...")
        try:
            self.fastapi_process = subprocess.Popen([
                sys.executable, "fastapi_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待 FastAPI 啟動
            if self.check_port(8000):
                print("✅ FastAPI 後端啟動成功 (http://localhost:8000)")
                return True
            else:
                print("❌ FastAPI 後端啟動失敗")
                return False
        except Exception as e:
            print(f"❌ 啟動 FastAPI 失敗: {e}")
            return False
    
    def start_streamlit(self):
        """啟動 Streamlit 前端"""
        print("🌐 啟動 Streamlit 前端...")
        try:
            self.streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待 Streamlit 啟動
            if self.check_port(8501):
                print("✅ Streamlit 前端啟動成功 (http://localhost:8501)")
                return True
            else:
                print("❌ Streamlit 前端啟動失敗")
                return False
        except Exception as e:
            print(f"❌ 啟動 Streamlit 失敗: {e}")
            return False
    
    def stop_services(self):
        """停止所有服務"""
        print("\n🛑 正在停止服務...")
        self.running = False
        
        if self.fastapi_process:
            self.fastapi_process.terminate()
            try:
                self.fastapi_process.wait(timeout=5)
                print("✅ FastAPI 服務已停止")
            except subprocess.TimeoutExpired:
                self.fastapi_process.kill()
                print("🔥 強制停止 FastAPI 服務")
        
        if self.streamlit_process:
            self.streamlit_process.terminate()
            try:
                self.streamlit_process.wait(timeout=5)
                print("✅ Streamlit 服務已停止")
            except subprocess.TimeoutExpired:
                self.streamlit_process.kill()
                print("🔥 強制停止 Streamlit 服務")
    
    def monitor_processes(self):
        """監控進程狀態"""
        while self.running:
            time.sleep(5)
            
            # 檢查 FastAPI 進程
            if self.fastapi_process and self.fastapi_process.poll() is not None:
                print("⚠️ FastAPI 進程意外退出")
                break
            
            # 檢查 Streamlit 進程
            if self.streamlit_process and self.streamlit_process.poll() is not None:
                print("⚠️ Streamlit 進程意外退出")
                break
    
    def run(self):
        """運行全棧應用"""
        print("🎯 RAGFlow 全棧聊天機器人啟動器")
        print("=" * 50)
        
        # 檢查依賴
        try:
            import streamlit
            import fastapi
            import uvicorn
        except ImportError as e:
            print(f"❌ 缺少依賴: {e}")
            print("請運行: pip install -r requirements.txt")
            return
        
        # 檢查配置文件
        if not os.path.exists("config.py"):
            print("❌ 找不到 config.py 配置文件")
            return
        
        if not os.path.exists("fastapi_server.py"):
            print("❌ 找不到 fastapi_server.py")
            return
        
        if not os.path.exists("streamlit_app.py"):
            print("❌ 找不到 streamlit_app.py")
            return
        
        try:
            # 啟動 FastAPI 後端
            if not self.start_fastapi():
                return
            
            time.sleep(2)  # 等待 FastAPI 完全啟動
            
            # 啟動 Streamlit 前端
            if not self.start_streamlit():
                self.stop_services()
                return
            
            print("\n" + "=" * 50)
            print("🎉 全棧應用啟動成功！")
            print("📡 FastAPI 後端: http://localhost:8000")
            print("   - API 文檔: http://localhost:8000/docs")
            print("   - ReDoc 文檔: http://localhost:8000/redoc")
            print("🌐 Streamlit 前端: http://localhost:8501")
            print("=" * 50)
            print("按 Ctrl+C 停止服務")
            
            # 監控進程
            monitor_thread = Thread(target=self.monitor_processes)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # 等待中斷信號
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n收到中斷信號...")
            
        except Exception as e:
            print(f"❌ 運行過程中發生錯誤: {e}")
        finally:
            self.stop_services()

def signal_handler(signum, frame):
    """信號處理器"""
    print("\n收到停止信號...")
    sys.exit(0)

def main():
    """主函數"""
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 創建並運行全棧應用
    runner = FullStackRunner()
    runner.run()

if __name__ == "__main__":
    main()