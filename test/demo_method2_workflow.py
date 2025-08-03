#!/usr/bin/env python3
"""
方法2 運作方式演示
詳細展示示例數據生成和儀表板啟動的完整流程
"""

import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def step1_generate_sample_data():
    """步驟1: 生成示例數據的詳細過程"""
    print("🎯 步驟1: 生成示例 DeepEval 數據")
    print("=" * 50)
    
    print("📝 這個步驟會做什麼:")
    print("   1. 創建法律相關的測試問題")
    print("   2. 生成對應的標準答案")
    print("   3. 模擬 AI 系統的實際回答")
    print("   4. 計算各項評估指標分數")
    print("   5. 判斷每個案例是否通過閾值")
    print("   6. 保存為 JSON 格式文件")
    
    print("\n🔧 數據生成邏輯:")
    print("   • 問題庫: 15個法律專業問題")
    print("   • 答案庫: 5個標準法律答案")
    print("   • 評估指標: 6個核心指標")
    print("   • 分數範圍: 0.1 - 0.99")
    print("   • 通過標準: 基於預設閾值")
    
    # 實際執行數據生成
    print("\n🚀 開始生成數據...")
    
    try:
        # 導入生成函數
        from generate_sample_data import generate_sample_evaluation_data, generate_summary_data
        
        # 生成20個測試案例
        num_cases = 20
        print(f"📊 生成 {num_cases} 個測試案例...")
        
        results = generate_sample_evaluation_data(num_cases)
        summary = generate_summary_data(results)
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"demo_evaluation_results_{timestamp}.json"
        summary_file = f"demo_evaluation_summary_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 詳細結果: {results_file}")
        print(f"✅ 摘要數據: {summary_file}")
        
        # 顯示生成的數據統計
        passed_count = sum(1 for r in results if r['passed'])
        pass_rate = passed_count / num_cases * 100
        avg_score = sum(r['overall_score'] for r in results) / num_cases
        
        print(f"\n📈 生成數據統計:")
        print(f"   總案例數: {num_cases}")
        print(f"   通過案例: {passed_count}")
        print(f"   通過率: {pass_rate:.1f}%")
        print(f"   平均分數: {avg_score:.3f}")
        
        # 顯示示例數據結構
        print(f"\n📋 數據結構示例:")
        example = results[0]
        print(f"   測試ID: {example['test_case_id']}")
        print(f"   問題: {example['question'][:50]}...")
        print(f"   整體分數: {example['overall_score']}")
        print(f"   是否通過: {example['passed']}")
        print(f"   指標數量: {len(example['metrics_scores'])}")
        
        return results_file, summary_file
        
    except Exception as e:
        print(f"❌ 數據生成失敗: {e}")
        return None, None

def step2_analyze_generated_data(results_file):
    """步驟2: 分析生成的數據"""
    print("\n🔍 步驟2: 分析生成的數據")
    print("=" * 50)
    
    if not results_file or not os.path.exists(results_file):
        print("❌ 沒有找到生成的數據文件")
        return
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 數據文件分析: {results_file}")
        print(f"   文件大小: {os.path.getsize(results_file)} bytes")
        print(f"   數據條目: {len(data)} 個")
        
        # 分析指標分布
        metrics = ['answer_relevancy', 'faithfulness', 'contextual_precision', 
                  'contextual_recall', 'hallucination', 'bias']
        
        print(f"\n📋 指標分數分布:")
        for metric in metrics:
            scores = [item['metrics_scores'][metric] for item in data if metric in item['metrics_scores']]
            if scores:
                avg_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                print(f"   {metric:20}: 平均 {avg_score:.3f} (範圍: {min_score:.3f} - {max_score:.3f})")
        
        # 分析通過/失敗分布
        passed_cases = [item for item in data if item['passed']]
        failed_cases = [item for item in data if not item['passed']]
        
        print(f"\n✅ 通過案例分析:")
        if passed_cases:
            avg_passed_score = sum(item['overall_score'] for item in passed_cases) / len(passed_cases)
            print(f"   數量: {len(passed_cases)}")
            print(f"   平均分數: {avg_passed_score:.3f}")
        
        print(f"\n❌ 失敗案例分析:")
        if failed_cases:
            avg_failed_score = sum(item['overall_score'] for item in failed_cases) / len(failed_cases)
            print(f"   數量: {len(failed_cases)}")
            print(f"   平均分數: {avg_failed_score:.3f}")
            
            # 顯示失敗原因
            print(f"   主要失敗原因:")
            for item in failed_cases[:3]:  # 顯示前3個失敗案例
                failing_metrics = []
                for metric, score in item['metrics_scores'].items():
                    if metric in ['hallucination', 'bias']:
                        if score > 0.3:  # 負向指標閾值
                            failing_metrics.append(f"{metric}({score:.3f})")
                    else:
                        if score < 0.7:  # 正向指標閾值
                            failing_metrics.append(f"{metric}({score:.3f})")
                
                if failing_metrics:
                    print(f"     {item['test_case_id']}: {', '.join(failing_metrics)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據分析失敗: {e}")
        return False

def step3_prepare_dashboard():
    """步驟3: 準備儀表板環境"""
    print("\n🛠️ 步驟3: 準備儀表板環境")
    print("=" * 50)
    
    print("🔍 檢查依賴包...")
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 需要安裝缺少的依賴: {', '.join(missing_packages)}")
        install_choice = input("是否現在安裝? [y/N]: ").strip().lower()
        
        if install_choice in ['y', 'yes']:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install"
                ] + missing_packages)
                print("✅ 依賴安裝成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ 依賴安裝失敗: {e}")
                return False
        else:
            print("⚠️ 跳過依賴安裝，儀表板可能無法正常運行")
    
    # 檢查儀表板文件
    print(f"\n📁 檢查儀表板文件...")
    dashboard_files = [
        'deepeval_dashboard.py',
        'run_dashboard.py'
    ]
    
    for file in dashboard_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - 文件不存在")
            return False
    
    print("✅ 儀表板環境準備完成")
    return True

def step4_launch_dashboard():
    """步驟4: 啟動儀表板"""
    print("\n🚀 步驟4: 啟動 Streamlit 儀表板")
    print("=" * 50)
    
    print("🌐 儀表板啟動信息:")
    print("   URL: http://localhost:8501")
    print("   功能: DeepEval 評估結果視覺化")
    print("   操作: 在側邊欄載入生成的 JSON 文件")
    
    print(f"\n📋 可載入的文件:")
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'evaluation' in f]
    for i, file in enumerate(json_files, 1):
        file_size = os.path.getsize(file)
        print(f"   {i}. {file} ({file_size} bytes)")
    
    print(f"\n💡 使用提示:")
    print("   1. 儀表板啟動後，在側邊欄選擇 JSON 文件")
    print("   2. 查看整體表現摘要")
    print("   3. 分析評估指標詳情")
    print("   4. 瀏覽詳細評估結果")
    print("   5. 導出分析報告")
    
    launch_choice = input("\n是否現在啟動儀表板? [y/N]: ").strip().lower()
    
    if launch_choice in ['y', 'yes']:
        print("🚀 正在啟動儀表板...")
        print("   按 Ctrl+C 停止服務")
        print("-" * 50)
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "deepeval_dashboard.py",
                "--server.port", "8501",
                "--server.address", "localhost"
            ])
        except KeyboardInterrupt:
            print("\n👋 儀表板已停止")
        except Exception as e:
            print(f"❌ 啟動失敗: {e}")
    else:
        print("💡 你可以稍後手動啟動:")
        print("   python3 run_dashboard.py")
        print("   或")
        print("   streamlit run deepeval_dashboard.py")

def main():
    """主函數 - 完整演示方法2的運作方式"""
    print("🎯 方法2 運作方式完整演示")
    print("=" * 60)
    print("這個演示將展示如何:")
    print("1. 生成示例 DeepEval 數據")
    print("2. 分析生成的數據結構")
    print("3. 準備儀表板環境")
    print("4. 啟動 Streamlit 儀表板")
    print("=" * 60)
    
    # 步驟1: 生成示例數據
    results_file, summary_file = step1_generate_sample_data()
    
    if not results_file:
        print("❌ 數據生成失敗，無法繼續")
        return
    
    # 步驟2: 分析生成的數據
    if not step2_analyze_generated_data(results_file):
        print("⚠️ 數據分析失敗，但可以繼續")
    
    # 步驟3: 準備儀表板環境
    if not step3_prepare_dashboard():
        print("❌ 儀表板環境準備失敗")
        return
    
    # 步驟4: 啟動儀表板
    step4_launch_dashboard()
    
    print(f"\n🎉 方法2 演示完成！")
    print(f"📁 生成的文件:")
    print(f"   - {results_file}")
    print(f"   - {summary_file}")

if __name__ == "__main__":
    main()