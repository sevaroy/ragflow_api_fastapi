#!/usr/bin/env python3
"""
DeepEval 配置文件
管理評估系統的各種設置和參數
"""

import os
from typing import Dict, List, Any

class DeepEvalConfig:
    """DeepEval 配置類"""
    
    # API 設置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # 評估指標閾值
    METRIC_THRESHOLDS = {
        'answer_relevancy': 0.7,
        'faithfulness': 0.7,
        'contextual_precision': 0.7,
        'contextual_recall': 0.7,
        'hallucination': 0.3,  # 越低越好
        'bias': 0.5
    }
    
    # 分階段評估策略
    EVALUATION_STAGES = {
        'quick': ['answer_relevancy'],  # 快速評估：1個指標
        'standard': ['answer_relevancy', 'faithfulness'],  # 標準評估：2個指標
        'comprehensive': ['answer_relevancy', 'faithfulness', 'hallucination'],  # 全面評估：3個指標
        'full': ['answer_relevancy', 'faithfulness', 'contextual_precision', 'contextual_recall', 'hallucination', 'bias']  # 完整評估：所有指標
    }
    
    # 測試數據生成設置
    DEFAULT_QUESTION_COUNT = 10
    MAX_QUESTION_COUNT = 50
    
    # 法律領域測試問題模板
    LEGAL_QUESTION_TEMPLATES = [
        "什麼是{concept}的基本原則？",
        "{law_area}中的{principle}如何理解？",
        "請解釋{legal_term}的定義和適用範圍",
        "{case_type}案件的處理程序是什麼？",
        "{legal_document}的主要內容包括哪些？"
    ]
    
    # 技術領域測試問題模板
    TECH_QUESTION_TEMPLATES = [
        "什麼是{technology}？",
        "如何實現{feature}功能？",
        "{framework}的主要特點是什麼？",
        "{concept}的工作原理是什麼？",
        "使用{tool}時需要注意什麼？"
    ]
    
    # 通用測試問題模板
    GENERAL_QUESTION_TEMPLATES = [
        "這個主題的核心概念是什麼？",
        "有哪些重要的注意事項？",
        "最佳實踐是什麼？",
        "常見問題有哪些？",
        "如何開始學習這個領域？"
    ]
    
    # 評估報告設置
    REPORT_CONFIG = {
        'include_detailed_scores': True,
        'include_failed_cases': True,
        'max_output_length': 200,
        'export_formats': ['json', 'csv', 'html']
    }
    
    # 法律專業詞彙
    LEGAL_CONCEPTS = [
        "憲法", "行政法", "民法", "刑法", "商法",
        "契約自由", "罪刑法定", "比例原則", "信賴保護",
        "基本人權", "權力分立", "法治國家"
    ]
    
    LEGAL_TERMS = [
        "法律行為", "物權", "債權", "親屬關係", "繼承",
        "犯罪構成要件", "刑罰", "緩刑", "假釋",
        "行政處分", "行政救濟", "國家賠償"
    ]
    
    # 技術專業詞彙
    TECH_CONCEPTS = [
        "API", "REST", "GraphQL", "微服務", "容器化",
        "機器學習", "深度學習", "自然語言處理",
        "區塊鏈", "雲端運算", "DevOps"
    ]
    
    @classmethod
    def get_question_templates(cls, domain: str) -> List[str]:
        """根據領域獲取問題模板"""
        if "法律" in domain or "legal" in domain.lower():
            return cls.LEGAL_QUESTION_TEMPLATES
        elif "技術" in domain or "tech" in domain.lower():
            return cls.TECH_QUESTION_TEMPLATES
        else:
            return cls.GENERAL_QUESTION_TEMPLATES
    
    @classmethod
    def get_domain_concepts(cls, domain: str) -> List[str]:
        """根據領域獲取專業概念"""
        if "法律" in domain or "legal" in domain.lower():
            return cls.LEGAL_CONCEPTS + cls.LEGAL_TERMS
        elif "技術" in domain or "tech" in domain.lower():
            return cls.TECH_CONCEPTS
        else:
            return ["核心概念", "基本原理", "實務應用", "最佳實踐"]
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """驗證配置設置"""
        issues = []
        warnings = []
        
        # 檢查 OpenAI API 密鑰
        if not cls.OPENAI_API_KEY:
            warnings.append("未設置 OPENAI_API_KEY，某些高級功能將無法使用")
        
        # 檢查閾值設置
        for metric, threshold in cls.METRIC_THRESHOLDS.items():
            if not 0 <= threshold <= 1:
                issues.append(f"指標 {metric} 的閾值 {threshold} 不在有效範圍 [0, 1] 內")
        
        # 檢查問題數量設置
        if cls.DEFAULT_QUESTION_COUNT > cls.MAX_QUESTION_COUNT:
            issues.append("預設問題數量不能超過最大問題數量")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    @classmethod
    def print_config_status(cls):
        """打印配置狀態"""
        print("⚙️  DeepEval 配置狀態")
        print("-" * 30)
        
        validation = cls.validate_config()
        
        if validation['valid']:
            print("✅ 配置驗證通過")
        else:
            print("❌ 配置存在問題:")
            for issue in validation['issues']:
                print(f"   - {issue}")
        
        if validation['warnings']:
            print("⚠️  警告:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
        
        print(f"\n📊 評估設置:")
        print(f"   - 預設問題數量: {cls.DEFAULT_QUESTION_COUNT}")
        print(f"   - 最大問題數量: {cls.MAX_QUESTION_COUNT}")
        print(f"   - OpenAI 模型: {cls.OPENAI_MODEL}")
        
        print(f"\n🎯 指標閾值:")
        for metric, threshold in cls.METRIC_THRESHOLDS.items():
            print(f"   - {metric}: {threshold}")

def main():
    """主函數 - 顯示配置狀態"""
    DeepEvalConfig.print_config_status()

if __name__ == "__main__":
    main()