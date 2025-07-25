# -*- coding: utf-8 -*-
"""
信息追问Agent - LLM驱动版本
用于分析租房用户需求的合理性，提供建议，并主动追问关键信息
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

API_KEY = os.getenv("API_KEY_POINT")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
QWEN_MODEL = "qwen-vl-max-latest"

# 汇率配置（参考值）#修改成实时汇率,引入API
EXCHANGE_RATES = {
    'CNY_TO_AUD': 0.21,  # 1 CNY = 0.21 AUD
    'AUD_TO_CNY': 4.76,  # 1 AUD = 4.76 CNY
    'USD_TO_AUD': 1.55,  # 1 USD = 1.55 AUD
    'AUD_TO_USD': 0.65   # 1 AUD = 0.65 USD
}

# 标准费用和专业知识库
RENTAL_KNOWLEDGE_BASE = {
    "汇率": EXCHANGE_RATES,
    "标准费用": {
        "bills_per_week": 30,          # 水电网费用(AUD/周)
        "furniture_1b": 30,            # 1B家具分摊成本(AUD/周)
        "furniture_2b": 15,            # 2B家具分摊成本(AUD/周)  
        "furniture_3b": 10,            # 3B家具分摊成本(AUD/周)
        "min_living_cost_monthly": 1200  # 最低生活费(AUD/月，除房租外)
    },
    "预算级别指导": {
        "premium": {"range": "≥800 AUD/周", "description": "预算充足，可选择任意房型和区域，基本不受限"},
        "high": {"range": "600-799 AUD/周", "description": "可选择Studio或1B，如果愿意合租，2B性价比更高"},
        "medium": {"range": "400-599 AUD/周", "description": "推荐2B1B合租，或考虑3B2B获得更好条件"},
        "low": {"range": "<400 AUD/周", "description": "建议考虑House分租或多人合租以降低成本"}
    },
    "房型推荐规则": {
        "studio": "适合单人居住，价格相对较低",
        "1b1b": "一室一厅，适合单人或情侣",
        "2b1b": "两室一厅，适合合租，性价比高",
        "2b2b": "两室两厅，更好的生活条件",
        "3b2b": "三室两厅，适合多人合租",
        "house_share": "独立屋分租，最经济选择"
    },
    "租赁方式比较": {
        "student_apartment": {
            "min_budget": 650,
            "pros": ["管理规范", "安全性高", "设施完善", "社交机会多"],
            "cons": ["价格较高", "规则较严", "空间相对较小"],
            "suitable_for": "预算充足、追求便利的学生"
        },
        "chinese_agent": {
            "min_budget": 500,
            "pros": ["沟通方便", "服务到位", "快速入住"],
            "cons": ["可能存在溢价", "选择相对有限"],
            "suitable_for": "不愿自己找房、可接受一定溢价的用户"
        },
        "social_housing": {
            "min_budget": 0,
            "pros": ["价格透明", "选择丰富", "性价比高"],
            "cons": ["需要自己筛选", "竞争激烈", "需要注意时间节点"],
            "suitable_for": "有时间、希望性价比最高的用户"
        }
    },
    "目标区域": [
        'kingsford', 'randwick', 'kensington', 'zetland', 'waterloo',
        'eastgarden', 'mascot', 'rosebery', 'wolli-creek', 'pagewood',
        'maroubra', 'paddington', 'hillsdale', 'alexandria', 'botany'
    ],
    "关键追问要素": [
        "总预算金额和币种",
        "是否包含学费",
        "学费具体金额",
        "是否包含Bills(水电网)",
        "是否包含家具",
        "房型偏好",
        "合租意愿",
        "现有室友情况",
        "偏好区域",
        "最大通勤时间",
        "入住时间",
        "租期长度",
        "特殊设施要求"
    ]
}

class InquiryAgent:
    """基于LLM的信息追问Agent"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {}
        self.questionnaire_data = None
        self.main_agent_history = None
        self.assessment_complete = False  # 标记需求评估是否完成
        
        # 初始化需求数据结构
        self.updated_requirements = {
            "budget_min": None,
            "budget_max": None,
            "includes_bills": None,
            "includes_furniture": None,
            "total_budget": None,
            "room_type": None,
            "consider_sharing": None,
            "commute_time": None,
            "move_in_date": None,
            "lease_duration": None,
            "accept_premium": None,
            "accept_small_room": None
        }
        
    def update_context(self, questionnaire_data=None, main_agent_history=None):
        """更新上下文信息，包括问卷数据和主Agent历史"""
        if questionnaire_data is not None:
            self.questionnaire_data = questionnaire_data
            # 初始化updated_requirements为问卷数据
            for key in self.updated_requirements.keys():
                if key in questionnaire_data and questionnaire_data[key] is not None:
                    self.updated_requirements[key] = questionnaire_data[key]
        if main_agent_history is not None:
            self.main_agent_history = main_agent_history
    
    def _format_questionnaire_context(self) -> str:
        """格式化问卷数据为上下文"""
        if not self.questionnaire_data:
            return "用户尚未填写问卷。"
        
        context = "## 用户问卷信息：\n\n"
        
        # 预算信息
        budget_min = self.questionnaire_data.get('budget_min')
        budget_max = self.questionnaire_data.get('budget_max')
        includes_bills = self.questionnaire_data.get('includes_bills')
        includes_furniture = self.questionnaire_data.get('includes_furniture')
        total_budget = self.questionnaire_data.get('total_budget')
        
        if budget_min is not None or budget_max is not None:
            context += f"**预算范围：** ${budget_min or '未设置'} - ${budget_max or '未设置'}/周\n"
        if includes_bills:
            context += f"**包含Bills：** {includes_bills}\n"
        if includes_furniture:
            context += f"**包含家具：** {includes_furniture}\n"
        if total_budget:
            context += f"**总开销预期：** ${total_budget}/周\n"
        
        # 房型偏好
        room_type = self.questionnaire_data.get('room_type')
        consider_sharing = self.questionnaire_data.get('consider_sharing')
        if room_type:
            context += f"**目标房型：** {room_type}\n"
        if consider_sharing:
            context += f"**合租意愿：** {consider_sharing}\n"
        
        # 其他要求
        commute_time = self.questionnaire_data.get('commute_time')
        move_in_date = self.questionnaire_data.get('move_in_date')
        lease_duration = self.questionnaire_data.get('lease_duration')
        accept_premium = self.questionnaire_data.get('accept_premium')
        accept_small_room = self.questionnaire_data.get('accept_small_room')
        
        if commute_time:
            context += f"**通勤时间要求：** {commute_time}\n"
        if move_in_date:
            context += f"**入住日期：** {move_in_date}\n"
        if lease_duration:
            context += f"**租期：** {lease_duration}\n"
        if accept_premium:
            context += f"**接受高溢价：** {accept_premium}\n"
        if accept_small_room:
            context += f"**接受小房间：** {accept_small_room}\n"
        
        return context
    
    def _format_main_agent_history(self) -> str:
        """格式化主Agent历史为上下文"""
        if not self.main_agent_history:
            return "暂无与主AI助手的对话历史。"
        
        context = "## 与主AI助手的对话历史：\n\n"
        for i, (role, content) in enumerate(self.main_agent_history[-6:], 1):  # 只取最近3轮对话
            # 将inquiry_assistant映射为assistant，确保API兼容性
            display_role = role
            if role == "inquiry_assistant":
                display_role = "智能需求分析师"
            elif role == "user":
                display_role = "用户"
            elif role == "assistant":
                display_role = "AI助手"
                
            context += f"**{display_role}：** {content[:200]}{'...' if len(content) > 200 else ''}\n\n"
        
        return context
        
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
            if role == "inquiry_assistant":
                role = "assistant"
            
            # 只保留API支持的角色
            if role in ["system", "assistant", "user", "tool", "function"]:
                filtered_messages.append({"role": role, "content": content})
        
        try:
            completion = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=filtered_messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return completion.choices[0].message.content or ""
            
        except Exception as e:
            print(f"Error calling Qwen API: {e}")
            raise
    
    def _detect_language(self, text: str) -> str:
        """检测文本语言"""
        chinese_char_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        return "chinese" if chinese_char_count > len(text) * 0.1 else "english"
    
    def _extract_and_update_requirements(self, response_text: str) -> str:
        """从AI响应中提取JSON格式的需求更新并更新到self.updated_requirements"""
        # 使用正则表达式提取JSON部分
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                requirements_update = json.loads(json_str)
                
                # 更新requirements，只更新非null的值
                for key, value in requirements_update.items():
                    if key in self.updated_requirements and value is not None:
                        self.updated_requirements[key] = value
                
                print(f"需求更新成功: {requirements_update}")
                
                # 返回去掉JSON部分的纯文本回复
                clean_response = re.sub(json_pattern, '', response_text, flags=re.DOTALL).strip()
                return clean_response
                
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return response_text
        else:
            print("未找到JSON格式的需求更新")
            return response_text
    
    def get_updated_requirements(self) -> dict:
        """获取当前更新后的需求数据"""
        return self.updated_requirements.copy()
    
    def get_current_requirements_json(self) -> str:
        """获取当前需求数据的JSON字符串格式"""
        return json.dumps(self.updated_requirements, ensure_ascii=False, indent=2)
    
    def _create_system_prompt(self, language: str) -> str:
        """创建系统提示词"""
        knowledge_json = json.dumps(RENTAL_KNOWLEDGE_BASE, ensure_ascii=False, indent=2)
        
        # 添加问卷和历史信息到提示词中
        questionnaire_context = self._format_questionnaire_context()
        main_agent_context = self._format_main_agent_history()
        
        if language == "chinese":
            return """
你是一名专业的租房需求评估师，专门负责分析用户填写的问卷信息，评估其租房需求的合理性。

## 你的专业知识库：
{}

## 用户上下文信息：
{}

{}""".format(knowledge_json, questionnaire_context, main_agent_context) + """

## 你的核心任务：
1. **需求合理性分析**：深入分析用户的预算、房型、地区需求是否合理
2. **预算评估**：
   - 检查预算是否包含所有必要开销（Bills、家具、生活费等）
   - 评估预算与房型选择的匹配度
   - 分析预算在目标区域的可实现性
3. **关键信息识别**：识别缺失或不明确的关键信息
4. **专业建议**：提供具体的预算调整建议和房型推荐
5. **追问关键问题**：当发现不合理或缺失信息时，主动追问

## 评估标准：
- 房租应占总生活费的45%-65%
- 除房租外，生活费至少1200澳元/月
- 预算需考虑Bills（约30AUD/周）和家具成本
- 房型选择需与预算和实际需求匹配

## 回复要求：
- 使用中文回复
- 明确指出需求中的问题和不合理之处
- 提供具体的改进建议
- 当信息不足时，主动追问关键问题
- 当需求完全合理时，明确表示"评估完成，建议咨询房源信息"

## 输出格式要求：
你的回复必须包含两部分：
1. **分析建议**：正常的对话回复，分析需求合理性并提供建议
2. **JSON更新**：基于用户回复更新的需求信息，格式如下（只更新有变化的字段）：

```json
{
  "budget_min": 300,
  "budget_max": 500,
  "includes_bills": "包含",
  "includes_furniture": "不包含",
  "total_budget": 600,
  "room_type": "2 Bedroom",
  "consider_sharing": "愿意",
  "commute_time": "30分钟以内",
  "move_in_date": "2024年3月",
  "lease_duration": "12个月",
  "accept_premium": "否",
  "accept_small_room": "是"
}
```

注意：
- budget_min/budget_max/total_budget: 数值或null
- includes_bills/includes_furniture: "包含"或"不包含"或null  
- room_type: "Studio"或"1 Bedroom"或"2 Bedroom"或"3+ Bedroom"或null
- consider_sharing: "愿意"或"不愿意"或null
- accept_premium/accept_small_room: "是"或"否"或null
- 其他字段: 字符串或null

## 重要提醒：
你的职责是评估需求合理性，不要提供具体的房源推荐。当用户需求评估完成且合理时，建议用户咨询专业的房源推荐服务。
"""
        else:
            return """
You are a professional rental requirement assessor, specialized in analyzing user questionnaire information and evaluating the reasonableness of rental requirements.

## Your Professional Knowledge Base:
{}

## User Context Information:
{}

{}""".format(knowledge_json, questionnaire_context, main_agent_context) + """

## Your Core Tasks:
1. **Requirement Reasonableness Analysis**: Deeply analyze whether user's budget, room type, and area requirements are reasonable
2. **Budget Assessment**:
   - Check if budget includes all necessary expenses (Bills, furniture, living costs)
   - Evaluate budget compatibility with room type choices
   - Analyze budget feasibility in target areas
3. **Key Information Identification**: Identify missing or unclear key information
4. **Professional Advice**: Provide specific budget adjustment suggestions and room type recommendations
5. **Ask Key Questions**: Proactively inquire when unreasonable or missing information is found

## Assessment Standards:
- Rent should account for 45%-65% of total living expenses
- Living expenses should be at least 1200 AUD/month excluding rent
- Budget should consider Bills (about 30AUD/week) and furniture costs
- Room type selection should match budget and actual needs

## Response Requirements:
- Respond in user's language
- Clearly point out problems and unreasonable aspects in requirements
- Provide specific improvement suggestions
- Proactively ask key questions when information is insufficient
- When requirements are completely reasonable, clearly state "Assessment complete, recommend consulting property information"

## Output Format Requirements:
Your response must include two parts:
1. **Analysis and Advice**: Normal conversational response analyzing requirement reasonableness and providing suggestions
2. **JSON Update**: Updated requirement information based on user response, in the following format (only update changed fields):

```json
{
  "budget_min": 300,
  "budget_max": 500,
  "includes_bills": "包含",
  "includes_furniture": "不包含",
  "total_budget": 600,
  "room_type": "2 Bedroom",
  "consider_sharing": "愿意",
  "commute_time": "Within 30 minutes",
  "move_in_date": "March 2024",
  "lease_duration": "12 months",
  "accept_premium": "否",
  "accept_small_room": "是"
}
```

Note:
- budget_min/budget_max/total_budget: number or null
- includes_bills/includes_furniture: "包含" or "不包含" or null  
- room_type: "Studio" or "1 Bedroom" or "2 Bedroom" or "3+ Bedroom" or null
- consider_sharing: "愿意" or "不愿意" or null
- accept_premium/accept_small_room: "是" or "否" or null
- Other fields: string or null

## Important Reminder:
Your responsibility is to assess requirement reasonableness, do not provide specific property recommendations. When user requirements are assessed and reasonable, recommend users to consult professional property recommendation services.
"""
    
    def assess_questionnaire_requirements(self, user_input: Optional[str] = None) -> str:
        """评估问卷需求的合理性"""
        
        # 检测语言
        language = self._detect_language(user_input or "")
        if not user_input:
            language = "chinese"  # 默认中文
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self._create_system_prompt(language)}
        ]
        
        # 如果有用户输入，加入对话历史
        if user_input:
            # 添加对话历史
            for role, content in self.conversation_history:
                messages.append({"role": role, "content": content})
            
            # 添加当前用户输入
            messages.append({"role": "user", "content": user_input})
        else:
            # 首次评估，直接分析问卷
            assessment_prompt = "请基于用户填写的问卷信息，分析其租房需求的合理性，指出问题并提供改进建议。如果有关键信息缺失，请主动追问。" if language == "chinese" else "Please analyze the reasonableness of the user's rental requirements based on the questionnaire information, point out problems and provide improvement suggestions. If key information is missing, please proactively inquire."
            messages.append({"role": "user", "content": assessment_prompt})
        
        # 调用LLM
        response = self._call_qwen_api(messages)
        
        # 提取并更新需求数据，获取清理后的回复
        clean_response = self._extract_and_update_requirements(response)
        
        # 更新对话历史
        if user_input:
            self.conversation_history.append(("user", user_input))
        self.conversation_history.append(("assistant", clean_response))
        
        # 检查需求验证和评估完成状态
        is_valid, validation_message = self._validate_requirements()
        
        if is_valid and ("评估完成" in clean_response or "assessment complete" in clean_response.lower()):
            self.assessment_complete = True
            # 添加验证成功的信息到回复中
            clean_response += f"\n\n✅ **验证通过**：{validation_message}\n\n**✨ 需求评估已完成，您可以进入下一步房源推荐阶段！**"
        elif "评估完成" in clean_response or "assessment complete" in clean_response.lower():
            # 如果AI认为评估完成但验证未通过，覆盖AI的判断
            clean_response = f"**⚠️ 验证未通过**：{validation_message}\n\n请继续完善您的需求信息，确保所有关键信息完整且预算合理后，才能进入下一步。"
        
        return clean_response
    
    def provide_follow_up_analysis(self, user_response: str) -> str:
        """基于用户回复提供进一步分析"""
        
        language = self._detect_language(user_response)
        
        follow_up_prompt = """
用户已经回复了之前的评估和追问。请基于新的信息：
1. 重新评估需求合理性
2. 检查是否还有问题需要解决
3. 如果还有问题，继续追问
4. 如果所有需求都已合理，明确表示"评估完成，建议咨询房源信息"

请给出完整的分析和建议。
""" if language == "chinese" else """
The user has responded to the previous assessment and inquiries. Based on the new information, please:
1. Re-assess requirement reasonableness
2. Check if there are still problems to resolve
3. If there are still problems, continue inquiring
4. If all requirements are reasonable, clearly state "Assessment complete, recommend consulting property information"

Please provide a complete analysis and recommendations.
"""
        
        messages = [
            {"role": "system", "content": self._create_system_prompt(language)}
        ]
        
        # 添加对话历史
        for role, content in self.conversation_history:
            messages.append({"role": role, "content": content})
        
        # 添加当前回复和追加分析请求
        messages.append({"role": "user", "content": user_response})
        messages.append({"role": "user", "content": follow_up_prompt})
        
        # 调用LLM
        response = self._call_qwen_api(messages)
        
        # 提取并更新需求数据，获取清理后的回复
        clean_response = self._extract_and_update_requirements(response)
        
        # 更新对话历史
        self.conversation_history.append(("user", user_response))
        self.conversation_history.append(("assistant", clean_response))
        
        # 检查需求验证和评估完成状态
        is_valid, validation_message = self._validate_requirements()
        
        if is_valid and ("评估完成" in clean_response or "assessment complete" in clean_response.lower()):
            self.assessment_complete = True
            # 添加验证成功的信息到回复中
            clean_response += f"\n\n✅ **验证通过**：{validation_message}\n\n**✨ 需求评估已完成，您可以进入下一步房源推荐阶段！**"
        elif "评估完成" in clean_response or "assessment complete" in clean_response.lower():
            # 如果AI认为评估完成但验证未通过，覆盖AI的判断
            clean_response = f"**⚠️ 验证未通过**：{validation_message}\n\n请继续完善您的需求信息，确保所有关键信息完整且预算合理后，才能进入下一步。"
        
        return clean_response
    
    def _check_completeness(self) -> tuple[bool, list[str]]:
        """检查所有关键信息是否完整"""
        missing_fields = []
        required_fields = {
            "budget_min": "最低预算",
            "budget_max": "最高预算", 
            "includes_bills": "是否包含Bills",
            "includes_furniture": "是否包含家具",
            "total_budget": "总生活预算",
            "room_type": "房型偏好",
            "consider_sharing": "合租意愿",
            "commute_time": "通勤时间要求",
            "move_in_date": "入住日期",
            "lease_duration": "租期长度"
        }
        
        for field, description in required_fields.items():
            if self.updated_requirements.get(field) is None:
                missing_fields.append(description)
        
        return len(missing_fields) == 0, missing_fields
    
    def _check_budget_feasibility(self) -> tuple[bool, str]:
        """检查预算合理性"""
        try:
            # 获取必要的预算信息
            budget_min = self.updated_requirements.get("budget_min")
            budget_max = self.updated_requirements.get("budget_max") 
            total_budget = self.updated_requirements.get("total_budget")
            includes_bills = self.updated_requirements.get("includes_bills")
            includes_furniture = self.updated_requirements.get("includes_furniture")
            room_type = self.updated_requirements.get("room_type")
            
            # 确保所有必要信息都存在且为有效值
            if (budget_min is None or budget_max is None or total_budget is None or 
                includes_bills is None or includes_furniture is None or room_type is None):
                return False, "预算信息不完整，无法进行合理性检查"
            
            # 计算每周必要开支
            weekly_expenses = 0
            
            # 1. 房租（取预算范围的平均值）
            avg_rent = (float(budget_min) + float(budget_max)) / 2
            weekly_expenses += avg_rent
            
            # 2. Bills费用（如果不包含）
            if includes_bills == "不包含":
                bills_cost = RENTAL_KNOWLEDGE_BASE["标准费用"]["bills_per_week"]
                weekly_expenses += bills_cost
            
            # 3. 家具费用（如果不包含）
            if includes_furniture == "不包含":
                if room_type == "1 Bedroom" or room_type == "Studio":
                    furniture_cost = RENTAL_KNOWLEDGE_BASE["标准费用"]["furniture_1b"]
                elif room_type == "2 Bedroom":
                    furniture_cost = RENTAL_KNOWLEDGE_BASE["标准费用"]["furniture_2b"] 
                elif room_type == "3+ Bedroom":
                    furniture_cost = RENTAL_KNOWLEDGE_BASE["标准费用"]["furniture_3b"]
                else:
                    furniture_cost = 20  # 默认值
                weekly_expenses += furniture_cost
            
            # 4. 基本生活费（除房租外）
            min_living_cost_weekly = RENTAL_KNOWLEDGE_BASE["标准费用"]["min_living_cost_monthly"] / 4.33  # 约277 AUD/周
            weekly_expenses += min_living_cost_weekly
            
            # 检查总预算是否足够
            total_budget_float = float(total_budget)
            budget_sufficient = total_budget_float >= weekly_expenses
            
            if budget_sufficient:
                surplus = total_budget_float - weekly_expenses
                return True, f"预算合理。每周开支约{weekly_expenses:.0f}澳元，剩余{surplus:.0f}澳元用于其他支出。"
            else:
                deficit = weekly_expenses - total_budget_float
                return False, f"预算不足。每周最低开支需要{weekly_expenses:.0f}澳元，但总预算只有{total_budget}澳元，缺口{deficit:.0f}澳元。建议调整预算或降低房租期望。"
                
        except Exception as e:
            return False, f"预算计算出错：{e}"
    
    def _validate_requirements(self) -> tuple[bool, str]:
        """验证需求完整性和合理性"""
        # 检查完整性
        is_complete, missing_fields = self._check_completeness()
        if not is_complete:
            missing_str = "、".join(missing_fields)
            return False, f"关键信息不完整，还需要确认：{missing_str}"
        
        # 检查预算合理性
        is_feasible, budget_message = self._check_budget_feasibility()
        if not is_feasible:
            return False, budget_message
        
        return True, budget_message

    def is_assessment_complete(self) -> bool:
        """检查需求评估是否完成"""
        return self.assessment_complete
    
    def get_validation_status(self) -> Dict[str, Any]:
        """获取当前需求验证状态"""
        is_complete, missing_fields = self._check_completeness()
        is_feasible, budget_message = self._check_budget_feasibility()
        is_valid, validation_message = self._validate_requirements()
        
        return {
            "is_complete": is_complete,
            "missing_fields": missing_fields,
            "is_budget_feasible": is_feasible,
            "budget_message": budget_message,
            "is_valid": is_valid,
            "validation_message": validation_message,
            "can_proceed": is_valid and self.assessment_complete
        }
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = []
        self.user_profile = {}
        self.questionnaire_data = None
        self.main_agent_history = None
        self.assessment_complete = False
        
        # 重置需求数据
        self.updated_requirements = {
            "budget_min": None,
            "budget_max": None,
            "includes_bills": None,
            "includes_furniture": None,
            "total_budget": None,
            "room_type": None,
            "consider_sharing": None,
            "commute_time": None,
            "move_in_date": None,
            "lease_duration": None,
            "accept_premium": None,
            "accept_small_room": None
        }
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """获取对话摘要"""
        if not self.conversation_history:
            return {"status": "empty", "summary": "暂无对话记录"}
        
        summary = {
            "status": "completed" if self.assessment_complete else "in_progress",
            "total_exchanges": len(self.conversation_history) // 2,
            "assessment_complete": self.assessment_complete,
            "key_issues_identified": [],
            "recommendations_given": []
        }
        
        # 简单分析对话内容，提取关键信息
        for role, content in self.conversation_history:
            if role == "assistant":
                if "问题" in content or "不合理" in content or "建议" in content:
                    summary["key_issues_identified"].append(content[:100] + "...")
                if "推荐" in content or "建议" in content:
                    summary["recommendations_given"].append(content[:100] + "...")
        
        return summary

def create_inquiry_agent() -> InquiryAgent:
    """创建信息追问Agent实例"""
    return InquiryAgent()

# 使用示例和测试
if __name__ == "__main__":
    # 创建Agent
    agent = create_inquiry_agent()
    
    # 测试用例
    print("🚀 信息追问Agent - 需求评估版本测试")
    print("=" * 60)
    
    # 模拟问卷数据
    test_questionnaire = {
        'budget_min': 300,
        'budget_max': 400,
        'includes_bills': '不包含',
        'includes_furniture': '不包含',
        'total_budget': 500,
        'room_type': '1 Bedroom',
        'consider_sharing': '不愿意',
        'commute_time': '30分钟以内'
    }
    
    agent.update_context(questionnaire_data=test_questionnaire)
    
    try:
        # 首次评估
        print("\n🧪 首次需求评估:")
        print("-" * 40)
        response = agent.assess_questionnaire_requirements()
        print(response)
        
        # 模拟用户回复
        user_response = "我的预算确实有限，但我不想合租，有什么建议吗？"
        print(f"\n用户回复: {user_response}")
        print("\n🧪 追问分析:")
        print("-" * 40)
        response = agent.provide_follow_up_analysis(user_response)
        print(response)
        
        # 显示更新后的需求数据
        print(f"\n📊 更新后的需求数据:")
        print("-" * 40)
        updated_requirements = agent.get_updated_requirements()
        print(json.dumps(updated_requirements, ensure_ascii=False, indent=2))
        
        # 检查评估状态
        print(f"\n评估完成状态: {agent.is_assessment_complete()}")
        
        # 获取对话摘要
        summary = agent.get_conversation_summary()
        print(f"\n对话摘要: {summary}")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}") 