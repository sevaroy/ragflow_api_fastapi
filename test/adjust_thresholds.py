#!/usr/bin/env python3
"""
DeepEval 閾值調整工具
提供互動式的閾值調整和測試功能
"""

import json
import os
from typing import Dict, Any
from deepeval_config import DeepEvalConfig

class ThresholdAdjuster:
    """閾值調整器"""
    
    def __init__(self):
        self.current_thresholds = DeepEvalConfig.METRIC_THRESHOLDS.copy()
        self.preset_configs = {
            'development': {
                'answer_relevancy': 0.6,
                'faithfulness': 0.6,
                'contextual_precision': 0.6,
                'contextual_recall': 0.6,
                'hallucination': 0.4,
                'bias': 0.6
            },
            'production': {
                'answer_relevancy': 0.8,
                'faithfulness': 0.8,
                'contextual_precision': 0.8,
                'contextual_recall': 0.7,
                'hallucination': 0.2,
                'bias': 0.3
            },
            'legal_strict': {
                'answer_relevancy': 0.8,
                'faithfulness': 0.9,
                'contextual_precision': 0.8,
                'contextual_recall': 0.7,
                'hallucination': 0.1,
                'bias': 0.2
            },
            'relaxed': {
                'answer_relevancy': 0.5,
                'faithfulness': 0.5,
                'contextual_precision': 0.5,
                'contextual_recall': 0.5,
                'hallucination': 0.5,
                'bias': 0.7
            }
        }
    
    def display_current_thresholds(self):
        """顯示當前閾值"""
        print("📊 當前評估閾值:")
        print("=" * 50)
        
        for metric, threshold in self.current_thresholds.items():
            status = self._get_threshold_status(metric, threshold)
            print(f"  {metric:20} : {threshold:4.1f} {status}")
        
        print()
    
    def _get_threshold_status(self, metric: str, threshold: float) -> str:
        """獲取閾值狀態標示"""
        if metric in ['hallucination', 'bias']:
            # 這些指標越低越好
            if threshold <= 0.2:
                return "🟢 (嚴格)"
            elif threshold <= 0.4:
                return "🟡 (中等)"
            else:
                return "🔴 (寬鬆)"
        else:
            # 其他指標越高越好
            if threshold >= 0.8:
                return "🟢 (嚴格)"
            elif threshold >= 0.6:
                return "🟡 (中等)"
            else:
                return "🔴 (寬鬆)"
    
    def show_preset_configs(self):
        """顯示預設配置"""
        print("🎯 預設配置選項:")
        print("=" * 50)
        
        for name, config in self.preset_configs.items():
            print(f"\n📋 {name.upper()}:")
            for metric, threshold in config.items():
                status = self._get_threshold_status(metric, threshold)
                print(f"  {metric:20} : {threshold:4.1f} {status}")
    
    def apply_preset_config(self, config_name: str) -> bool:
        """應用預設配置"""
        if config_name in self.preset_configs:
            self.current_thresholds = self.preset_configs[config_name].copy()
            print(f"✅ 已應用 {config_name.upper()} 配置")
            return True
        else:
            print(f"❌ 配置 {config_name} 不存在")
            return False
    
    def adjust_single_threshold(self, metric: str, value: float) -> bool:
        """調整單個閾值"""
        if metric not in self.current_thresholds:
            print(f"❌ 指標 {metric} 不存在")
            return False
        
        if not 0 <= value <= 1:
            print(f"❌ 閾值必須在 0-1 之間")
            return False
        
        old_value = self.current_thresholds[metric]
        self.current_thresholds[metric] = value
        
        print(f"✅ {metric}: {old_value:.1f} → {value:.1f}")
        return True
    
    def interactive_adjustment(self):
        """互動式閾值調整"""
        print("🔧 互動式閾值調整")
        print("=" * 50)
        
        while True:
            self.display_current_thresholds()
            
            print("選項:")
            print("  1. 調整單個指標")
            print("  2. 應用預設配置")
            print("  3. 保存當前配置")
            print("  4. 測試當前配置")
            print("  5. 重置為預設值")
            print("  6. 退出")
            
            try:
                choice = input("\n請選擇 [1-6]: ").strip()
                
                if choice == '1':
                    self._adjust_single_metric()
                elif choice == '2':
                    self._apply_preset()
                elif choice == '3':
                    self._save_config()
                elif choice == '4':
                    self._test_config()
                elif choice == '5':
                    self._reset_config()
                elif choice == '6':
                    print("👋 退出閾值調整")
                    break
                else:
                    print("❌ 無效選擇")
                    
            except KeyboardInterrupt:
                print("\n👋 退出閾值調整")
                break
    
    def _adjust_single_metric(self):
        """調整單個指標"""
        print("\n📊 可調整的指標:")
        metrics = list(self.current_thresholds.keys())
        
        for i, metric in enumerate(metrics, 1):
            current = self.current_thresholds[metric]
            print(f"  {i}. {metric:20} (當前: {current:.1f})")
        
        try:
            choice = int(input(f"\n選擇指標 [1-{len(metrics)}]: ")) - 1
            if 0 <= choice < len(metrics):
                metric = metrics[choice]
                current = self.current_thresholds[metric]
                
                print(f"\n調整 {metric} (當前: {current:.1f})")
                
                # 提供建議值
                if metric in ['hallucination', 'bias']:
                    print("建議值: 0.1 (嚴格), 0.3 (中等), 0.5 (寬鬆)")
                else:
                    print("建議值: 0.9 (嚴格), 0.7 (中等), 0.5 (寬鬆)")
                
                new_value = float(input("新值 [0.0-1.0]: "))
                self.adjust_single_threshold(metric, new_value)
            else:
                print("❌ 無效選擇")
        except (ValueError, IndexError):
            print("❌ 輸入錯誤")
    
    def _apply_preset(self):
        """應用預設配置"""
        print("\n🎯 預設配置:")
        configs = list(self.preset_configs.keys())
        
        for i, config in enumerate(configs, 1):
            print(f"  {i}. {config}")
        
        try:
            choice = int(input(f"\n選擇配置 [1-{len(configs)}]: ")) - 1
            if 0 <= choice < len(configs):
                config_name = configs[choice]
                self.apply_preset_config(config_name)
            else:
                print("❌ 無效選擇")
        except (ValueError, IndexError):
            print("❌ 輸入錯誤")
    
    def _save_config(self):
        """保存配置"""
        filename = input("配置文件名 (預設: custom_thresholds.json): ").strip()
        if not filename:
            filename = "custom_thresholds.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'thresholds': self.current_thresholds,
                    'description': '自定義閾值配置',
                    'created_at': str(os.popen('date').read().strip())
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存失敗: {e}")
    
    def _test_config(self):
        """測試當前配置"""
        print("\n🧪 測試當前配置...")
        
        try:
            from deepeval_integration import RAGFlowEvaluator
            
            # 創建評估器並應用當前閾值
            evaluator = RAGFlowEvaluator()
            
            # 更新評估器的閾值
            for metric_name, threshold in self.current_thresholds.items():
                if metric_name in evaluator.metrics:
                    evaluator.metrics[metric_name].threshold = threshold
            
            print("✅ 閾值已應用到評估器")
            print("💡 你可以運行 python3 test/deepeval_demo.py 來測試效果")
            
        except Exception as e:
            print(f"❌ 測試配置失敗: {e}")
    
    def _reset_config(self):
        """重置配置"""
        self.current_thresholds = DeepEvalConfig.METRIC_THRESHOLDS.copy()
        print("✅ 已重置為預設配置")
    
    def load_config_from_file(self, filename: str) -> bool:
        """從文件載入配置"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'thresholds' in data:
                self.current_thresholds = data['thresholds']
                print(f"✅ 已載入配置: {filename}")
                return True
            else:
                print(f"❌ 配置文件格式錯誤: {filename}")
                return False
                
        except Exception as e:
            print(f"❌ 載入配置失敗: {e}")
            return False
    
    def compare_configs(self, config1: Dict[str, float], config2: Dict[str, float]):
        """比較兩個配置"""
        print("📊 配置比較:")
        print("=" * 60)
        print(f"{'指標':20} {'配置1':>8} {'配置2':>8} {'差異':>8}")
        print("-" * 60)
        
        for metric in config1.keys():
            val1 = config1.get(metric, 0)
            val2 = config2.get(metric, 0)
            diff = val2 - val1
            
            diff_str = f"{diff:+.1f}"
            if diff > 0:
                diff_str = f"🔺{diff_str}"
            elif diff < 0:
                diff_str = f"🔻{diff_str}"
            else:
                diff_str = "➖ 0.0"
            
            print(f"{metric:20} {val1:8.1f} {val2:8.1f} {diff_str:>8}")

def main():
    """主函數"""
    print("🔧 DeepEval 閾值調整工具")
    print("=" * 50)
    
    adjuster = ThresholdAdjuster()
    
    print("當前配置:")
    adjuster.display_current_thresholds()
    
    print("可用操作:")
    print("  1. 互動式調整")
    print("  2. 查看預設配置")
    print("  3. 載入配置文件")
    print("  4. 退出")
    
    while True:
        try:
            choice = input("\n請選擇 [1-4]: ").strip()
            
            if choice == '1':
                adjuster.interactive_adjustment()
                break
            elif choice == '2':
                adjuster.show_preset_configs()
            elif choice == '3':
                filename = input("配置文件路徑: ").strip()
                if filename:
                    adjuster.load_config_from_file(filename)
            elif choice == '4':
                print("👋 再見！")
                break
            else:
                print("❌ 無效選擇")
                
        except KeyboardInterrupt:
            print("\n👋 程序被中斷")
            break

if __name__ == "__main__":
    main()