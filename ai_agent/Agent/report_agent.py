# -*- coding: utf-8 -*-
"""
租房报告生成Agent
用于整合用户需求、房源信息、分析结果，生成综合性的租房报告
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

API_KEY = os.getenv("API_KEY_POINT")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-vl-max-latest"

# 报告模板配置
REPORT_TEMPLATES = {
    "executive_summary": {
        "title": "租房需求执行摘要",
        "sections": ["需求概述", "预算分析", "推荐方案", "风险评估"]
    },
    "detailed_analysis": {
        "title": "详细租房分析报告",
        "sections": ["用户画像", "需求分析", "市场调研", "房源推荐", "区域对比", "费用估算", "行动计划"]
    },
    "comparison_report": {
        "title": "房源对比分析报告",
        "sections": ["候选房源", "对比矩阵", "优劣分析", "最终推荐"]
    }
}

class ReportAgent:
    """租房报告生成Agent"""
    
    def __init__(self):
        self.user_data = {}
        self.questionnaire_data = None
        self.main_agent_history = None
        self.inquiry_agent_history = None
        self.property_search_results = []
        self.area_analysis_results = {}
        self.user_preferences = {}
        
    def update_user_data(self, 
                        questionnaire_data=None, 
                        main_agent_history=None,
                        inquiry_agent_history=None,
                        property_search_results=None,
                        area_analysis_results=None):
        """更新用户数据和分析结果"""
        if questionnaire_data is not None:
            self.questionnaire_data = questionnaire_data
            
        if main_agent_history is not None:
            self.main_agent_history = main_agent_history
            
        if inquiry_agent_history is not None:
            self.inquiry_agent_history = inquiry_agent_history
            
        if property_search_results is not None:
            self.property_search_results = property_search_results
            
        if area_analysis_results is not None:
            self.area_analysis_results = area_analysis_results
    
    def _call_qwen_api(self, messages: list) -> str:
        """调用Qwen API"""
        if not API_KEY:
            raise ValueError("API_KEY_POINT not set in environment variables")
        
        client = OpenAI(api_key=API_KEY, base_url=DASHSCOPE_BASE_URL)
        
        # 过滤和转换消息角色，确保API兼容性
        filtered_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # 将非标准角色映射为assistant
            if role in ["inquiry_assistant", "report_assistant"]:
                role = "assistant"
            
            # 只保留API支持的角色
            if role in ["system", "assistant", "user", "tool", "function"]:
                filtered_messages.append({"role": role, "content": content})
        
        try:
            completion = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=filtered_messages,
                temperature=0.3,  # 较低的温度以确保报告的一致性
                max_tokens=4000
            )
            
            return completion.choices[0].message.content or ""
            
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            raise
    
    def _detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text:
            return "chinese"  # 默认中文
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        return "chinese" if chinese_char_count > len(text) * 0.1 else "english"
    
    def _extract_user_preferences(self) -> Dict[str, Any]:
        """从对话历史中提取用户偏好"""
        preferences = {
            "budget_range": None,
            "preferred_areas": [],
            "room_types": [],
            "special_requirements": [],
            "deal_breakers": [],
            "priorities": []
        }
        
        # 从问卷数据提取偏好
        if self.questionnaire_data:
            if self.questionnaire_data.get('budget_min') and self.questionnaire_data.get('budget_max'):
                preferences["budget_range"] = {
                    "min": self.questionnaire_data['budget_min'],
                    "max": self.questionnaire_data['budget_max'],
                    "currency": "AUD"
                }
            
            if self.questionnaire_data.get('room_type'):
                preferences["room_types"].append(self.questionnaire_data['room_type'])
            
            if self.questionnaire_data.get('commute_time'):
                preferences["special_requirements"].append(f"通勤时间: {self.questionnaire_data['commute_time']}")
        
        # 从对话历史提取偏好
        all_conversations = []
        if self.main_agent_history:
            all_conversations.extend(self.main_agent_history)
        if self.inquiry_agent_history:
            all_conversations.extend(self.inquiry_agent_history)
        
        for role, content in all_conversations:
            if role == "user":
                # 简单的关键词提取（可以后续优化为更智能的NLP分析）
                content_lower = content.lower()
                
                # 提取区域偏好
                areas = ['kingsford', 'randwick', 'kensington', 'zetland', 'waterloo', 
                        'eastgarden', 'mascot', 'rosebery', 'unsw', 'university']
                for area in areas:
                    if area in content_lower and area not in preferences["preferred_areas"]:
                        preferences["preferred_areas"].append(area)
                
                # 提取特殊要求
                if any(word in content_lower for word in ['pet', '宠物']):
                    preferences["special_requirements"].append("允许宠物")
                if any(word in content_lower for word in ['parking', '停车']):
                    preferences["special_requirements"].append("停车位")
                if any(word in content_lower for word in ['gym', '健身']):
                    preferences["special_requirements"].append("健身房")
        
        return preferences
    
    def _format_questionnaire_summary(self) -> str:
        """格式化问卷信息摘要"""
        if not self.questionnaire_data:
            return "用户未填写详细问卷信息。"
        
        summary = "## 问卷信息摘要\n\n"
        
        # 预算信息
        budget_info = []
        if self.questionnaire_data.get('budget_min') and self.questionnaire_data.get('budget_max'):
            budget_info.append(f"预算范围: ${self.questionnaire_data['budget_min']}-${self.questionnaire_data['budget_max']}/周")
        if self.questionnaire_data.get('includes_bills'):
            budget_info.append(f"Bills包含情况: {self.questionnaire_data['includes_bills']}")
        if self.questionnaire_data.get('includes_furniture'):
            budget_info.append(f"家具包含情况: {self.questionnaire_data['includes_furniture']}")
        if self.questionnaire_data.get('total_budget'):
            budget_info.append(f"总开销预期: ${self.questionnaire_data['total_budget']}/周")
        
        if budget_info:
            summary += "**预算信息:**\n"
            for info in budget_info:
                summary += f"- {info}\n"
            summary += "\n"
        
        # 房型和偏好
        preference_info = []
        if self.questionnaire_data.get('room_type'):
            preference_info.append(f"目标房型: {self.questionnaire_data['room_type']}")
        if self.questionnaire_data.get('consider_sharing'):
            preference_info.append(f"合租意愿: {self.questionnaire_data['consider_sharing']}")
        if self.questionnaire_data.get('commute_time'):
            preference_info.append(f"通勤时间要求: {self.questionnaire_data['commute_time']}")
        
        if preference_info:
            summary += "**偏好信息:**\n"
            for info in preference_info:
                summary += f"- {info}\n"
            summary += "\n"
        
        # 时间信息
        time_info = []
        if self.questionnaire_data.get('move_in_date'):
            time_info.append(f"入住日期: {self.questionnaire_data['move_in_date']}")
        if self.questionnaire_data.get('lease_duration'):
            time_info.append(f"租期: {self.questionnaire_data['lease_duration']}")
        
        if time_info:
            summary += "**时间安排:**\n"
            for info in time_info:
                summary += f"- {info}\n"
            summary += "\n"
        
        return summary
    
    def _format_search_results_summary(self) -> str:
        """格式化搜索结果摘要"""
        if not self.property_search_results:
            return "暂无房源搜索结果。"
        
        summary = "## 房源搜索结果摘要\n\n"
        
        total_properties = 0
        price_ranges = []
        areas_found = set()
        room_types_found = set()
        
        for result in self.property_search_results:
            if isinstance(result, dict) and "result" in result:
                result_data = result["result"]
                
                if "properties" in result_data:
                    properties = result_data["properties"]
                    total_properties += len(properties)
                    
                    for prop in properties:
                        # 收集价格信息
                        if "pricePerWeek" in prop:
                            price_ranges.append(prop["pricePerWeek"])
                        
                        # 收集区域信息
                        if "suburb" in prop:
                            areas_found.add(prop["suburb"].lower())
                        
                        # 收集房型信息
                        if "bedroomCount" in prop and "bathroomCount" in prop:
                            room_types_found.add(f"{prop['bedroomCount']}室{prop['bathroomCount']}卫")
        
        summary += f"**搜索统计:**\n"
        summary += f"- 总计找到房源: {total_properties}套\n"
        
        if price_ranges:
            min_price = min(price_ranges)
            max_price = max(price_ranges)
            avg_price = sum(price_ranges) / len(price_ranges)
            summary += f"- 价格范围: ${min_price}-${max_price}/周 (平均: ${avg_price:.0f}/周)\n"
        
        if areas_found:
            summary += f"- 涉及区域: {', '.join(sorted(areas_found))}\n"
        
        if room_types_found:
            summary += f"- 房型分布: {', '.join(sorted(room_types_found))}\n"
        
        summary += "\n"
        
        return summary
    
    def _format_area_analysis_summary(self) -> str:
        """格式化区域分析摘要"""
        if not self.area_analysis_results:
            return "暂无区域分析结果。"
        
        summary = "## 区域分析摘要\n\n"
        
        for area, analysis in self.area_analysis_results.items():
            summary += f"**{area.upper()}区域:**\n"
            
            if "total_properties" in analysis:
                summary += f"- 房源总数: {analysis['total_properties']}套\n"
            
            if "room_types" in analysis:
                summary += f"- 房型分布:\n"
                for room_type, stats in analysis["room_types"].items():
                    summary += f"  - {room_type}: {stats['count']}套, 平均${stats['avg_price']}/周\n"
            
            summary += "\n"
        
        return summary
    
    def _create_system_prompt(self, language: str, report_type: str = "detailed_analysis") -> str:
        """创建系统提示词"""
        
        # 获取用户偏好
        user_preferences = self._extract_user_preferences()
        questionnaire_summary = self._format_questionnaire_summary()
        search_summary = self._format_search_results_summary()
        area_summary = self._format_area_analysis_summary()
        
        template = REPORT_TEMPLATES.get(report_type, REPORT_TEMPLATES["detailed_analysis"])
        
        if language == "chinese":
            return f"""
你是一名专业的租房顾问，专门为用户生成全面的租房分析报告。

## 报告类型: {template['title']}

## 用户完整信息:

{questionnaire_summary}

{search_summary}

{area_summary}

## 用户偏好提取:
{json.dumps(user_preferences, ensure_ascii=False, indent=2)}

## 你的任务:
基于以上所有信息，生成一份专业、全面的租房报告，包含以下部分：

{chr(10).join([f"{i+1}. {section}" for i, section in enumerate(template['sections'])])}

## 报告要求:
- 使用中文书写
- 结构清晰，逻辑严谨
- 提供具体数据和分析
- 包含可操作的建议
- 风格专业但易懂
- 长度适中，内容充实
- 包含风险提示和注意事项
- 提供明确的行动步骤

## 输出格式:
请按照markdown格式输出，使用适当的标题层级、列表和表格来组织内容。

## 注意事项:
- 基于实际数据进行分析，不要编造信息
- 突出用户最关心的问题
- 提供多种选择方案
- 考虑预算限制和实际可行性
- 包含时间规划和优先级建议
"""
        else:
            return f"""
You are a professional rental consultant specializing in generating comprehensive rental analysis reports for users.

## Report Type: {template['title']}

## Complete User Information:

{questionnaire_summary}

{search_summary}

{area_summary}

## Extracted User Preferences:
{json.dumps(user_preferences, ensure_ascii=False, indent=2)}

## Your Task:
Based on all the above information, generate a professional and comprehensive rental report including the following sections:

{chr(10).join([f"{i+1}. {section}" for i, section in enumerate(template['sections'])])}

## Report Requirements:
- Write in user's language
- Clear structure and rigorous logic
- Provide specific data and analysis
- Include actionable recommendations
- Professional but understandable style
- Appropriate length with substantial content
- Include risk alerts and precautions
- Provide clear action steps

## Output Format:
Please output in markdown format, using appropriate heading levels, lists, and tables to organize content.

## Important Notes:
- Base analysis on actual data, don't fabricate information
- Highlight user's main concerns
- Provide multiple options
- Consider budget constraints and feasibility
- Include time planning and priority recommendations
"""
    
    def generate_executive_summary(self, language: str = None) -> str:
        """生成执行摘要报告"""
        if language is None:
            # 从问卷或对话历史中检测语言
            sample_text = ""
            if self.questionnaire_data:
                sample_text = str(self.questionnaire_data.values())
            elif self.main_agent_history:
                sample_text = " ".join([content for role, content in self.main_agent_history[-3:] if role == "user"])
            language = self._detect_language(sample_text)
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(language, "executive_summary")},
            {"role": "user", "content": "请生成一份简洁的租房需求执行摘要报告。" if language == "chinese" else "Please generate a concise rental requirements executive summary report."}
        ]
        
        return self._call_qwen_api(messages)
    
    def generate_detailed_report(self, language: str = None) -> str:
        """生成详细分析报告"""
        if language is None:
            # 从问卷或对话历史中检测语言
            sample_text = ""
            if self.questionnaire_data:
                sample_text = str(self.questionnaire_data.values())
            elif self.main_agent_history:
                sample_text = " ".join([content for role, content in self.main_agent_history[-3:] if role == "user"])
            language = self._detect_language(sample_text)
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(language, "detailed_analysis")},
            {"role": "user", "content": "请生成一份全面详细的租房分析报告。" if language == "chinese" else "Please generate a comprehensive detailed rental analysis report."}
        ]
        
        return self._call_qwen_api(messages)
    
    def generate_comparison_report(self, selected_properties: List[Dict] = None, language: str = None) -> str:
        """生成房源对比报告"""
        if language is None:
            # 从问卷或对话历史中检测语言
            sample_text = ""
            if self.questionnaire_data:
                sample_text = str(self.questionnaire_data.values())
            elif self.main_agent_history:
                sample_text = " ".join([content for role, content in self.main_agent_history[-3:] if role == "user"])
            language = self._detect_language(sample_text)
        
        # 准备候选房源信息
        properties_info = ""
        if selected_properties:
            properties_info = "## 候选房源信息:\n\n"
            for i, prop in enumerate(selected_properties, 1):
                properties_info += f"**房源 {i}:**\n"
                properties_info += f"- 地址: {prop.get('addressLine1', '')} {prop.get('addressLine2', '')}\n"
                properties_info += f"- 房型: {prop.get('bedroomCount', 'N/A')}室{prop.get('bathroomCount', 'N/A')}卫\n"
                properties_info += f"- 价格: ${prop.get('pricePerWeek', 'N/A')}/周\n"
                properties_info += f"- 区域: {prop.get('suburb', 'N/A')}\n\n"
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(language, "comparison_report")},
            {"role": "user", "content": f"{properties_info}\n请基于以上房源生成对比分析报告。" if language == "chinese" else f"{properties_info}\nPlease generate a comparison analysis report based on the above properties."}
        ]
        
        return self._call_qwen_api(messages)
    
    def generate_action_plan(self, priority: str = "balanced", language: str = None) -> str:
        """生成行动计划"""
        if language is None:
            # 从问卷或对话历史中检测语言
            sample_text = ""
            if self.questionnaire_data:
                sample_text = str(self.questionnaire_data.values())
            elif self.main_agent_history:
                sample_text = " ".join([content for role, content in self.main_agent_history[-3:] if role == "user"])
            language = self._detect_language(sample_text)
        
        priority_desc = {
            "fast": "快速入住优先",
            "budget": "预算优先", 
            "quality": "房源质量优先",
            "balanced": "均衡考虑"
        }
        
        action_prompt = f"""
请基于用户的完整需求和分析结果，生成一个详细的找房行动计划。

优先级策略: {priority_desc.get(priority, '均衡考虑')}

行动计划应该包括：
1. 时间规划（短期、中期、长期任务）
2. 优先级排序
3. 具体执行步骤
4. 关键节点和截止日期
5. 备选方案
6. 风险控制措施
7. 联系方式和资源清单

请提供可操作的具体建议。
""" if language == "chinese" else f"""
Please generate a detailed house-hunting action plan based on the user's complete requirements and analysis results.

Priority Strategy: {priority}

The action plan should include:
1. Time planning (short-term, medium-term, long-term tasks)
2. Priority ranking
3. Specific execution steps
4. Key milestones and deadlines
5. Alternative plans
6. Risk control measures
7. Contact information and resource list

Please provide actionable specific recommendations.
"""
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(language, "detailed_analysis")},
            {"role": "user", "content": action_prompt}
        ]
        
        return self._call_qwen_api(messages)
    
    def get_report_metadata(self) -> Dict[str, Any]:
        """获取报告元数据"""
        return {
            "generated_at": datetime.now().isoformat(),
            "user_data_sources": {
                "questionnaire": bool(self.questionnaire_data),
                "main_agent_history": bool(self.main_agent_history),
                "inquiry_agent_history": bool(self.inquiry_agent_history),
                "property_search_results": len(self.property_search_results),
                "area_analysis_results": len(self.area_analysis_results)
            },
            "data_completeness": self._assess_data_completeness(),
            "report_quality_score": self._calculate_quality_score()
        }
    
    def _assess_data_completeness(self) -> Dict[str, Any]:
        """评估数据完整性"""
        completeness = {
            "basic_requirements": 0,
            "budget_info": 0,
            "preferences": 0,
            "search_results": 0,
            "total_score": 0
        }
        
        # 基本需求完整性
        if self.questionnaire_data:
            basic_fields = ['budget_min', 'budget_max', 'room_type']
            filled_fields = sum(1 for field in basic_fields if self.questionnaire_data.get(field))
            completeness["basic_requirements"] = filled_fields / len(basic_fields)
        
        # 预算信息完整性
        if self.questionnaire_data:
            budget_fields = ['includes_bills', 'includes_furniture', 'total_budget']
            filled_fields = sum(1 for field in budget_fields if self.questionnaire_data.get(field))
            completeness["budget_info"] = filled_fields / len(budget_fields)
        
        # 偏好信息完整性
        preferences = self._extract_user_preferences()
        preference_score = 0
        if preferences["budget_range"]: preference_score += 0.3
        if preferences["preferred_areas"]: preference_score += 0.3
        if preferences["room_types"]: preference_score += 0.2
        if preferences["special_requirements"]: preference_score += 0.2
        completeness["preferences"] = preference_score
        
        # 搜索结果完整性
        if self.property_search_results:
            completeness["search_results"] = min(len(self.property_search_results) / 3, 1.0)
        
        # 总体得分
        completeness["total_score"] = sum([
            completeness["basic_requirements"] * 0.3,
            completeness["budget_info"] * 0.2,
            completeness["preferences"] * 0.3,
            completeness["search_results"] * 0.2
        ])
        
        return completeness
    
    def _calculate_quality_score(self) -> float:
        """计算报告质量得分"""
        data_completeness = self._assess_data_completeness()
        
        # 基础得分来自数据完整性
        base_score = data_completeness["total_score"] * 70
        
        # 加分项
        bonus_score = 0
        
        # 有区域分析结果
        if self.area_analysis_results:
            bonus_score += 10
        
        # 有多轮对话历史
        if self.main_agent_history and len(self.main_agent_history) >= 4:
            bonus_score += 10
        
        # 有详细的需求分析
        if self.inquiry_agent_history and len(self.inquiry_agent_history) >= 2:
            bonus_score += 10
        
        return min(base_score + bonus_score, 100)
    
    def reset_data(self):
        """重置所有数据"""
        self.user_data = {}
        self.questionnaire_data = None
        self.main_agent_history = None
        self.inquiry_agent_history = None
        self.property_search_results = []
        self.area_analysis_results = {}
        self.user_preferences = {}

def create_report_agent() -> ReportAgent:
    """创建报告生成Agent实例"""
    return ReportAgent()

# 使用示例和测试
if __name__ == "__main__":
    # 创建Agent
    agent = create_report_agent()
    
    # 模拟测试数据
    test_questionnaire = {
        'budget_min': 500,
        'budget_max': 800,
        'includes_bills': '不包含',
        'includes_furniture': '包含',
        'total_budget': 1200,
        'room_type': '2 Bedroom',
        'consider_sharing': '愿意考虑',
        'commute_time': '30分钟以内',
        'move_in_date': '2024-03-01',
        'lease_duration': '12个月'
    }
    
    test_history = [
        ("user", "我想在UNSW附近找一个两室一厅的房子，预算600-800澳元每周"),
        ("assistant", "我为您分析了UNSW附近的房源情况，推荐Kingsford和Randwick地区"),
        ("user", "Kingsford地区的房源怎么样？"),
        ("assistant", "Kingsford地区很受学生欢迎，交通便利，平均价格650澳元/周")
    ]
    
    test_properties = [
        {
            "addressLine1": "123 Anzac Parade",
            "addressLine2": "Kingsford",
            "bedroomCount": 2,
            "bathroomCount": 1,
            "pricePerWeek": 650,
            "suburb": "kingsford"
        },
        {
            "addressLine1": "456 High Street", 
            "addressLine2": "Randwick",
            "bedroomCount": 2,
            "bathroomCount": 2,
            "pricePerWeek": 720,
            "suburb": "randwick"
        }
    ]
    
    # 更新Agent数据
    agent.update_user_data(
        questionnaire_data=test_questionnaire,
        main_agent_history=test_history,
        property_search_results=[{"result": {"properties": test_properties}}]
    )
    
    print("? 租房报告生成Agent测试")
    print("=" * 60)
    
    try:
        # 测试执行摘要
        print("\n? 生成执行摘要:")
        print("-" * 40)
        summary = agent.generate_executive_summary()
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        
        # 测试报告元数据
        print("\n? 报告元数据:")
        print("-" * 40)
        metadata = agent.get_report_metadata()
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        
        print("\n? 测试完成！")
        
    except Exception as e:
        print(f"? 测试失败: {e}") 